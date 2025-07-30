"""
FabricEase Advanced Usage Example
Author: Abdulrafiu Izuafa

This example shows advanced features and patterns
"""

from fabricease import FabricDatabase
from fabricease.utils import validate_environment, print_connection_help
import json

def demonstrate_context_manager():
    """Show context manager usage"""
    print("🔧 Context Manager Example")
    print("-" * 30)
    
    # Using context manager ensures proper connection cleanup
    with FabricDatabase.from_env() as db:
        result = db.test_connection()
        print(f"✅ Connected: {result['connected']}")
        
        # Get list of tables
        tables = db.get_tables()
        print(f"📋 Found {len(tables)} tables: {', '.join(tables[:5])}")
    
    print("✅ Connection automatically closed")

def demonstrate_error_handling():
    """Show proper error handling"""
    print("\n🛡️ Error Handling Example")
    print("-" * 30)
    
    try:
        db = FabricDatabase.from_env()
        
        # This will fail intentionally
        result = db.query("SELECT * FROM non_existent_table")
        
    except Exception as e:
        print(f"✅ Caught expected error: {type(e).__name__}")
        print(f"   Message: {str(e)[:100]}...")

def demonstrate_transaction_pattern():
    """Show transaction-like operations"""
    print("\n💼 Transaction Pattern Example")
    print("-" * 30)
    
    try:
        db = FabricDatabase.from_env()
        
        # Check if employees table exists
        if not db.table_exists('employees'):
            print("❌ Employees table doesn't exist. Run crud_operations.py first.")
            return
        
        # Begin "transaction" (manual approach)
        try:
            # Multiple related operations
            db.insert('employees', {
                'name': 'Transaction Test',
                'email': 'test@company.com',
                'department': 'IT',
                'salary': 55000.00
            })
            
            db.update(
                table='employees',
                data={'salary': 60000.00},
                where='email = ?',
                params=('test@company.com',)
            )
            
            print("✅ Transaction operations completed")
            
        except Exception as e:
            print(f"❌ Transaction failed: {e}")
            # In real app, you'd rollback here
            
    except Exception as e:
        print(f"❌ Setup error: {e}")

def demonstrate_environment_validation():
    """Show environment validation"""
    print("\n🔍 Environment Validation Example")
    print("-" * 30)
    
    validation = validate_environment()
    
    if validation['valid']:
        print("✅ Environment configuration is valid")
    else:
        print("❌ Environment configuration issues found:")
        for missing in validation['missing']:
            print(f"   - Missing: {missing}")
    
    if validation['warnings']:
        print("⚠️ Warnings:")
        for warning in validation['warnings']:
            print(f"   - {warning}")

def demonstrate_direct_connection():
    """Show direct connection (without .env file)"""
    print("\n🔗 Direct Connection Example")
    print("-" * 30)
    
    # This would work if you provide actual credentials
    print("💡 Direct connection example (credentials not provided):")
    print("""
    db = FabricDatabase(
        server="your-server.database.fabric.microsoft.com",
        database="your-database",
        client_id="your-client-id",
        client_secret="your-client-secret",
        tenant_id="your-tenant-id"
    )
    """)

def demonstrate_data_analysis():
    """Show data analysis capabilities"""
    print("\n📊 Data Analysis Example")
    print("-" * 30)
    
    try:
        db = FabricDatabase.from_env()
        
        if not db.table_exists('employees'):
            print("❌ Employees table doesn't exist. Run crud_operations.py first.")
            return
        
        # Department statistics
        dept_stats = db.query("""
            SELECT 
                department,
                COUNT(*) as employee_count,
                AVG(salary) as avg_salary,
                MIN(salary) as min_salary,
                MAX(salary) as max_salary
            FROM employees 
            WHERE is_active = 1
            GROUP BY department
            ORDER BY avg_salary DESC
        """)
        
        print("🏢 Department Statistics:")
        for dept in dept_stats:
            print(f"   {dept['department']}: {dept['employee_count']} employees, "
                  f"Avg salary: ${dept['avg_salary']:,.2f}")
        
        # Salary distribution
        salary_ranges = db.query("""
            SELECT 
                CASE 
                    WHEN salary < 60000 THEN 'Under $60K'
                    WHEN salary < 70000 THEN '$60K-$70K'  
                    WHEN salary < 80000 THEN '$70K-$80K'
                    ELSE 'Over $80K'
                END as salary_range,
                COUNT(*) as count
            FROM employees
            WHERE is_active = 1
            GROUP BY 
                CASE 
                    WHEN salary < 60000 THEN 'Under $60K'
                    WHEN salary < 70000 THEN '$60K-$70K'
                    WHEN salary < 80000 THEN '$70K-$80K'
                    ELSE 'Over $80K'
                END
            ORDER BY count DESC
        """)
        
        print("\n💰 Salary Distribution:")
        for range_info in salary_ranges:
            print(f"   {range_info['salary_range']}: {range_info['count']} employees")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

def main():
    """Main demonstration function"""
    print("🚀 FabricEase Advanced Usage Demo")
    print("=" * 50)
    
    try:
        demonstrate_environment_validation()
        demonstrate_context_manager()
        demonstrate_error_handling()
        demonstrate_transaction_pattern()
        demonstrate_direct_connection()
        demonstrate_data_analysis()
        
        print("\n🎉 Advanced usage demonstration completed!")
        print("\n💡 For more help, run:")
        print("   from fabricease.utils import print_connection_help")
        print("   print_connection_help()")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")

if __name__ == "__main__":
    main()