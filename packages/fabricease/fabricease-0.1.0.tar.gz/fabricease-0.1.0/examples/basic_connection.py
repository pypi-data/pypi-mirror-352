"""
FabricEase Basic Connection Example
Author: Abdulrafiu Izuafa

This example shows the simplest way to connect to Fabric SQL Database
"""

from fabricease import FabricDatabase

def main():
    print("🚀 FabricEase Basic Connection Example")
    print("=" * 50)
    
    # Method 1: Connect using environment variables (.env file)
    try:
        # This loads credentials from .env file automatically
        db = FabricDatabase.from_env()
        
        # Test the connection
        result = db.test_connection()
        
        if result['connected']:
            print("✅ Connection successful!")
            print(f"📊 Server: {result['version'][:50]}...")
            print(f"🕐 Server Time: {result['server_time']}")
            print(f"👤 Connected as: {result['user_name']}")
        else:
            print(f"❌ Connection failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have a .env file with your credentials!")
        print("   Run: python -c \"from fabricease.utils import create_env_template; create_env_template()\"")

if __name__ == "__main__":
    main()