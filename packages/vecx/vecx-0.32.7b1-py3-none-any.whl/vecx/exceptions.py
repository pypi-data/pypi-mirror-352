class VectorXException(Exception):
    """Base class for all VectorX related exceptions."""
    pass

class APIException(VectorXException):
    """Generic Exception. Raised when an API call returns an error."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"API Error: {message}")

class DuplicateIndexException(VectorXException):
    """Raised when we try to create an index which exists."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Index Error: {message}")

class IndexNotFoundException(VectorXException):
    """Raised when the index is not there."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Index Error: {message}")

class AuthenticationException(VectorXException):
    """Exception raised for token is invalid."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Authentication Error: {message}")

class KeyException(VectorXException):
    """Exception raised for token is invalid."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Key Error: {message}")

class DataFormatException(VectorXException):
    """Exception raised when metadata is no JSON."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Data Format Error: {message}")

class SubscriptionException(VectorXException):
    """Exception raised when metadata is no JSON."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Upgrade your subscription: {message}")

def raise_exception(code:int, message:str=None):
    """Raise an exception based on the error code."""
    if code == 400:
        if message is None:
            message = "Bad Request"
        raise APIException(message)
    elif code == 401:
        if message is None:
            message = "Unauthorized. Invalid token."
        raise AuthenticationException(message)
    elif code == 409:
        if message is None:
            message = "Index already exists."
        raise DuplicateIndexException(message)
    elif code == 404:
        if message is None:
            message = "Index not found."
        raise IndexNotFoundException(message)
    elif code == 422:
        if message is None:
            message = "Data format error."
        raise DataFormatException(message)
    elif code == 460:
        if message is None:
            message = "Key checksum does not match with the index. Please verify if the key is correct"
        raise KeyException(message)
    elif code == 461:
        if message is None:
            message = "Index already exists."
        raise DuplicateIndexException(message)
    elif code == 462:
        if message is None:
            message = "Upgrade your subscription for this operation."
        raise DuplicateIndexException(message)
    else:
        raise APIException(message)