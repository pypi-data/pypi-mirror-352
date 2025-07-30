"""
Utility functions for FabricEase
"""

import os
import json
from typing import Dict, Any

def create_env_template(filename: str = '.env') -> None:
    """Create a template .env file with required variables"""
    template = """# FabricEase Configuration
# Microsoft Fabric SQL Database Connection Settings

# Fabric SQL Database Details
FABRIC_SERVER=your-server.database.fabric.microsoft.com
FABRIC_DATABASE=your-database-name

# Azure Service Principal Credentials
# Get these from Azure Portal > Microsoft Entra ID > App registrations
AZURE_CLIENT_ID=your-application-client-id
AZURE_CLIENT_SECRET=your-client-secret-value
AZURE_TENANT_ID=your-directory-tenant-id

# Optional: Alternative variable names (for compatibility)
# AZURE_SQL_SERVER=your-server.database.fabric.microsoft.com
# AZURE_SQL_DATABASE=your-database-name
"""
    
    with open(filename, 'w') as f:
        f.write(template)
    
    print(f"✅ Created {filename} template file")
    print(f"📝 Please edit {filename} with your actual Azure credentials")

def validate_environment() -> Dict[str, Any]:
    """Validate that all required environment variables are set"""
    required_vars = [
        'AZURE_CLIENT_ID',
        'AZURE_CLIENT_SECRET', 
        'AZURE_TENANT_ID'
    ]
    
    server_vars = ['FABRIC_SERVER', 'AZURE_SQL_SERVER']
    database_vars = ['FABRIC_DATABASE', 'AZURE_SQL_DATABASE']
    
    result = {
        'valid': True,
        'missing': [],
        'warnings': []
    }
    
    # Check required auth variables
    for var in required_vars:
        if not os.getenv(var):
            result['missing'].append(var)
            result['valid'] = False
    
    # Check server configuration
    if not any(os.getenv(var) for var in server_vars):
        result['missing'].extend(server_vars)
        result['valid'] = False
    
    # Check database configuration  
    if not any(os.getenv(var) for var in database_vars):
        result['missing'].extend(database_vars)
        result['valid'] = False
    
    return result

def print_connection_help():
    """Print helpful connection troubleshooting information"""
    help_text = """
🔧 FabricEase Connection Help
=============================

Common Issues and Solutions:

1. ❌ Authentication Failed
   - Verify your Azure Service Principal credentials
   - Check that the service principal has access to your Fabric workspace
   - Ensure you're using the correct tenant ID

2. ❌ Connection Timeout  
   - Check your network connectivity
   - Ensure ports 11000-11999 are open for outbound connections
   - Verify firewall settings allow Azure SQL service tags

3. ❌ ODBC Driver Issues
   - Install ODBC Driver 18 for SQL Server
   - Update to the latest version of pyodbc

4. ❌ Environment Variables Missing
   - Run: fabricease.utils.create_env_template()
   - Fill in your actual Azure credentials
   - Load with: fabricease.FabricDatabase.from_env()

5. ✅ Test Your Connection
   - Use: db.test_connection() to verify everything works

For more help, visit: https://github.com/Ramseyxlil/fabrisqldb_python_library
"""
    
    print(help_text)