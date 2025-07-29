import json
class VectorXException(Exception):
    """Base class for all VectorX related exceptions."""
    def __init__(self, message="An error occurred in VectorX"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

# General error class used for various vector operations
class VectorXError(VectorXException):
    """General error class for VectorX operations."""
    def __init__(self, message="An error occurred during vector operation"):
        self.message = message
        super().__init__(message)

class APIException(VectorXException):
    """Generic Exception. Raised when an API call returns an error."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"API Error: {message}")

class ServerException(VectorXException):
    """ 5xx Server Errors."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Server Busy: {message}")

class ForbiddenException(VectorXException):
    """User is not allowed to perform the operation."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Server Busy: {message}")

class DuplicateIndexException(VectorXException):
    """Raised when we try to create an index which exists."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Duplicate Index Error: {message}")

class IndexNotFoundException(VectorXException):
    """Raised when the index is not there."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Index Not Found Error: {message}")

class VectorNotFoundException(VectorXException):
    """Raised when the vector is not there."""
    def __init__(self, message):
        self.message = message
        super().__init__(f"Vector Error: {message}")

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
        super().__init__(f"Subscription Error: {message}")

def raise_exception(code:int, text:str=None):
    """Raise an exception based on the error code."""
    message = None
    try:
        message = json.loads(text).get("error", "Unknown error")
    except (json.JSONDecodeError, TypeError, AttributeError):
        message = text or "Unknown error"

    if code == 400:
        raise APIException(message)
    elif code == 401:
        raise AuthenticationException(message)
    elif code == 403:
        raise ForbiddenException(message)
    elif code == 404:
        raise IndexNotFoundException(message)
    elif code == 409:
        raise DuplicateIndexException(message)
    elif code == 422:
        raise DataFormatException(message)
    elif code == 423:
        raise VectorNotFoundException(message)
    elif code == 460:
        raise KeyException(message)
    elif code == 462:
        raise SubscriptionException(message)
    elif code >= 500:
        message = "Server is busy. Please try again in sometime"
        raise ServerException(message)
    else:
        message = "Unknown Error. Please try again in sometime"
        raise APIException(message)