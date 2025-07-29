import requests
import secrets
from vecx.exceptions import raise_exception
from vecx.index import Index
from vecx.crypto import get_checksum
from vecx.utils import is_valid_index_name

class VectorX:
    def __init__(self, token:str):
        self.token = token
        self.base_url = "https://api.vectorxdb.ai"
        self.default_version = 1
        self.env = 'prod'
        self.supported_regions = ["us-west", "india-west"]

    def set_env(self, env:str):
        self.env = env
        if self.env == 'local':
            self.base_url = 'http://127.0.0.1:8080'
            self.supported_regions = ['local']
        elif self.env == 'private':
            self.supported_regions = []
        elif self.env == 'dev':
            self.base_url = 'https://5kxdt2rvme.ap-south-1.awsapprunner.com'
            self.supported_regions = ['us-west-dev', 'india-west-dev']
        

    def __str__(self):
        return self.token

    def generate_key(self)->str:
        # Generate a random hex key of length 32
        key = secrets.token_hex(16)  # 16 bytes * 2 hex chars/byte = 32 chars
        print("Store this encryption key in a secure location. Loss of the key will result in the irreversible loss of associated vector data.\nKey: ",key)
        return key

    def create_index(self, name:str, dimensions:int, key:str, distance_metric:str, region : str="us-west", version:int=None):
        if is_valid_index_name(name) == False:
            raise ValueError("Invalid index name. Index name must be alphanumeric and can contain underscores and less than 48 characters")
        if region not in self.supported_regions and self.env!='private':
            raise ValueError(f"Invalid region: {region}")
        version = version if version else self.default_version
        distance_metric = distance_metric.upper()
        if distance_metric not in ["COSINE", "L2", "DOT_PRODUCT"]:
            raise ValueError(f"Invalid distance metric: {distance_metric}")
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': name,
            'dimensions': dimensions,
            'distance_metric': distance_metric,
            'checksum': get_checksum(key),
            'region': region,
            'version': version
        }
        response = requests.post(f'{self.base_url}/index/create', headers=headers, json=data)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        data = response.json()
        edge_url = data['edge_url']
        # Post to edge server to create an index
        checksum = get_checksum(key)
        headers = {
            'Authorization': f'{self.token}:{name}:{checksum}',
            'Content-Type': 'application/json'
        }
        data = {
            'name': name,
            'dimensions': dimensions,
            'distance_metric': distance_metric,
        }
        response = requests.post(f'{edge_url}/index/create', headers=headers, json=data)
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
        for index in indexes:
            index['name'] = '_'.join(index['name'].split('_')[2:])
        return indexes
    # TODO - Delete the index cache if the index is deleted
    def delete_index(self, name:str, key:str):
        # Get index details from the server. Delete at the edge and then delete at the server
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.get(f'{self.base_url}/index/{name}/get', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        data = response.json()
        edge_url = data['edge_url']
        checksum = get_checksum(key)
        headers = {
            'Authorization': f'{self.token}:{name}:{checksum}',
            'Content-Type': 'application/json'
        }
        response = requests.get(f'{edge_url}/index/{name}/delete', headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        headers = {
            'Authorization': f'{self.token}',
        }
        response = requests.get(f'{self.base_url}/index/{name}/delete', headers=headers)
        if response.status_code != 200:
            print(response.text)
            raise_exception(response.status_code)
        return f'Index {name} deleted successfully'


    def get_index(self, name:str, key:str):
        headers = {
            'Authorization': f'{self.token}',
            'Content-Type': 'application/json'
        }
        # Get index details from the server
        response = requests.get(f'{self.base_url}/index/{name}/get', headers=headers)
        if response.status_code != 200:
            raise_exception(response.status_code)
        data = response.json()
        #print(data)
        # Raise error if checksum does not match
        checksum = get_checksum(key)
        if checksum != data['checksum']:
            raise_exception(460)
        idx = Index(name=name, key=key, token=self.token, lib_token=data['lib_token'], edge_url=data['edge_url'], distance_metric=data['distance_metric'], dimensions=data['dimensions'], version=data['version'])
        return idx
