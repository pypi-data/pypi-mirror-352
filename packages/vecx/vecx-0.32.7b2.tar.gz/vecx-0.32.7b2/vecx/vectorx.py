import requests
import secrets
import json
from vecx.exceptions import raise_exception
from vecx.index import Index
from vecx.user import User
from vecx.crypto import get_checksum
from vecx.utils import is_valid_index_name
from functools import lru_cache
from vecx.hybrid import HybridIndex
import time

SUPPORTED_REGIONS = ["us-west", "india-west", "local"]
class VectorX:
    def __init__(self, token:str|None=None):
        self.token = token
        self.region = "local"
        self.base_url = "http://127.0.0.1:8080/api/v1"
        # Token will be of the format user:token:region
        if token:
            token_parts = self.token.split(":")
            if len(token_parts) > 2:
                self.base_url = f"https://{token_parts[2]}.vectorxdb.ai/api/v1"
                self.token = f"{token_parts[0]}:{token_parts[1]}"
        self.version = 1

    def __str__(self):
        return self.token

    def set_token(self, token:str):
        self.token = token
        self.region = self.token.split (":")[1]
    
    def set_base_url(self, base_url:str):
        self.base_url = base_url
    
    def generate_key(self)->str:
        # Generate a random hex key of length 32
        key = secrets.token_hex(16)  # 16 bytes * 2 hex chars/byte = 32 chars
        print("Store this encryption key in a secure location. Loss of the key will result in the irreversible loss of associated vector data.\nKey: ",key)
        return key

    def create_index(self, name:str, dimension:int, key:str|None, space_type:str, M:int=16, ef_con:int=128, use_fp16:bool=True, version:int=None):
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        if dimension > 10000:
            raise ValueError("Dimension cannot be greater than 10000")
        space_type = space_type.lower()
        if space_type not in ["cosine", "l2", "ip"]:
            raise ValueError(f"Invalid space type: {space_type}")
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'index_name': name,
            'dim': dimension,
            'space_type': space_type,
            'M':M,
            'ef_con': ef_con,
            'checksum': get_checksum(key),
            'use_fp16': use_fp16,
            'version': version
        }
        response = requests.post(f'{self.base_url}/index/create', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return "Index created successfully"

    def list_indexes(self):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.get(f'{self.base_url}/index/list', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        indexes = response.json()
        return indexes
    
    # TODO - Delete the index cache if the index is deleted
    def delete_index(self, name:str):
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.delete(f'{self.base_url}/index/{name}/delete', headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return f'Index {name} deleted successfully'


    # Keep in lru cache for sometime
    @lru_cache(maxsize=10)
    def get_index(self, name:str, key:str|None=None):
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        # Get index details from the server
        response = requests.get(f'{self.base_url}/index/{name}/info', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        data = response.json()
        #print(data)
        #print(data)
        # Raise error if checksum does not match
        checksum = get_checksum(key)
        if checksum != data['checksum']:
            raise_exception(460)
        idx = Index(name=name, key=key, token=self.token, url=self.base_url, version=self.version, params=data)
        return idx
    
    def get_user(self):
        return User(self.base_url, self.token)

    def create_hybrid_index(self, name:str, dimension:int, vocab_size:int=30522, key:str=None, 
                           space_type:str="cosine", M:int=16, ef_con:int=128, 
                           use_fp16:bool=True, version:int=None):
        """
        Create a hybrid index that combines dense and sparse vector search capabilities.
        
        Args:
            name: Base name for the hybrid index
            dimension: Dimensionality of the dense vectors
            vocab_size: Vocabulary size for sparse vectors (default: 30522)
            key: Encryption key (optional)
            space_type: Distance metric for dense vectors (cosine, l2, ip)
            M: Graph connectivity parameter for dense index
            ef_con: Construction-time parameter for dense index
            use_fp16: Use half-precision for storage optimization
            version: Version number (optional)
            
        Returns:
            Success message
        """
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        
        # Create names for the underlying dense and sparse indices
        dense_name = f"{name}_dense"
        sparse_name = f"{name}_sparse"
        
        # Step 1: Create dense index
        try:
            dense_result = self.create_index(
                name=dense_name,
                dimension=dimension,
                key=key,
                space_type=space_type,
                M=M,
                ef_con=ef_con,
                use_fp16=use_fp16,
                version=version
            )
            
            # Add a small delay to give the server time to process the dense index creation
            time.sleep(1.5)
            
        except Exception as e:
            raise ValueError(f"Failed to create dense index: {str(e)}")
        
        # Step 2: Create sparse index
        try:
            # Create sparse index with the given vocab_size
            headers = {
                'Authorization': self.token,
                'Content-Type': 'application/json'
            }
            sparse_data = {
                'index_name': sparse_name,
                'vocab_size': vocab_size
            }
            
            # Print request details for debugging
            print(f"Creating sparse index: {sparse_name}")
            print(f"Request URL: {self.base_url}/sparse/index/create")
            print(f"Request headers: {headers}")
            print(f"Request data: {sparse_data}")
            
            response = requests.post(f'{self.base_url}/sparse/index/create', headers=headers, json=sparse_data)
            
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code != 200 and response.status_code != 201:
                # If sparse index creation fails, try to cleanup the dense index
                try:
                    self.delete_index(dense_name)
                except:
                    pass
                raise_exception(response.status_code, response.text)
        except Exception as e:
            # If sparse index creation fails, try to cleanup the dense index
            try:
                self.delete_index(dense_name)
            except:
                pass
            raise ValueError(f"Failed to create sparse index: {str(e)}")
        
        return f"Hybrid index '{name}' created successfully with dense index '{dense_name}' and sparse index '{sparse_name}'"

    def delete_hybrid_index(self, name:str):
        """
        Delete a hybrid index (both dense and sparse components).
        
        Args:
            name: Base name of the hybrid index
            
        Returns:
            Success message
        """
        # Create names for the underlying dense and sparse indices
        dense_name = f"{name}_dense"
        sparse_name = f"{name}_sparse"
        
        results = {
            "dense_result": None,
            "sparse_result": None
        }
        
        # Step 1: Delete dense index
        try:
            dense_result = self.delete_index(dense_name)
            results["dense_result"] = dense_result
        except Exception as e:
            results["dense_result"] = f"Failed to delete dense index: {str(e)}"
        
        # Step 2: Delete sparse index
        try:
            headers = {
                'Authorization': self.token,
            }
            response = requests.delete(f'{self.base_url}/sparse/{sparse_name}/delete', headers=headers)
            if response.status_code != 200:
                results["sparse_result"] = f"Failed to delete sparse index: {response.text}"
            else:
                results["sparse_result"] = f"Sparse index '{sparse_name}' deleted successfully"
        except Exception as e:
            results["sparse_result"] = f"Failed to delete sparse index: {str(e)}"
        
        # Check if both deletions were successful
        if "Failed" in results["dense_result"] or "Failed" in results["sparse_result"]:
            return f"Partial deletion of hybrid index '{name}': {results}"
        else:
            return f"Hybrid index '{name}' deleted successfully"

    @lru_cache(maxsize=10)
    def get_hybrid_index(self, name:str, key:str=None):
        """
        Get a reference to a hybrid index.
        
        Args:
            name: Base name of the hybrid index
            key: Encryption key (optional)
            
        Returns:
            HybridIndex object
        """
        # Create names for the underlying dense and sparse indices
        dense_name = f"{name}_dense"
        sparse_name = f"{name}_sparse"
        
        # Step 1: Get dense index info
        headers = {
            'Authorization': self.token,
            'Content-Type': 'application/json'
        }
        
        # Get dense index details
        try:
            dense_response = requests.get(f'{self.base_url}/index/{dense_name}/info', headers=headers)
            if dense_response.status_code != 200:
                raise_exception(dense_response.status_code, dense_response.text)
            dense_data = dense_response.json()
            
            # Verify encryption key checksum
            checksum = get_checksum(key)
            if checksum != dense_data['checksum']:
                raise_exception(460)
        except Exception as e:
            raise ValueError(f"Failed to get dense index info: {str(e)}")
        
        # Step 2: Get sparse index info
        try:
            sparse_response = requests.get(f'{self.base_url}/sparse/{sparse_name}/info', headers=headers)
            if sparse_response.status_code != 200:
                raise_exception(sparse_response.status_code, sparse_response.text)
            sparse_data = sparse_response.json()
        except Exception as e:
            raise ValueError(f"Failed to get sparse index info: {str(e)}")
        
        # Create and return HybridIndex object
        hybrid_idx = HybridIndex(
            name=name,
            key=key,
            token=self.token,
            url=self.base_url,
            dense_name=dense_name,
            sparse_name=sparse_name,
            dense_params=dense_data,
            sparse_params=sparse_data,
            version=self.version
        )
        
        return hybrid_idx

