class ModelManagerClientError(Exception):
    """Base exception for Model Manager Client errors"""
    pass

class ConnectionError(ModelManagerClientError):
    """Raised when connection to gRPC server fails"""
    pass

class ValidationError(ModelManagerClientError):
    """Raised when input validation fails"""
    pass