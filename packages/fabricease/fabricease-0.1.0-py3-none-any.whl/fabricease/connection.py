"""
Core connection handling for Fabric SQL Database
"""

import pyodbc
from .auth import FabricAuthenticator
from .exceptions import FabricConnectionError, FabricConfigurationError

class FabricConnection:
    """Manages connection to Fabric SQL Database"""
    
    def __init__(self, server, database, authenticator=None, **kwargs):
        """
        Initialize Fabric connection
        
        Args:
            server: Fabric SQL server endpoint
            database: Database name
            authenticator: FabricAuthenticator instance
            **kwargs: Additional connection parameters
        """
        self.server = self._validate_server(server)
        self.database = database
        self.authenticator = authenticator or FabricAuthenticator()
        self.connection = None
        self.connection_string = self._build_connection_string(**kwargs)
    
    def _validate_server(self, server):
        """Validate and format server endpoint"""
        if not server:
            raise FabricConfigurationError("Server endpoint is required")
        
        # Add fabric domain if not present
        if not server.endswith('.database.fabric.microsoft.com'):
            if '.' not in server:
                # Assume it's just the server ID
                server = f"{server}.database.fabric.microsoft.com"
        
        return server
    
    def _build_connection_string(self, **kwargs):
        """Build ODBC connection string"""
        # Default connection parameters
        params = {
            'Driver': '{ODBC Driver 18 for SQL Server}',
            'Server': f"{self.server},1433",
            'Database': self.database,
            'Encrypt': 'yes',
            'TrustServerCertificate': 'no'
        }
        
        # Override with any user-provided parameters
        params.update(kwargs)
        
        # Build connection string
        conn_str = ';'.join([f"{key}={value}" for key, value in params.items()])
        return conn_str
    
    def connect(self):
        """Establish connection to Fabric SQL Database"""
        if self.connection:
            return self.connection
        
        try:
            # Get access token
            access_token = self.authenticator.get_access_token()
            token_bytes = self.authenticator.encode_token_for_odbc(access_token)
            
            # Connect using token
            attrs_before = {1256: token_bytes}  # SQL_COPT_SS_ACCESS_TOKEN
            self.connection = pyodbc.connect(
                self.connection_string, 
                attrs_before=attrs_before
            )
            
            return self.connection
            
        except Exception as e:
            raise FabricConnectionError(
                f"Failed to connect to Fabric SQL Database: {str(e)}",
                original_error=e
            )
    
    def disconnect(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def is_connected(self):
        """Check if connection is active"""
        if not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except:
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()