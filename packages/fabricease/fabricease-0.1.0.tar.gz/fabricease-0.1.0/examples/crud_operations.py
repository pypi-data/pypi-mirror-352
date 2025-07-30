"""
FabricEase CRUD Operations Example
Author: Abdulrafiu Izuafa

This example demonstrates Create, Read, Update, Delete operations
"""

from fabricease import FabricDatabase
import datetime

def create_sample_table(db):
    """Create a sample table for demonstration"""
    print("📋 Creating sample table...")
    
    create_table_sql = """
    IF OBJECT_ID('dbo.employees', 'U') IS NOT NULL
        DROP TABLE dbo.employees;
    
    CREATE TABLE dbo.employees (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        email NVARCHAR(255) UNIQUE,
        department NVARCHAR(50),
        salary DECIMAL(10,2),
        hire_date DATETIME2 DEFAULT GETDATE(),
        is_active BIT DEFAULT 1
    );
    """
    
    db.execute(create_table_sql)
    print("✅ Table created successfully!")

def demonstrate_insert(db):
    """Demonstrate INSERT operations"""
    print("\n➕ INSERT Operations")
    print("-" * 30)
    
    # Insert single record
    employee_data = {
        'name': 'Ahmed Al-Hassan',
        'email': 'ahmed@company.com',
        'department': 'Engineering',
        'salary': 75000.00,
        'is_active': True
    }
    
    rows_affected = db.insert('employees', employee_data)
    print(f"✅ Inserted {rows_affected} employee record")
    
    # Insert multiple records
    employees = [
        {
            'name': 'Fatima Al-Zahra',
            'email': 'fatima@company.com',
            'department': 'Marketing',
            'salary': 68000.00,
            'is_active': True
        },
        {
            'name': 'Omar Mansour',
            'email': 'omar@company.com',
            'department': 'Sales',
            'salary': 62000.00,
            'is_active': True
        },
        {
            'name': 'Layla Ibrahim',
            'email': 'layla@company.com',
            'department': 'HR',
            'salary': 70000.00,
            'is_active': False
        }
    ]
    
    rows_affected = db.insert_many('employees', employees)
    print(f"✅ Bulk inserted {rows_affected} employee records")

def demonstrate_select(db):
    """Demonstrate SELECT operations"""
    print("\n📖 SELECT Operations")
    print("-" * 30)
    
    # Select all employees
    all_employees = db.query("SELECT * FROM employees ORDER BY name")
    print(f"📊 Found {len(all_employees)} total employees:")
    
    for emp in all_employees:
        status = "Active" if emp['is_active'] else "Inactive"
        print(f"   {emp['id']}. {emp['name']} ({emp['department']}) - ${emp['salary']:,.2f} - {status}")
    
    # Select with filtering
    print("\n🔍 Active employees in Engineering:")
    eng_employees = db.query(
        "SELECT * FROM employees WHERE department = ? AND is_active = ?",
        ('Engineering', True)
    )
    
    for emp in eng_employees:
        print(f"   {emp['name']} - {emp['email']}")

def demonstrate_update(db):
    """Demonstrate UPDATE operations"""
    print("\n✏️ UPDATE Operations")
    print("-" * 30)
    
    # Update salary for specific employee
    rows_affected = db.update(
        table='employees',
        data={'salary': 80000.00},
        where='name = ?',
        params=('Ahmed Al-Hassan',)
    )
    print(f"✅ Updated salary for {rows_affected} employee(s)")
    
    # Update department for multiple employees
    rows_affected = db.update(
        table='employees',
        data={'department': 'Business Development'},
        where='department = ?',
        params=('Sales',)
    )
    print(f"✅ Updated department for {rows_affected} employee(s)")

def demonstrate_delete(db):
    """Demonstrate DELETE operations"""
    print("\n🗑️ DELETE Operations")
    print("-" * 30)
    
    # Delete inactive employees
    rows_affected = db.delete(
        table='employees',
        where='is_active = ?',
        params=(False,)
    )
    print(f"✅ Deleted {rows_affected} inactive employee(s)")

def main():
    """Main demonstration function"""
    print("🚀 FabricEase CRUD Operations Demo")
    print("=" * 50)
    
    try:
        # Connect to database
        db = FabricDatabase.from_env()
        
        # Test connection
        result = db.test_connection()
        if not result['connected']:
            print(f"❌ Connection failed: {result['error']}")
            return
        
        print("✅ Connected to Fabric SQL Database")
        
        # Demonstrate all CRUD operations
        create_sample_table(db)
        demonstrate_insert(db)
        demonstrate_select(db)
        demonstrate_update(db)
        demonstrate_select(db)  # Show updated data
        demonstrate_delete(db)
        demonstrate_select(db)  # Show final data
        
        print("\n🎉 CRUD operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
    
    finally:
        # Clean up connection
        if 'db' in locals():
            db.disconnect()

if __name__ == "__main__":
    main()