import requests
import json
import numpy as np
import msgpack
import time
from typing import Dict, List, Union, Tuple, Any, Optional
from .libvx import LibVectorX as Vxlib
from .crypto import get_checksum, json_zip, json_unzip
from .exceptions import raise_exception, VectorXError

class HybridIndex:
    """
    HybridIndex combines dense and sparse vector search capabilities.
    It maintains references to both a dense and sparse index for hybrid search operations.
    """
    def __init__(self, name: str, key: str, token: str, url: str, 
                 dense_name: str, sparse_name: str, 
                 dense_params: Dict[str, Any], sparse_params: Dict[str, Any],
                 version: int = 1):
        self.name = name
        self.key = key
        self.token = token
        self.url = url
        self.version = version
        self.checksum = get_checksum(self.key)
        
        # Store names for underlying indices
        self.dense_name = dense_name
        self.sparse_name = sparse_name
        
        # Store parameters for the dense index
        self.dense_lib_token = dense_params["lib_token"]
        self.dense_count = dense_params["total_elements"]
        self.dense_space_type = dense_params["space_type"]
        self.dense_dimension = dense_params["dimension"]
        self.dense_precision = "float16" if dense_params["use_fp16"] else "float32"
        self.dense_M = dense_params["M"]
        
        # Store parameters for the sparse index
        self.sparse_vocab_size = sparse_params.get("vocab_size", 30522)
        self.sparse_count = sparse_params.get("total_elements", 0)
        
        # Initialize the vector library for encryption if a key is provided
        if key:
            self.vxlib = Vxlib(key=key, lib_token=self.dense_lib_token, 
                              space_type=self.dense_space_type, 
                              version=version, 
                              dimension=self.dense_dimension)
        else:
            self.vxlib = None

    def __str__(self):
        return f"HybridIndex({self.name})"
    
    def _normalize_dense_vector(self, vector):
        """Normalize dense vector if using cosine distance"""
        if self.dense_space_type != "cosine":
            return vector, 1.0
            
        vector = np.array(vector, dtype=np.float32)
        # Check dimension of the vector
        if vector.ndim != 1 or vector.shape[0] != self.dense_dimension:
            raise ValueError(f"Dense vector dimension mismatch: expected {self.dense_dimension}, got {vector.shape[0]}")
            
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector, 1.0
            
        normalized_vector = vector / norm
        return normalized_vector, float(norm)

    def _validate_sparse_vector(self, vector_data):
        """Validate sparse vector format"""
        if not isinstance(vector_data, list):
            raise ValueError("Sparse vector must be a list of {index, value} objects")
            
        # Check that all items have index and value
        for item in vector_data:
            if not isinstance(item, dict) or 'index' not in item or 'value' not in item:
                raise ValueError("Each sparse vector item must be a dict with 'index' and 'value' keys")
                
            # Validate index is within vocab size
            if item['index'] >= self.sparse_vocab_size:
                raise ValueError(f"Sparse vector index {item['index']} exceeds vocab_size {self.sparse_vocab_size}")
                
        return True

    def _prepare_dense_vector_for_insert(self, item):
        """Prepare a dense vector for insertion"""
        if 'vector' not in item or not item['vector']:
            raise ValueError("Dense vector data is missing")
            
        # Normalize vector and set norm
        vector, norm = self._normalize_dense_vector(item['vector'])
        
        # Encrypt vector and meta if needed
        meta_data = json_zip(dict=item.get('meta', {}))
        if self.vxlib:
            vector = self.vxlib.encrypt_vector(vector)
            meta_data = self.vxlib.encrypt_meta(meta_data)
        
        # Convert numpy array to list for serialization
        vector_list = vector.tolist() if isinstance(vector, np.ndarray) else list(vector)
        
        # Create vector object as an array in the expected order:
        # [id, meta, filter, norm, vector]
        vector_obj = [
            str(item.get('id', '')),                # id
            meta_data,                              # meta
            json.dumps(item.get('filter', {})),     # filter
            float(norm),                            # norm
            vector_list                             # vector
        ]
        
        return vector_obj

    def _prepare_sparse_vector_for_insert(self, item):
        """Prepare a sparse vector for insertion in flat format"""
        if 'sparse_vector' not in item or not item['sparse_vector']:
            raise ValueError("Sparse vector data is missing")
            
        # Validate sparse vector format
        self._validate_sparse_vector(item['sparse_vector'])
        
        # Create meta as JSON string
        meta_str = json.dumps(item.get('meta', {}))
        
        # For sparse vectors, we need to convert from [{index: X, value: Y}, ...] format
        # to flat arrays of indices and values
        indices = []
        values = []
        
        for element in sorted(item['sparse_vector'], key=lambda x: x['index']):
            indices.append(int(element['index']))
            values.append(float(element['value']))
        
        # Calculate the norm
        norm = 0.0
        for val in values:
            norm += val * val
        norm = float(np.sqrt(norm))
        
        # Create sparse vector object with the flat format expected by the API
        sparse_vector = {
            "id": str(item.get('id', '')),
            "meta": meta_str,
            "norm": norm,
            "indices": indices,
            "values": values
        }
        
        return sparse_vector

    def upsert(self, items):
        """
        Insert or update hybrid vectors (both dense and sparse components).
        
        Args:
            items: List of dictionaries containing:
                - id: Unique identifier
                - vector: Dense vector component
                - sparse_vector: Sparse vector component as list of {index, value} objects
                - meta: Optional metadata
                - filter: Optional filter data
                
        Returns:
            Success message
        """
        if not items:
            raise ValueError("No items provided for insertion")
            
        if len(items) > 1000:
            raise ValueError("Cannot insert more than 1000 vectors at a time")
        
        # Check that each item has both dense and sparse vectors or handle appropriately
        dense_batch = []
        sparse_batch = []
        
        for item in items:
            if 'id' not in item:
                raise ValueError("Each item must contain an 'id' field")
                
            # Process dense vector if provided
            if 'vector' in item and item['vector']:
                dense_obj = self._prepare_dense_vector_for_insert(item)
                dense_batch.append(dense_obj)
                
            # Process sparse vector if provided
            if 'sparse_vector' in item and item['sparse_vector']:
                sparse_obj = self._prepare_sparse_vector_for_insert(item)
                sparse_batch.append(sparse_obj)
                
            # Ensure at least one vector type is provided
            if ('vector' not in item or not item['vector']) and ('sparse_vector' not in item or not item['sparse_vector']):
                raise ValueError(f"Item with ID {item.get('id', 'unknown')} must contain either 'vector' or 'sparse_vector'")
        
        # Insert dense vectors if any
        dense_result = None
        if dense_batch:
            dense_result = self._insert_dense_vectors(dense_batch)
            
        # Insert sparse vectors if any
        sparse_result = None
        if sparse_batch:
            sparse_result = self._insert_sparse_vectors(sparse_batch)
            
        # Return results
        results = {
            "message": "Hybrid vectors inserted successfully",
            "dense_result": dense_result,
            "sparse_result": sparse_result
        }
        
        return results

    def _insert_dense_vectors(self, dense_batch):
        """Insert dense vectors to the dense index"""
        # Serialize batch using msgpack
        serialized_data = msgpack.packb(dense_batch, use_bin_type=True, use_single_float=True)
        
        # Send request
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/msgpack'
        }
        
        try:
            response = requests.post(
                f'{self.url}/index/{self.dense_name}/vector/insert', 
                headers=headers, 
                data=serialized_data
            )

            if response.status_code != 200:
                raise_exception(response.status_code, response.text)
                
            return "Dense vectors inserted successfully"
            
        except Exception as e:
            error_msg = f"Failed to insert dense vectors: {str(e)}"
            raise VectorXError(error_msg) from e

    def _insert_sparse_vectors(self, sparse_batch):
        """Insert sparse vectors to the sparse index"""
        # Serialize batch using msgpack
        try:
            payload_msgpack = msgpack.packb(sparse_batch, use_bin_type=True)
            
            # Send request
            headers = {
                'Authorization': self.token,
                'Content-Type': 'application/msgpack'
            }
            
            response = requests.post(
                f'{self.url}/sparse/{self.sparse_name}/add_flat', 
                headers=headers, 
                data=payload_msgpack
            )

            if response.status_code != 200:
                raise_exception(response.status_code, response.text)
                
            return "Sparse vectors inserted successfully"
            
        except Exception as e:
            error_msg = f"Failed to insert sparse vectors: {str(e)}"
            raise VectorXError(error_msg) from e

    def hybrid_search(self, dense_vector=None, sparse_vector=None, 
                      dense_top_k=10, sparse_top_k=10, final_top_k=10, 
                      k_rrf=1.0, include_vectors=False, filter=None, ef=128):
        """
        Perform hybrid search using both dense and sparse vectors.
        
        Args:
            dense_vector: Dense vector for search
            sparse_vector: Sparse vector as list of {index, value} objects
            dense_top_k: Number of results to retrieve from dense search
            sparse_top_k: Number of results to retrieve from sparse search
            final_top_k: Number of final results after fusion
            k_rrf: RRF constant for ranking fusion
            include_vectors: Whether to include vectors in results
            filter: Optional filter criteria (will be applied to dense search)
            ef: Search-time EF parameter for dense search
            
        Returns:
            List of search results
        """
        if dense_vector is None and sparse_vector is None:
            raise ValueError("At least one of dense_vector or sparse_vector must be provided")
            
        # Validate the search parameters
        if dense_top_k > 100:
            raise ValueError("dense_top_k cannot be greater than 100")
        if sparse_top_k > 100:
            raise ValueError("sparse_top_k cannot be greater than 100")
        if final_top_k > 100:
            raise ValueError("final_top_k cannot be greater than 100")
            
        # Process dense vector if provided
        has_dense_vector = dense_vector is not None and len(dense_vector) > 0
        if has_dense_vector:
            # Normalize query vector if using cosine distance
            norm = 1.0
            if self.dense_space_type == "cosine":
                dense_vector, norm = self._normalize_dense_vector(dense_vector)

            # Encrypt if using encryption
            original_vector = dense_vector
            if self.vxlib:
                dense_vector = self.vxlib.encrypt_vector(dense_vector)
        
        # Process sparse vector if provided
        has_sparse_vector = sparse_vector is not None and len(sparse_vector) > 0
        if has_sparse_vector:
            self._validate_sparse_vector(sparse_vector)
            # Sort by index for better readability and consistency
            sparse_vector.sort(key=lambda x: x["index"])
        
        # Create payload for hybrid search
        payload = {
            "dense_index": self.dense_name,
            "sparse_index": self.sparse_name,
            "final_top_k": final_top_k,
            "include_vectors": include_vectors,
            "k_rrf": k_rrf
        }
        
        # Add dense search parameters if dense vector is provided
        if has_dense_vector:
            payload["dense_vector"] = dense_vector.tolist() if isinstance(dense_vector, np.ndarray) else list(dense_vector)
            payload["dense_top_k"] = dense_top_k
            
        # Add sparse search parameters if sparse vector is provided
        if has_sparse_vector:
            payload["sparse_vector"] = sparse_vector
            payload["sparse_top_k"] = sparse_top_k
            
        # Add filter if provided
        if filter:
            payload["filter"] = json.dumps(filter)
            
        # Send request
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(
                f'{self.url}/hybrid/search', 
                headers=headers, 
                json=payload
            )

            if response.status_code != 200:
                raise_exception(response.status_code, response.text)
                
            # Parse response and format results
            results = response.json().get("results", [])
            
            # Process results (decrypt if necessary)
            processed_results = []
            for result in results:
                processed_result = {
                    'id': result.get('id'),
                    'rrf_score': result.get('rrf_score'),
                    'dense_rank': result.get('dense_rank'),
                    'sparse_rank': result.get('sparse_rank')
                }
                
                # Process meta data if present
                meta = result.get('meta')
                if meta:
                    processed_result['meta'] = self._process_metadata(meta)
                
                # Include vector if requested and available
                if include_vectors:
                    if 'vector' in result and result['vector']:
                        vector_data = result['vector']
                        processed_result['vector'] = list(self.vxlib.decrypt_vector(vector_data)) if self.vxlib else vector_data
                
                processed_results.append(processed_result)
                
            return processed_results
            
        except Exception as e:
            error_msg = f"Failed to perform hybrid search: {str(e)}"
            raise VectorXError(error_msg) from e

    def delete_vector(self, id):
        """
        Delete a vector from both dense and sparse indices.
        
        Args:
            id: Vector ID to delete
            
        Returns:
            Dict with deletion results
        """
        results = {
            "dense_delete": None,
            "sparse_delete": None,
            "message": f"Attempted to delete vector {id} from hybrid index {self.name}"
        }
        
        # Delete from dense index
        try:
            headers = {
                'Authorization': self.token,
            }
            response = requests.delete(
                f'{self.url}/index/{self.dense_name}/vector/{id}/delete', 
                headers=headers
            )
            if response.status_code == 200:
                results["dense_delete"] = f"Vector {id} deleted from dense index"
            else:
                results["dense_delete"] = f"Failed to delete from dense index: {response.text}"
        except Exception as e:
            results["dense_delete"] = f"Error deleting from dense index: {str(e)}"
            
        # Delete from sparse index
        try:
            headers = {
                'Authorization': self.token,
            }
            response = requests.delete(
                f'{self.url}/sparse/{self.sparse_name}/vectors/{id}', 
                headers=headers
            )
            if response.status_code == 200:
                results["sparse_delete"] = f"Vector {id} deleted from sparse index"
            else:
                results["sparse_delete"] = f"Failed to delete from sparse index: {response.text}"
        except Exception as e:
            results["sparse_delete"] = f"Error deleting from sparse index: {str(e)}"
            
        return results
        
    def delete_with_filter(self, filter):
        """
        Delete vectors matching filter from both dense and sparse indices.
        
        Args:
            filter: Filter criteria
            
        Returns:
            Dict with deletion results
        """
        results = {
            "dense_delete": None,
            "sparse_delete": None,
            "message": f"Attempted to delete vectors with filter from hybrid index {self.name}"
        }
        
        # Convert filter to appropriate format
        filter_json = json.dumps(filter) if isinstance(filter, dict) else filter
        
        # Delete from dense index
        try:
            headers = {
                'Authorization': self.token,
                'Content-Type': 'application/json'
            }
            data = {"filter": filter}
            response = requests.delete(
                f'{self.url}/index/{self.dense_name}/vectors/delete', 
                headers=headers, 
                json=data
            )
            if response.status_code == 200:
                results["dense_delete"] = f"Vectors deleted from dense index: {response.text}"
            else:
                results["dense_delete"] = f"Failed to delete from dense index: {response.text}"
        except Exception as e:
            results["dense_delete"] = f"Error deleting from dense index: {str(e)}"
            
        # Note: The current API doesn't seem to support delete by filter for sparse vectors
        # This is a placeholder for when that functionality becomes available
        results["sparse_delete"] = "Delete by filter not supported for sparse index"
            
        return results

    def describe(self):
        """
        Get information about the hybrid index.
        
        Returns:
            Dict with hybrid index information
        """
        return {
            "name": self.name,
            "dense_index": self.dense_name,
            "sparse_index": self.sparse_name,
            "dense_params": {
                "space_type": self.dense_space_type,
                "dimension": self.dense_dimension,
                "count": self.dense_count,
                "precision": self.dense_precision,
                "M": self.dense_M,
            },
            "sparse_params": {
                "vocab_size": self.sparse_vocab_size,
                "count": self.sparse_count
            }
        }

    def _process_metadata(self, meta_str):
        """Process metadata string to handle various formats and encoding issues"""
        if not meta_str:
            return {}
            
        # If it's already a dictionary, return as is
        if isinstance(meta_str, dict):
            return meta_str
            
        # If encryption is enabled, decrypt first
        if self.vxlib:
            try:
                meta_str = self.vxlib.decrypt_meta(meta_str)
            except:
                # If decryption fails, continue with the original string
                pass
                
        # Try to parse as JSON
        try:
            return json.loads(meta_str)
        except json.JSONDecodeError:
            # Try different encoding/decoding approaches
            try:
                # Method 1: Try to decode as UTF-8 and then parse as JSON
                decoded = meta_str.encode('latin1').decode('utf-8')
                return json.loads(decoded)
            except:
                pass
                
            try:
                # Method 2: Try to encode as bytes and decode with utf-8 errors ignored
                if isinstance(meta_str, str):
                    decoded = meta_str.encode('latin1').decode('utf-8', errors='ignore')
                    return json.loads(decoded)
            except:
                pass
                
            try:
                # Method 3: Try to treat as base64 encoded
                import base64
                decoded = base64.b64decode(meta_str).decode('utf-8')
                return json.loads(decoded)
            except:
                pass
                
            # Method 4: If it has visible JSON characters, try to extract them
            import re
            if isinstance(meta_str, str) and ('{' in meta_str or '[' in meta_str):
                # Try to extract json-like substrings
                json_pattern = r'(\{.*\}|\[.*\])'
                matches = re.search(json_pattern, meta_str)
                if matches:
                    try:
                        return json.loads(matches.group(1))
                    except:
                        pass
                
            # If all else fails, return a cleaned string or the original
            if isinstance(meta_str, str):
                # Clean up non-printable characters
                printable = ''.join(c for c in meta_str if c.isprintable() or c in ['\n', '\t', '\r'])
                return printable if printable else meta_str
            
            return meta_str 