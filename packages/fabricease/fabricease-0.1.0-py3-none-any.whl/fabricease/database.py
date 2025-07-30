"""
High-level database operations for Fabric SQL Database
"""

import os
import datetime
from typing import Dict, List, Any, Optional, Union
from .connection import FabricConnection
from .auth import FabricAuthenticator
from .exceptions import FabricQueryError, FabricConfigurationError

class FabricDatabase:
    """High-level interface for Fabric SQL Database operations"""
    
    def __init__(self, server=None, database=None, client_id=None, 
                 client_secret=None, tenant_id=None, **kwargs):
        """
        Initialize FabricDatabase
        
        Args:
            server: Fabric SQL server endpoint
            database: Database name  
            client_id: Azure client ID
            client_secret: Azure client secret
            tenant_id: Azure tenant ID
            **kwargs: Additional connection parameters
        """
        
        # Validate required parameters
        if not server or not database:
            raise FabricConfigurationError(
                "Server and database are required. "
                "Use FabricDatabase.from_env() to load from environment variables."
            )
        
        # Setup authenticator
        authenticator = FabricAuthenticator(client_id, client_secret, tenant_id)
        
        # Setup connection
        self.connection_manager = FabricConnection(
            server=server,
            database=database, 
            authenticator=authenticator,
            **kwargs
        )
        
        self._connection = None
    
    @classmethod
    def from_env(cls, env_file='.env'):
        """
        Create FabricDatabase from environment variables
        
        Expected environment variables:
        - FABRIC_SERVER or AZURE_SQL_SERVER
        - FABRIC_DATABASE or AZURE_SQL_DATABASE  
        - AZURE_CLIENT_ID
        - AZURE_CLIENT_SECRET
        - AZURE_TENANT_ID
        """
        # Load .env file if it exists
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        
        # Get configuration from environment
        server = os.getenv('FABRIC_SERVER') or os.getenv('AZURE_SQL_SERVER')
        database = os.getenv('FABRIC_DATABASE') or os.getenv('AZURE_SQL_DATABASE')
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not server or not database:
            raise FabricConfigurationError(
                "Missing required environment variables. Please set:\n"
                "- FABRIC_SERVER (or AZURE_SQL_SERVER)\n"
                "- FABRIC_DATABASE (or AZURE_SQL_DATABASE)\n"
                "- AZURE_CLIENT_ID\n"
                "- AZURE_CLIENT_SECRET\n" 
                "- AZURE_TENANT_ID"
            )
        
        return cls(
            server=server,
            database=database,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id
        )
    
    def connect(self):
        """Establish database connection"""
        if not self._connection:
            self._connection = self.connection_manager.connect()
        return self._connection
    
    def disconnect(self):
        """Close database connection"""
        if self._connection:
            self.connection_manager.disconnect()
            self._connection = None
    
    def query(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as list of dictionaries
        
        Args:
            sql: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List of dictionaries representing rows
        """
        connection = self.connect()
        
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch all rows and convert to dictionaries
            rows = []
            for row in cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = value
                rows.append(row_dict)
            
            cursor.close()
            return rows
            
        except Exception as e:
            raise FabricQueryError(
                f"Query execution failed: {str(e)}",
                query=sql,
                original_error=e
            )
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """
        Execute INSERT/UPDATE/DELETE query
        
        Args:
            sql: SQL query string
            params: Query parameters (optional)
            
        Returns:
            Number of affected rows
        """
        connection = self.connect()
        
        try:
            cursor = connection.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            affected_rows = cursor.rowcount
            connection.commit()
            cursor.close()
            
            return affected_rows
            
        except Exception as e:
            connection.rollback()
            raise FabricQueryError(
                f"Query execution failed: {str(e)}",
                query=sql,
                original_error=e
            )
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """
        Insert a single row into table
        
        Args:
            table: Table name
            data: Dictionary of column -> value mappings
            
        Returns:
            Number of affected rows
        """
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = tuple(data.values())
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        return self.execute(sql, values)
    
    def insert_many(self, table: str, data: List[Dict[str, Any]]) -> int:
        """
        Insert multiple rows into table
        
        Args:
            table: Table name
            data: List of dictionaries (column -> value mappings)
            
        Returns:
            Number of affected rows
        """
        if not data:
            return 0
        
        # Use first row to determine columns
        columns = list(data[0].keys())
        placeholders = ', '.join(['?' for _ in columns])
        
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        connection = self.connect()
        
        try:
            cursor = connection.cursor()
            
            # Convert data to list of tuples
            values_list = [tuple(row[col] for col in columns) for row in data]
            
            cursor.executemany(sql, values_list)
            affected_rows = cursor.rowcount
            connection.commit()
            cursor.close()
            
            return affected_rows
            
        except Exception as e:
            connection.rollback()
            raise FabricQueryError(
                f"Bulk insert failed: {str(e)}",
                query=sql,
                original_error=e
            )
    
    def update(self, table: str, data: Dict[str, Any], where: str, params: tuple = None) -> int:
        """
        Update rows in table
        
        Args:
            table: Table name
            data: Dictionary of column -> value mappings to update
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause
            
        Returns:
            Number of affected rows
        """
        set_clause = ', '.join([f"{col} = ?" for col in data.keys()])
        values = tuple(data.values())
        
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        if params:
            all_params = values + params
        else:
            all_params = values
        
        return self.execute(sql, all_params)
    
    def delete(self, table: str, where: str, params: tuple = None) -> int:
        """
        Delete rows from table
        
        Args:
            table: Table name
            where: WHERE clause (without 'WHERE' keyword)
            params: Parameters for WHERE clause
            
        Returns:
            Number of affected rows
        """
        sql = f"DELETE FROM {table} WHERE {where}"
        return self.execute(sql, params)
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in database"""
        sql = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
        """
        
        results = self.query(sql)
        return [row['TABLE_NAME'] for row in results]
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        sql = """
        SELECT COUNT(*) as count
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ? AND TABLE_TYPE = 'BASE TABLE'
        """
        
        result = self.query(sql, (table_name,))
        return result[0]['count'] > 0
    
    def test_connection(self) -> Dict[str, Any]:
        """Test database connection and return server info"""
        sql = "SELECT @@VERSION as version, GETDATE() as server_time, USER_NAME() as user_name"
        
        try:
            result = self.query(sql)
            return {
                'connected': True,
                'version': result[0]['version'],
                'server_time': result[0]['server_time'],
                'user_name': result[0]['user_name']
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()