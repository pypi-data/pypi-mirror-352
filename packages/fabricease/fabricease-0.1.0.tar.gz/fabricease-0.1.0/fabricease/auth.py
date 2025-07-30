"""
Authentication module for Fabric SQL Database
Handles all the complex token-based authentication
"""

import os
import struct
from itertools import chain, repeat
from azure.identity import ClientSecretCredential, DefaultAzureCredential, AzureCliCredential
from .exceptions import FabricAuthenticationError

class FabricAuthenticator:
    """Handles authentication for Fabric SQL Database"""
    
    def __init__(self, client_id=None, client_secret=None, tenant_id=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self._token_cache = {}
    
    @classmethod
    def from_env(cls):
        """Create authenticator from environment variables"""
        return cls(
            client_id=os.getenv('AZURE_CLIENT_ID'),
            client_secret=os.getenv('AZURE_CLIENT_SECRET'),
            tenant_id=os.getenv('AZURE_TENANT_ID')
        )
    
    def get_access_token(self):
        """Get access token for Fabric SQL Database"""
        try:
            # Try service principal first if credentials provided
            if all([self.client_id, self.client_secret, self.tenant_id]):
                return self._get_service_principal_token()
            
            # Fallback to default credential chain
            return self._get_default_credential_token()
            
        except Exception as e:
            raise FabricAuthenticationError(
                f"Failed to acquire access token: {str(e)}", 
                auth_method="token"
            )
    
    def _get_service_principal_token(self):
        """Get token using service principal"""
        credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        
        token_object = credential.get_token("https://database.windows.net/.default")
        return token_object.token
    
    def _get_default_credential_token(self):
        """Get token using default credential chain"""
        # Try Azure CLI first, then other methods
        try:
            credential = AzureCliCredential()
            token_object = credential.get_token("https://database.windows.net/.default")
            return token_object.token
        except:
            # Fallback to default credential
            credential = DefaultAzureCredential(exclude_interactive_browser_credential=True)
            token_object = credential.get_token("https://database.windows.net/.default")
            return token_object.token
    
    def encode_token_for_odbc(self, token):
        """
        Encode access token for ODBC driver consumption
        This handles the complex binary encoding required by the ODBC driver
        """
        # Convert token to bytes
        token_as_bytes = bytes(token, "UTF-8")
        
        # Encode for wide characters (required by ODBC driver)
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        
        # Add length prefix
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        
        return token_bytes