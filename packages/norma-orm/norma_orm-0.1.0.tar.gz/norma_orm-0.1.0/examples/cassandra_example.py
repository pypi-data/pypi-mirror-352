"""
Norma ORM Cassandra Example

Demonstrates the usage of Norma ORM with Apache Cassandra database.
Shows time-series data modeling and Cassandra-specific features.
"""

import asyncio
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4

# Import Norma components
from norma import BaseModel, Field, NormaClient
from norma.schema import generate_schemas


@dataclass
class User(BaseModel):
    """
    User model for Cassandra.
    
    Uses UUID as primary key which is suitable for Cassandra's distributed nature.
    """
    
    # Primary key - using UUID for Cassandra
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid4()),
        description="Unique user identifier (UUID)"
    )
    
    # User data
    username: str = Field(
        max_length=50,
        index=True,
        description="Unique username"
    )
    
    email: str = Field(
        max_length=255,
        index=True,
        description="User's email address"
    )
    
    name: str = Field(
        max_length=100,
        description="User's full name"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Account creation timestamp"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )


@dataclass
class Sensor(BaseModel):
    """
    Sensor model for IoT data.
    
    Demonstrates Cassandra's strength in time-series data.
    """
    
    # Partition key - groups related data together
    sensor_id: str = Field(
        primary_key=True,
        description="Sensor identifier (partition key)"
    )
    
    # Clustering key - provides ordering within partition
    timestamp: datetime = Field(
        primary_key=True,
        default_factory=datetime.now,
        description="Measurement timestamp (clustering key)"
    )
    
    # Measurement data
    temperature: float = Field(
        description="Temperature reading in Celsius"
    )
    
    humidity: float = Field(
        description="Humidity percentage"
    )
    
    location: str = Field(
        max_length=100,
        description="Sensor location"
    )
    
    battery_level: Optional[float] = Field(
        default=None,
        min_value=0.0,
        max_value=100.0,
        description="Battery level percentage"
    )


@dataclass
class Event(BaseModel):
    """
    Event log model for distributed systems.
    
    Shows how to model events in Cassandra.
    """
    
    # Time-based UUID for natural ordering
    id: str = Field(
        primary_key=True,
        default_factory=lambda: str(uuid4()),
        description="Event UUID"
    )
    
    event_type: str = Field(
        max_length=50,
        index=True,
        description="Type of event"
    )
    
    user_id: str = Field(
        index=True,
        description="User who triggered the event"
    )
    
    data: str = Field(
        description="Event data (JSON string)"
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        index=True,
        description="Event timestamp"
    )
    
    severity: str = Field(
        default="info",
        description="Event severity level"
    )


async def demonstrate_cassandra_operations():
    """Demonstrate Cassandra database operations."""
    
    print("🗄️  Cassandra Database Operations")
    print("=" * 40)
    
    # Initialize Cassandra client
    client = NormaClient(
        adapter_type="cassandra",
        database_url="127.0.0.1",  # Cassandra contact points
        keyspace="norma_example",
        port=9042,
        # Optional authentication
        # username="cassandra",
        # password="cassandra",
        # protocol_version=4,
        connect_timeout=10,
        request_timeout=10,
    )
    
    try:
        async with client:
            # Get model clients
            user_client = client.get_model_client(User)
            sensor_client = client.get_model_client(Sensor)
            event_client = client.get_model_client(Event)
            
            # Create tables
            await user_client.create_table()
            await sensor_client.create_table()
            await event_client.create_table()
            print("✅ Tables created")
            
            # Create users
            users_data = [
                {"username": "alice", "email": "alice@example.com", "name": "Alice Johnson"},
                {"username": "bob", "email": "bob@example.com", "name": "Bob Smith"},
                {"username": "charlie", "email": "charlie@example.com", "name": "Charlie Brown"},
            ]
            
            created_users = []
            for user_data in users_data:
                user = User(**user_data)
                created_user = await user_client.insert(user)
                created_users.append(created_user)
                print(f"✅ Created user: {created_user.username} (ID: {created_user.id[:8]}...)")
            
            # Demonstrate time-series data with sensors
            print(f"\n📊 Creating sensor data...")
            
            sensor_ids = ["temp_001", "temp_002", "humid_001"]
            locations = ["Room A", "Room B", "Greenhouse"]
            
            # Generate sample sensor data over the last 24 hours
            base_time = datetime.now() - timedelta(hours=24)
            
            for i in range(50):  # 50 measurements
                for j, sensor_id in enumerate(sensor_ids):
                    timestamp = base_time + timedelta(minutes=i * 30)  # Every 30 minutes
                    
                    sensor_data = Sensor(
                        sensor_id=sensor_id,
                        timestamp=timestamp,
                        temperature=20.0 + (j * 5) + (i % 10),  # Varying temperature
                        humidity=40.0 + (j * 10) + (i % 20),    # Varying humidity
                        location=locations[j],
                        battery_level=100.0 - (i * 0.5)  # Declining battery
                    )
                    
                    await sensor_client.insert(sensor_data)
                    
                    if i % 10 == 0:  # Progress indicator
                        print(f"📊 Inserted data for {sensor_id} at {timestamp.strftime('%H:%M')}")
            
            # Query sensor data
            print(f"\n🔍 Querying sensor data...")
            
            # Find data for specific sensor
            sensor_readings = await sensor_client.find_many(
                {"sensor_id": "temp_001"},
                limit=10
            )
            print(f"📈 Found {len(sensor_readings)} readings for temp_001")
            
            # Show recent readings
            if sensor_readings:
                latest = sensor_readings[0]
                print(f"   Latest: {latest.temperature}°C, {latest.humidity}% humidity at {latest.timestamp}")
            
            # Create events
            print(f"\n📝 Creating events...")
            
            event_types = ["login", "logout", "data_export", "settings_change"]
            
            for i, user in enumerate(created_users):
                for j, event_type in enumerate(event_types):
                    event = Event(
                        event_type=event_type,
                        user_id=user.id,
                        data=f'{{"action": "{event_type}", "user": "{user.username}"}}',
                        severity="info" if j < 2 else "warning"
                    )
                    
                    await event_client.insert(event)
                    print(f"📝 Created {event_type} event for {user.username}")
            
            # Query events
            print(f"\n🔍 Querying events...")
            
            # Find events by type
            login_events = await event_client.find_many(
                {"event_type": "login"},
                limit=5
            )
            print(f"🔐 Found {len(login_events)} login events")
            
            # Find events by user
            if created_users:
                user_events = await event_client.find_many(
                    {"user_id": created_users[0].id},
                    limit=10
                )
                print(f"👤 Found {len(user_events)} events for {created_users[0].username}")
            
            # Demonstrate counting
            total_users = await user_client.count()
            total_sensors = await sensor_client.count()
            total_events = await event_client.count()
            
            print(f"\n📊 Database Statistics:")
            print(f"   Users: {total_users}")
            print(f"   Sensor readings: {total_sensors}")
            print(f"   Events: {total_events}")
            
            # Find users by criteria
            active_users = await user_client.find_many({"is_active": True})
            print(f"   Active users: {len(active_users)}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure Cassandra is running on localhost:9042")
        print("You can start Cassandra using Docker:")
        print("docker run -d --name cassandra -p 9042:9042 cassandra:latest")


def demonstrate_cassandra_schema_generation():
    """Demonstrate Pydantic schema generation for Cassandra models."""
    
    print("\n🔧 Cassandra Schema Generation")
    print("=" * 40)
    
    try:
        # Generate schemas for Cassandra models
        for model_class in [User, Sensor, Event]:
            schemas = generate_schemas(model_class)
            
            print(f"\n✅ Generated schemas for {model_class.__name__}:")
            for schema_type, schema_class in schemas.items():
                print(f"  - {schema_type}: {schema_class.__name__}")
            
            # Example usage with User
            if model_class == User:
                CreateUser = schemas['create']
                
                # Create user data
                user_data = {
                    "username": "cassandra_user",
                    "email": "cassandra@example.com",
                    "name": "Cassandra User"
                }
                
                create_instance = CreateUser(**user_data)
                print(f"\n📝 Create schema example: {create_instance}")
                
                # Convert to User model
                user = User.from_dict(create_instance.model_dump())
                print(f"🔄 Converted to User model: {user.username} (ID: {user.id[:8]}...)")
    
    except ImportError:
        print("⚠️  Pydantic not available. Install with: pip install pydantic>=2.0.0")


def demonstrate_cassandra_best_practices():
    """Demonstrate Cassandra-specific best practices."""
    
    print("\n💡 Cassandra Best Practices")
    print("=" * 40)
    
    print("""
    📋 Key Design Principles:
    
    1. 🔑 Partition Key Design:
       - Choose keys that distribute data evenly
       - Avoid hotspots (popular partition keys)
       - Consider your query patterns
    
    2. 🕐 Clustering Key Usage:
       - Provides sorting within partitions
       - Essential for time-series data
       - Enables efficient range queries
    
    3. 📊 Time-Series Modeling:
       - Use timestamp as clustering key
       - Consider bucketing for large datasets
       - Plan for data retention policies
    
    4. 🔍 Query Patterns:
       - Design tables around your queries
       - Denormalization is normal and encouraged
       - Avoid expensive operations (joins, aggregations)
    
    5. 🚀 Performance Tips:
       - Use prepared statements for repeated queries
       - Implement proper pagination
       - Monitor partition sizes
    """)
    
    print("🏗️  Example Time-Series Table Design:")
    print("""
    @dataclass
    class MetricsByDay(BaseModel):
        # Partition by date to distribute load
        date: str = Field(primary_key=True)  # "2024-01-15"
        
        # Cluster by timestamp for ordering
        timestamp: datetime = Field(primary_key=True)
        
        # Include metric data
        metric_name: str = Field()
        value: float = Field()
        tags: str = Field()  # JSON string for metadata
    """)


async def main():
    """Main demonstration function."""
    
    print("🚀 Norma ORM Cassandra Example")
    print("=" * 50)
    print("Demonstrating Cassandra operations with time-series data")
    print("=" * 50)
    
    # Run Cassandra demonstrations
    await demonstrate_cassandra_operations()
    
    # Demonstrate schema generation
    demonstrate_cassandra_schema_generation()
    
    # Show best practices
    demonstrate_cassandra_best_practices()
    
    print("\n🎉 Cassandra demonstration completed!")
    print("\nNext steps:")
    print("1. Install Cassandra: docker run -d --name cassandra -p 9042:9042 cassandra:latest")
    print("2. Try the CLI: norma init my-cassandra-project --database cassandra")
    print("3. Explore time-series modeling patterns")
    print("4. Learn about Cassandra data modeling best practices")


if __name__ == "__main__":
    asyncio.run(main()) 