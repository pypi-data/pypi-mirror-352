
import os
import json
import platform
import ctypes
from functools import lru_cache

@lru_cache(maxsize=4)
def load_libvx():
    """Loads the correct C++ library based on the OS and architecture."""

    system = platform.system().lower()
    arch = platform.machine().lower()

    # Linux
    if system == "linux":
        if arch == "x86_64" or arch == "amd64":
            library_name = "libvx_x86_64.so"
        elif arch == "arm64" or arch == "aarch64":
            library_name = "libvx_arm64.so"
        else:
            raise Exception(f"Unsupported architecture for Linux: {arch}")
    # macOS (Darwin)
    elif system == "darwin":
        if arch == "x86_64":
            library_name = "libvx_x86_64.dylib"
        elif arch == "arm64":
            library_name = "libvx_arm64.dylib"
        else:
            raise Exception(f"Unsupported architecture for macOS: {arch}")
    # Windows
    # TODO - check for arm architecture in Windows
    # TODO - check for 32-bit architecture in Windows
    elif system == "windows" or "mingw" in system:
        if arch == "amd64" or arch == "x86_64":  # 64-bit
            library_name = "libvx_x86_64.dll"
        elif arch == "x86":  # 32-bit
            library_name = "libvx_x86_64.dll"
        else:
            raise Exception(f"Unsupported architecture for Windows: {arch}")
    else:
        raise Exception(f"Unsupported operating system: {system}")

    # Ensure library file exists
    library_path = os.path.join(os.path.dirname(__file__), "libvx", library_name)
    if not os.path.exists(library_path):
        raise Exception(f"Library file not found: {library_path}")

    #print(f"Loading library: {library_path}")

    # Load the library using ctypes
    vxlib = ctypes.cdll.LoadLibrary(library_path)
    return vxlib

# Define the argument and return types of the functions

# Define the function to encode a string
def encode_vector(key:str, lib_token:str, distance_metric:str, version:int, vector):
    libvx = load_libvx()
    libvx.encode_vector.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
    libvx.encode_vector.restype = None
    # Convert the string to a byte string
    key = key.encode('utf-8')
    lib_token = lib_token.encode('utf-8')
    distance_metric = distance_metric.encode('utf-8')
    # Convert the string to a c_char_p
    c_key = ctypes.c_char_p(key)
    c_lib_token = ctypes.c_char_p(lib_token)
    c_distance_metric = ctypes.c_char_p(distance_metric)
    vector_size = len(vector)
    c_vector = (ctypes.c_double * vector_size)(*vector)
    c_transformed_vector = (ctypes.c_double * vector_size)()
    # Call the function
    libvx.encode_vector(c_key, c_lib_token, c_distance_metric, version, vector_size, c_vector, c_transformed_vector)
    transformed_vector = list(c_transformed_vector)
    #print(transformed_vector)
    return transformed_vector

# Define the function to decode a string
def decode_vector(key:str, lib_token:str, distance_metric:str, version:int, vector):
    libvx = load_libvx()
    libvx.decode_vector.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]
    libvx.decode_vector.restype = None
    # Convert the string to a byte string
    key = key.encode('utf-8')
    lib_token = lib_token.encode('utf-8')
    distance_metric = distance_metric.encode('utf-8')
    # Convert the string to a c_char_p
    c_key = ctypes.c_char_p(key)
    c_lib_token = ctypes.c_char_p(lib_token)
    c_distance_metric = ctypes.c_char_p(distance_metric)
    vector_size = len(vector)
    c_vector = (ctypes.c_double * vector_size)(*vector)
    c_transformed_vector = (ctypes.c_double * vector_size)()
    # Call the function
    libvx.decode_vector(c_key, c_lib_token, c_distance_metric, version, vector_size, c_vector, c_transformed_vector)
    transformed_vector = list(c_transformed_vector)
    return transformed_vector

def encode(key: str, lib_token: str, distance_metric: str, version: int, input_array: list):
    """Encodes a JSON array using the loaded C++ library."""

    libvx = load_libvx()

    # Define argument types and return type for the C function
    libvx.encode.argtypes = [
        ctypes.c_char_p,       # key
        ctypes.c_char_p,       # lib_token
        ctypes.c_char_p,       # distance_metric
        ctypes.c_int,         # version
        ctypes.c_int,         # vector_size
        ctypes.c_char_p,       # input_array
        ctypes.POINTER(ctypes.c_char_p)  # output_array (double pointer)
    ]
    libvx.encode.restype = None  # No direct return value; output is via the pointer

    # Encode input strings
    c_key = key.encode('utf-8')
    c_lib_token = lib_token.encode('utf-8')
    c_distance_metric = distance_metric.encode('utf-8')

    # Determine vector size and encode input array
    vector_size = len(input_array[0]['vector'])
    input_array_str = json.dumps(input_array)
    c_input_array = input_array_str.encode('utf-8')

    # Output pointer initialization (important!)
    c_output_array = ctypes.c_char_p(None)

    # Call the C++ function
    libvx.encode(c_key, c_lib_token, c_distance_metric, version, vector_size, c_input_array, ctypes.byref(c_output_array))

    # Handle output
    output_string = c_output_array.value.decode('utf-8')  # Decode the returned string
    output_array = json.loads(output_string)              # Parse JSON
    
    # Free the memory allocated in C++ for the output array
    libvx.free_output_buffer(c_output_array) 

    return output_array  

def decode(key: str, lib_token: str, distance_metric: str, version: int, query_vector: list, input_array: list):
    """Decodes data using the loaded C++ library and a query vector."""

    libvx = load_libvx()

    # Define argument types and return type
    libvx.decode.argtypes = [
        ctypes.c_char_p,       # key
        ctypes.c_char_p,       # lib_token
        ctypes.c_char_p,       # distance_metric
        ctypes.c_int,         # version
        ctypes.c_int,         # vector_size
        ctypes.POINTER(ctypes.c_double),  # query_vector
        ctypes.c_char_p,       # input_array
        ctypes.POINTER(ctypes.c_char_p)  # output_array (double pointer)
    ]
    libvx.decode.restype = None  # Output is via the double pointer

    # Encode strings
    c_key = key.encode('utf-8')
    c_lib_token = lib_token.encode('utf-8')
    c_distance_metric = distance_metric.encode('utf-8')

    # Convert query_vector to C-compatible format
    c_query_vector = (ctypes.c_double * len(query_vector))(*query_vector)

    # Prepare input array as JSON string
    input_array_str = json.dumps(input_array)
    c_input_array = input_array_str.encode('utf-8')

    # Output pointer initialization (important for C++ to write to)
    c_output_array = ctypes.c_char_p(None)

    # Call the C++ function
    libvx.decode(c_key, c_lib_token, c_distance_metric, version, len(query_vector), c_query_vector, c_input_array, ctypes.byref(c_output_array))

    # Handle output and free memory
    output_string = c_output_array.value.decode('utf-8')
    output_array = json.loads(output_string)
    # Free memory allocated in C++
    libvx.free_output_buffer(c_output_array) 

    return output_array
