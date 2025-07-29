"""
Norma ORM User Example

Demonstrates the complete usage of Norma ORM with the User model
as specified in the requirements.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

# Import Norma components
from norma import BaseModel, Field, NormaClient
from norma.schema import generate_schemas


@dataclass
class User(BaseModel):
    """
    User model example: User(name: str, email: str, age: int = 0)
    
    This demonstrates a complete Norma model with:
    - Primary key with auto-generation
    - Field validation and constraints
    - Unique constraints
    - Default values
    - Indexing
    """
    
    # Required name field with validation
    name: str = Field(
        max_length=100,
        min_length=1,
        index=True,
        description="User's full name"
    )
    
    # Unique email with pattern validation
    email: str = Field(
        unique=True,
        max_length=255,
        regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="User's email address"
    )
    
    # Age with default value and range validation
    age: int = Field(
        default=0,
        min_value=0,
        max_value=150,
        description="User's age in years"
    )
    
    # Primary key with auto-generation
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique user identifier"
    )


async def demonstrate_sql_operations():
    """Demonstrate SQL database operations."""
    
    print("🗄️  SQL Database Operations (SQLite)")
    print("=" * 40)
    
    # Initialize SQLite client
    client = NormaClient(
        adapter_type="sql",
        database_url="sqlite:///./users_example.db",
        echo=True  # Show SQL queries
    )
    
    async with client:
        # Get model client
        user_client = client.get_model_client(User)
        
        # Drop and recreate table to start fresh
        try:
            await user_client.drop_table()
            print("🗑️  Dropped existing table")
        except Exception:
            pass  # Table might not exist
        
        # Create table
        await user_client.create_table()
        print("✅ User table created")
        
        # Create users
        users_data = [
            {"name": "John Doe", "email": "john@example.com", "age": 30},
            {"name": "Jane Smith", "email": "jane@example.com", "age": 25},
            {"name": "Bob Wilson", "email": "bob@example.com", "age": 35},
        ]
        
        created_users = []
        for user_data in users_data:
            user = User(**user_data)
            created_user = await user_client.insert(user)
            created_users.append(created_user)
            print(f"✅ Created user: {created_user.name} (ID: {created_user.id})")
        
        # Find all users
        all_users = await user_client.find_many()
        print(f"\n📋 Found {len(all_users)} users:")
        for user in all_users:
            print(f"  - {user.name} ({user.email}) - Age: {user.age}")
        
        # Find users with filters
        adults = await user_client.find_many({"age": {"$gte": 30}})
        print(f"\n👥 Found {len(adults)} users aged 30+:")
        for user in adults:
            print(f"  - {user.name} - Age: {user.age}")
        
        # Find by ID
        first_user = created_users[0]
        found_user = await user_client.find_by_id(first_user.id)
        print(f"\n🔍 Found user by ID: {found_user.name}")
        
        # Update user
        found_user.age = 31
        updated_user = await user_client.update(found_user)
        print(f"📝 Updated user age: {updated_user.name} is now {updated_user.age}")
        
        # Count users
        user_count = await user_client.count()
        print(f"\n📊 Total users: {user_count}")
        
        # Delete user
        deleted = await user_client.delete_by_id(created_users[-1].id)
        print(f"🗑️  Deleted user: {deleted}")
        
        # Final count
        final_count = await user_client.count()
        print(f"📊 Users after deletion: {final_count}")


async def demonstrate_mongo_operations():
    """Demonstrate MongoDB operations."""
    
    print("\n🍃 MongoDB Operations")
    print("=" * 40)
    
    # Initialize MongoDB client
    client = NormaClient(
        adapter_type="mongo",
        database_url="mongodb://localhost:27017",
        database_name="norma_example"
    )
    
    try:
        async with client:
            # Get model client
            user_client = client.get_model_client(User)
            
            # Drop and recreate collection to start fresh
            try:
                await user_client.drop_table()
                print("🗑️  Dropped existing collection")
            except Exception:
                pass  # Collection might not exist
            
            # Create collection and indexes
            await user_client.create_table()
            print("✅ User collection created")
            
            # Create users with unique emails
            import time
            timestamp = int(time.time())
            users_data = [
                {"name": "Alice Johnson", "email": f"alice{timestamp}@mongo.com", "age": 28},
                {"name": "Charlie Brown", "email": f"charlie{timestamp}@mongo.com", "age": 22},
            ]
            
            created_users = []
            for user_data in users_data:
                user = User(**user_data)
                created_user = await user_client.insert(user)
                created_users.append(created_user)
                print(f"✅ Created user: {created_user.name} (ID: {created_user.id})")
            
            # Find with MongoDB-style queries
            young_users = await user_client.find_many({"age": {"$lt": 25}})
            print(f"\n👶 Found {len(young_users)} users under 25:")
            for user in young_users:
                print(f"  - {user.name} - Age: {user.age}")
            
            # Find with sorting
            sorted_users = await user_client.find_many(order_by=["-age"])
            print(f"\n📈 Users sorted by age (descending):")
            for user in sorted_users:
                print(f"  - {user.name} - Age: {user.age}")
    
    except Exception as e:
        print(f"⚠️  MongoDB operation failed: {e}")
        print("Make sure MongoDB is running on localhost:27017")


def demonstrate_pydantic_schemas():
    """Demonstrate Pydantic schema generation."""
    
    print("\n🔧 Pydantic Schema Generation")
    print("=" * 40)
    
    try:
        # Generate all schemas for User model
        schemas = generate_schemas(User)
        
        print("✅ Generated schemas:")
        for schema_type, schema_class in schemas.items():
            print(f"  - {schema_type}: {schema_class.__name__}")
        
        # Create schema instances
        CreateUser = schemas['create']
        ReadUser = schemas['read']
        UpdateUser = schemas['update']
        
        # Example create schema usage
        create_data = {
            "name": "Schema User",
            "email": "schema@example.com",
            "age": 27
        }
        
        create_instance = CreateUser(**create_data)
        print(f"\n📝 Create schema instance: {create_instance}")
        
        # Convert to User model
        user = User.from_dict(create_instance.model_dump())
        print(f"🔄 Converted to User model: {user}")
        
        # Example read schema
        read_instance = ReadUser(**user.to_dict())
        print(f"📖 Read schema instance: {read_instance}")
        
        # Example update schema
        update_data = {"id": user.id, "age": 28}
        update_instance = UpdateUser(**update_data)
        print(f"✏️  Update schema instance: {update_instance}")
        
    except ImportError:
        print("⚠️  Pydantic not available. Install with: pip install pydantic>=2.0.0")


def demonstrate_sync_operations():
    """Demonstrate synchronous operations."""
    
    print("\n🔄 Synchronous Operations")
    print("=" * 40)
    
    # Initialize SQLite client
    client = NormaClient(
        adapter_type="sql",
        database_url="sqlite:///./users_sync.db"
    )
    
    with client:
        # Get model client
        user_client = client.get_model_client(User)
        
        # Create user synchronously
        import time
        timestamp = int(time.time())
        user = User(name="Sync User", email=f"sync{timestamp}@example.com", age=25)
        created_user = user_client.insert_sync(user)
        print(f"✅ Created user synchronously: {created_user.name}")
        
        # Find synchronously
        found_user = user_client.find_by_id_sync(created_user.id)
        print(f"🔍 Found user synchronously: {found_user.name}")
        
        # Update synchronously
        found_user.age = 26
        updated_user = user_client.update_sync(found_user)
        print(f"📝 Updated user synchronously: {updated_user.age}")


async def main():
    """Main demonstration function."""
    
    print("🚀 Norma ORM Complete Example")
    print("=" * 50)
    print("Demonstrating User(name: str, email: str, age: int = 0)")
    print("=" * 50)
    
    # Demonstrate model validation
    print("\n✅ Model Validation")
    print("-" * 20)
    
    try:
        # Valid user
        user = User(name="Valid User", email="valid@example.com", age=25)
        print(f"✅ Valid user created: {user}")
        
        # Invalid user (will raise ValidationError)
        try:
            invalid_user = User(name="", email="invalid-email", age=-5)
        except Exception as e:
            print(f"❌ Validation error (expected): {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Run database demonstrations
    await demonstrate_sql_operations()
    await demonstrate_mongo_operations()
    
    # Demonstrate schema generation
    demonstrate_pydantic_schemas()
    
    # Demonstrate synchronous operations
    demonstrate_sync_operations()
    
    print("\n🎉 All demonstrations completed!")
    print("\nNext steps:")
    print("1. Try the CLI: norma init my-project")
    print("2. Generate schemas: norma generate --models ./models")
    print("3. Explore the documentation and examples")


if __name__ == "__main__":
    asyncio.run(main()) 