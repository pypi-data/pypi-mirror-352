"""
Custom exceptions for FabricEase library
"""

class FabricEaseError(Exception):
    """Base exception for all FabricEase errors"""
    pass

class FabricConnectionError(FabricEaseError):
    """Raised when connection to Fabric SQL Database fails"""
    def __init__(self, message, original_error=None):
        super().__init__(message)
        self.original_error = original_error

class FabricAuthenticationError(FabricEaseError):
    """Raised when authentication fails"""
    def __init__(self, message, auth_method=None):
        super().__init__(message)
        self.auth_method = auth_method

class FabricQueryError(FabricEaseError):
    """Raised when SQL query execution fails"""
    def __init__(self, message, query=None, original_error=None):
        super().__init__(message)
        self.query = query
        self.original_error = original_error

class FabricConfigurationError(FabricEaseError):
    """Raised when configuration is invalid or missing"""
    pass