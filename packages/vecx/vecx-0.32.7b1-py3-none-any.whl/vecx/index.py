import requests, json
from .libvx import encode, decode, encode_vector
from .crypto import get_checksum
from .exceptions import raise_exception

class Index:
    def __init__(self, name:str, key:str, token:str, lib_token:str, edge_url:str, dimensions:int, region:str="us-west", distance_metric:str="COSINE", version:int=1):
        self.name = name
        self.key = key
        self.token = token
        self.lib_token = lib_token
        self.edge_url = edge_url
        self.region = region
        self.distance_metric = distance_metric
        self.dimensions = dimensions
        self.version = version
        self.checksum = get_checksum(self.key)

    def __str__(self):
        return self.name

    def upsert(self, input_array):
        if len(input_array) > 1000:
            raise ValueError("Cannot insert more than 1000 vectors at a time")
        for e in input_array:
            if "filter" not in e:
                e["filter"] = {}
            if "meta" not in e:
                e["meta"] = {}
        checksum = get_checksum(self.key)
        encoded_array = encode(self.key, self.lib_token, self.distance_metric, self.version, input_array)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
            'Content-Type': 'application/json'
        }
        data = {
            'checksum': checksum,
            'vectors': encoded_array,
        }
        response = requests.post(f'{self.edge_url}/vector/{self.name}/upsert', headers=headers, json=data)
        print(response.text)
        if response.status_code != 200:
            raise_exception(response.status_code)
        return "Vectors inserted successfully"

    def query(self, vector, top_k=10, include_vectors=False, log=False):
        if top_k > 1000:
            raise ValueError("top_k cannot be greater than 1000")
        checksum = get_checksum(self.key)
        encoded_vector = encode_vector(key=self.key,lib_token=self.lib_token,distance_metric=self.distance_metric, version=self.version, vector=vector)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
            'Content-Type': 'application/json'
        }
        data = {
            'vector': encoded_vector,
            'checksum': checksum,
            'top_k': top_k,
            'distance_metric': self.distance_metric
        }
        response = requests.post(f'{self.edge_url}/vector/{self.name}/query', headers=headers, json=data)
        if response.status_code != 200:
            raise_exception(response.status_code)
        if log == True:
            print(response.text)
        results = response.json()
        #print(results)
        round_off = True
        result_array = decode(key=self.key,lib_token=self.lib_token, distance_metric=self.distance_metric, version=self.version, query_vector=vector, input_array = results)
        for result in result_array:
            if not include_vectors:
                del result["vector"]
            else:
                result["vector"] = [round(x, 6) for x in result["vector"]]
            if round_off:
                result["similarity"] = round(result["similarity"], 4)
        return result_array[0:top_k]

    def query_with_filter(self, vector, filter, top_k=10, include_vectors=False, log=False):
        if top_k > 1000:
            raise ValueError("top_k cannot be greater than 1000")
        checksum = get_checksum(self.key)
        encoded_vector = encode_vector(key=self.key,lib_token=self.lib_token,distance_metric=self.distance_metric, version=self.version, vector=vector)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
            'Content-Type': 'application/json'
        }
        data = {
            'vector': encoded_vector,
            'filter': filter,
            'checksum': checksum,
            'top_k': top_k,
            'distance_metric': self.distance_metric
        }
        response = requests.post(f'{self.edge_url}/vector/{self.name}/query_with_filter', headers=headers, json=data)
        if response.status_code != 200:
            raise_exception(response.status_code)
        if log == True:
            print(response.text)
        results = response.json()
        #print(results)
        round_off = True
        result_array = decode(key=self.key,lib_token=self.lib_token, distance_metric=self.distance_metric, version=self.version, query_vector=vector, input_array = results)
        for result in result_array:
            if not include_vectors:
                del result["vector"]
            if round_off:
                result["similarity"] = round(result["similarity"], 4)
        return result_array[0:top_k]

    def delete_vector(self, id):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
            }
        data = {
            'checksum': checksum,
        }
        response = requests.get(f'{self.edge_url}/vector/{self.name}/delete/{id}', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        return response.text + " rows deleted"
    
    # Delete multiple vectors based on a filter
    def delete_with_filter(self, filter):
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
            'Content-Type': 'application/json'
            }
        data = {"filter": filter}
        print(filter)
        response = requests.post(f'{self.edge_url}/vector/{self.name}/delete_with_filter', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return response.text
    
    def describe(self):
        checksum = get_checksum(self.key)
        checksum = get_checksum(self.key)
        headers = {
            'Authorization': f'{self.token}:{self.name}:{self.checksum}',
        }
        response = requests.get(f'{self.edge_url}/index/{self.name}/describe', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        data = {
            "name": self.name,
            "dimensions": self.dimensions,
            "distance_metric": self.distance_metric,
            "region": self.region,
            "rows": response.text
        }
        return data

