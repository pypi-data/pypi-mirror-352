"""
FabricEase - A Professional Python Library for Microsoft Fabric SQL Database Connections

Author: Abdulrafiu Izuafa
Email: abdulrafiu@azurelearnai.org
GitHub: https://github.com/Ramseyxlil/fabrisqldb_python_library
Description: Revolutionizes connecting to and working with Fabric SQL Database, 
            solving industry-wide authentication and connectivity challenges.

Born from real-world enterprise experience, FabricEase transforms complex 
OAuth token encoding and ODBC configuration into simple, intuitive API calls.
"""

__version__ = "0.1.0"
__author__ = "Abdulrafiu Izuafa"
__email__ = "abdulrafiu@azurelearnai.org"
__license__ = "MIT"
__url__ = "https://github.com/Ramseyxlil/fabrisqldb_python_library"
__description__ = "A Professional Python Library for Microsoft Fabric SQL Database Connections"

from .connection import FabricConnection
from .database import FabricDatabase
from .exceptions import (
    FabricConnectionError, 
    FabricAuthenticationError,
    FabricQueryError,
    FabricConfigurationError,
    FabricEaseError
)

# Make the main classes easily accessible
__all__ = [
    'FabricConnection',
    'FabricDatabase', 
    'FabricConnectionError',
    'FabricAuthenticationError',
    'FabricQueryError',
    'FabricConfigurationError',
    'FabricEaseError'
]

# Version information for programmatic access
VERSION_INFO = {
    'major': 0,
    'minor': 1,
    'patch': 0,
    'release': 'stable',
    'build': None
}

def get_version():
    """Return the version string"""
    return __version__

def get_author_info():
    """Return author information"""
    return {
        'name': __author__,
        'email': __email__,
        'github': 'https://github.com/Ramseyxlil',
        'website': 'https://azurelearnai.org'
    }

# Simple usage example in docstring
"""
🚀 Quick Start Guide:

Basic Connection:
    from fabricease import FabricDatabase
    
    # Option 1: Use environment variables (.env file) - Recommended
    db = FabricDatabase.from_env()
    
    # Test connection
    result = db.test_connection()
    print(f"Connected: {result['connected']}")
    
    # Option 2: Direct credentials
    db = FabricDatabase(
        server="your-server.database.fabric.microsoft.com",
        database="your-database",
        client_id="your-client-id",
        client_secret="your-client-secret", 
        tenant_id="your-tenant-id"
    )

Database Operations:
    # Query data with type safety
    employees = db.query("SELECT * FROM employees WHERE salary > ?", (50000,))
    
    # Insert single record
    db.insert("employees", {
        "first_name": "Abdulrafiu",
        "last_name": "Izuafa", 
        "email": "abdulrafiu@azurelearnai.org",
        "department": "Data Engineering",
        "salary": 95000
    })
    
    # Bulk insert for efficiency
    new_employees = [
        {"name": "Alice", "email": "alice@company.com", "salary": 75000},
        {"name": "Bob", "email": "bob@company.com", "salary": 80000}
    ]
    db.insert_many("employees", new_employees)
    
    # Update with conditions
    db.update("employees", 
        data={"salary": 85000},
        where="name = ?", 
        params=("Alice",)
    )

Context Manager (Recommended):
    with FabricDatabase.from_env() as db:
        tables = db.get_tables()
        print(f"Found {len(tables)} tables: {tables}")
    # Connection automatically closed

Error Handling:
    from fabricease import FabricConnectionError, FabricQueryError
    
    try:
        db = FabricDatabase.from_env()
        result = db.query("SELECT * FROM employees")
    except FabricConnectionError as e:
        print(f"Connection failed: {e}")
    except FabricQueryError as e:
        print(f"Query failed: {e}")

Environment Setup:
    # Generate .env template
    python -c "from fabricease.utils import create_env_template; create_env_template()"
    
    # Or use command line tool (installed automatically)
    fabricease-init
    
    # Edit .env with your Azure credentials:
    FABRIC_SERVER=your-server.database.fabric.microsoft.com
    FABRIC_DATABASE=your-database-name
    AZURE_CLIENT_ID=your-application-client-id
    AZURE_CLIENT_SECRET=your-client-secret-value
    AZURE_TENANT_ID=your-directory-tenant-id

Advanced Features:
    # Environment validation
    from fabricease.utils import validate_environment
    validation = validate_environment()
    
    # Performance monitoring
    import time
    start = time.time()
    results = db.query("SELECT COUNT(*) FROM large_table")
    print(f"Query completed in {time.time() - start:.2f}s")
    
    # Schema introspection
    if db.table_exists("employees"):
        columns = db.query(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?",
            ("employees",)
        )

🎯 Why FabricEase?
- ✅ Solves industry-wide Fabric SQL connectivity problems
- ✅ 90% less code than manual implementation  
- ✅ Enterprise-grade error handling and security
- ✅ Production-ready with comprehensive testing
- ✅ Built by developers, for developers

📚 Documentation: https://github.com/Ramseyxlil/fabrisqldb_python_library#readme
🐛 Issues: https://github.com/Ramseyxlil/fabrisqldb_python_library/issues
💬 Discussions: https://github.com/Ramseyxlil/fabrisqldb_python_library/discussions

Created with ❤️ by Abdulrafiu Izuafa to solve real-world enterprise data challenges.
"""

# Library metadata for introspection
__metadata__ = {
    'name': 'fabricease',
    'version': __version__,
    'author': __author__,
    'email': __email__,
    'license': __license__,
    'url': __url__,
    'description': __description__,
    'keywords': [
        'microsoft-fabric', 'sql-database', 'azure', 'authentication', 
        'pyodbc', 'database-connection', 'enterprise', 'data-engineering'
    ],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
}

# Compatibility check
import sys

if sys.version_info < (3, 8):
    raise RuntimeError(
        f"FabricEase requires Python 3.8 or later. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}."
    )

# Optional: Check for required dependencies on import
try:
    import pyodbc
    import azure.identity
    import dotenv
except ImportError as e:
    missing_package = str(e).split("'")[1] if "'" in str(e) else "unknown"
    raise ImportError(
        f"Missing required dependency: {missing_package}. "
        f"Please install FabricEase with: pip install fabricease"
    ) from e

# Welcome message for interactive use
def _show_welcome_message():
    """Show welcome message in interactive environments"""
    import os
    
    # Only show in interactive environments, not in scripts
    if hasattr(sys, 'ps1') or os.environ.get('JUPYTER_RUNTIME_DIR'):
        print("🚀 FabricEase loaded successfully!")
        print(f"📦 Version: {__version__} | 👨‍💻 Author: {__author__}")
        print("💡 Quick start: db = FabricDatabase.from_env()")
        print("📚 Docs: https://github.com/Ramseyxlil/fabrisqldb_python_library")

# Show welcome message on first import
_show_welcome_message()