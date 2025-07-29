import requests, json, zlib
import numpy as np
import msgpack
from .libvx import LibVectorX as Vxlib
from .crypto import get_checksum, json_zip, json_unzip
from .exceptions import raise_exception

class Index:
    def __init__(self, name:str, key:str, token:str, url:str, version:int=1, params=None):
        self.name = name
        self.key = key
        self.token = token
        self.url = url
        self.version = version
        self.checksum = get_checksum(self.key)
        self.lib_token = params["lib_token"]
        self.count = params["total_elements"]
        self.space_type = params["space_type"]
        self.dimension = params["dimension"]
        self.precision = "float16" if params["use_fp16"] else "float32"
        self.M = params["M"]

        if key:
            self.vxlib = Vxlib(key=key, lib_token=self.lib_token, space_type=self.space_type, version=version, dimension=self.dimension)
        else:
            self.vxlib = None

    def __str__(self):
        return self.name
    
    def _normalize_vector(self, vector):
        # Normalize only if using cosine distance
        if self.space_type != "cosine":
            return vector, 1.0
        vector = np.array(vector, dtype=np.float32)
        # Check dimension of the vector
        if vector.ndim != 1 or vector.shape[0] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {vector.shape[0]}")
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector, 1.0
        normalized_vector = vector / norm
        return normalized_vector, float(norm)

    def upsert(self, input_array):
        if len(input_array) > 1000:
            raise ValueError("Cannot insert more than 1000 vectors at a time")
        
        # Process all vectors into a list of arrays (not dictionaries)
        vector_batch = []
        
        for item in input_array:
            # Normalize vector and set norm
            vector, norm = self._normalize_vector(item['vector'])
            
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
            
            # Add to batch
            vector_batch.append(vector_obj)
        
        # Serialize batch using msgpack
        serialized_data = msgpack.packb(vector_batch, use_bin_type=True, use_single_float=True)
        
        # Send request
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/msgpack'
        }
        
        response = requests.post(
            f'{self.url}/index/{self.name}/vector/insert', 
            headers=headers, 
            data=serialized_data
        )

        if response.status_code != 200:
            raise_exception(response.status_code, response.text)
        return "Vectors inserted successfully"
    
    def query(self, vector, top_k=10, filter=None, ef=128, include_vectors=False, log=False):
        if top_k > 100:
            raise ValueError("top_k cannot be greater than 100")

        # Normalize query vector if using cosine distance
        norm = 1.0
        if self.space_type == "cosine":
            vector, norm = self._normalize_vector(vector)

        original_vector = vector
        if self.vxlib:
            vector = self.vxlib.encrypt_vector(vector)
            top_k += 5  # Add some extra results for over-fetching and re-scoring
            
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'vector': vector.tolist() if isinstance(vector, np.ndarray) else list(vector),
            'k': top_k,
            'ef': ef,
            'include_vectors': include_vectors
        }
        
        if filter:
            data['filter'] = json.dumps(filter)
                
        response = requests.post(f'{self.url}/index/{self.name}/search', headers=headers, json=data)
        
        if response.status_code != 200:
            raise_exception(response.status_code, response.text)

        # Parse msgpack response - server returns an array of VectorResult objects as arrays
        # Order: [distance, id, meta, filter, norm, vector]
        results = msgpack.unpackb(response.content, raw=False)
        
        # Convert to a more Pythonic list of dictionaries
        vectors = []
        processed_results = []
        
        for result in results:
            # Access each field by its index position
            distance = result[0]  # distance
            vector_id = result[1]  # id
            meta_data = result[2]  # meta
            filter_str = result[3]  # filter
            norm_value = result[4]  # norm
            vector_data = result[5] if len(result) > 5 else []  # vector (if present)
            
            processed_result = {
                'id': vector_id,
                'distance': distance,
                'similarity': 1 - distance,
                'meta': json_unzip(self.vxlib.decrypt_meta(meta_data)) if self.vxlib else json_unzip(meta_data),
                'norm': norm_value
            }
            
            # Filter will come as a string by default
            if filter_str:
                processed_result['filter'] = json.loads(filter_str)

            # Include vector if requested and available
            if (include_vectors or self.vxlib) and vector_data:
                processed_result['vector'] = list(self.vxlib.decrypt_vector(vector_data)) if self.vxlib else list(vector_data)
                vectors.append(np.array(processed_result['vector'], dtype=np.float32))

            processed_results.append(processed_result)
        
        # If using encryption, rescore the results
        if self.vxlib and vectors:
            top_k -= 5  # Adjust for the extra results we requested
            distances = self.vxlib.calculate_distances(query_vector=original_vector, vectors=vectors)
            # Set distance and similarity in processed results
            for i, result in enumerate(processed_results):
                if i < len(distances):  # Ensure we don't go out of bounds
                    result['distance'] = distances[i]
                    result['similarity'] = 1 - distances[i]
            # Now sort processed results by distance
            processed_results = sorted(processed_results, key=lambda x: x['distance'])
            # Return only top_k results
            processed_results = processed_results[:top_k]
            
        # If include_vectors is False then remove the vectors from the result
        if not include_vectors:
            for result in processed_results:
                result.pop('vector', None)

        return processed_results
    
    def delete_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.delete(f'{self.url}/index/{self.name}/vector/{id}/delete', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        return response.text + " rows deleted"
    
    # Delete multiple vectors based on a filter
    def delete_with_filter(self, filter):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {"filter": filter}
        print(filter)
        response = requests.delete(f'{self.url}/index/{self.name}/vectors/delete', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return response.text
    
    # Get a single vector by id
    def get_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        
        # Use POST method with the ID in the request body
        response = requests.post(
            f'{self.url}/index/{self.name}/vector/get',
            headers=headers,
            json={'id': id}
        )
        
        if response.status_code != 200:
            raise_exception(response.status_code)
        
        # Parse the msgpack response
        vector_obj = msgpack.unpackb(response.content, raw=False)
        
        response = {
            'id': vector_obj[0],
            'meta': json_unzip(self.vxlib.decrypt_meta(vector_obj[1])) if self.vxlib else json_unzip(vector_obj[1]),
            'filter': vector_obj[2],
            'norm': vector_obj[3],
            'vector': list(self.vxlib.decrypt_vector(vector_obj[4])) if self.vxlib else list(vector_obj[4])
        }
        
        return response

    def describe(self):
        data = {
            "name": self.name,
            "space_type": self.space_type,
            "dimension": self.dimension,
            "count": self.count,
            "precision": self.precision,
            "M": self.M,
        }
        return data