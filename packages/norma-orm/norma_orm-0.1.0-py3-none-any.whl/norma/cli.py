"""
Norma CLI

Command-line interface for Norma ORM providing project initialization
and code generation capabilities.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

try:
    import typer
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    TYPER_AVAILABLE = True
except ImportError:
    TYPER_AVAILABLE = False
    typer = None
    Console = None

if TYPER_AVAILABLE:
    app = typer.Typer(
        name="norma",
        help="Norma ORM - A modern Python ORM framework",
        add_completion=False,
    )
    console = Console()
else:
    app = None
    console = None


def check_dependencies():
    """Check if required dependencies are available."""
    if not TYPER_AVAILABLE:
        print("Error: Required dependencies not found.")
        print("Please install with: pip install norma-orm[dev]")
        sys.exit(1)


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Name of the project to initialize"),
    template: str = typer.Option("basic", help="Template to use (basic, fastapi, django)"),
    database: str = typer.Option("sqlite", help="Database type (sqlite, postgresql, mongodb, cassandra)"),
    output_dir: Optional[str] = typer.Option(None, help="Output directory (default: current directory)"),
):
    """
    Initialize a new Norma project with example models and configuration.
    """
    check_dependencies()
    
    console.print(Panel.fit(
        f"🚀 Initializing Norma project: [bold green]{project_name}[/bold green]",
        border_style="green"
    ))
    
    # Determine output directory
    if output_dir:
        base_dir = Path(output_dir) / project_name
    else:
        base_dir = Path.cwd() / project_name
    
    # Create project directory
    base_dir.mkdir(parents=True, exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Creating project structure...", total=None)
        
        # Create directory structure
        (base_dir / "models").mkdir(exist_ok=True)
        (base_dir / "schemas").mkdir(exist_ok=True)
        (base_dir / "config").mkdir(exist_ok=True)
        
        progress.update(task, description="Generating configuration files...")
        
        # Generate configuration files
        _create_config_files(base_dir, database)
        
        progress.update(task, description="Creating example models...")
        
        # Generate example models
        _create_example_models(base_dir)
        
        progress.update(task, description="Generating application template...")
        
        # Generate application template based on type
        _create_application_template(base_dir, template, database)
        
        progress.update(task, description="Creating requirements file...")
        
        # Generate requirements.txt
        _create_requirements_file(base_dir, template, database)
        
        progress.update(task, description="Generating README...")
        
        # Generate README
        _create_readme_file(base_dir, project_name, template, database)
    
    console.print(f"\n✅ Project [bold green]{project_name}[/bold green] created successfully!")
    console.print(f"📁 Location: {base_dir.absolute()}")
    console.print("\n📋 Next steps:")
    console.print("1. cd " + str(base_dir.name))
    console.print("2. pip install -r requirements.txt")
    console.print("3. norma generate --models ./models --output ./schemas")
    if template == "fastapi":
        console.print("4. uvicorn main:app --reload")


@app.command()
def generate(
    models: str = typer.Option("./models", help="Path to models directory"),
    output: str = typer.Option("./schemas", help="Output directory for generated schemas"),
    format: str = typer.Option("pydantic", help="Output format (pydantic, dataclass)"),
    watch: bool = typer.Option(False, help="Watch for changes and regenerate automatically"),
):
    """
    Generate Pydantic schemas and ORM code from Norma models.
    """
    check_dependencies()
    
    models_path = Path(models)
    output_path = Path(output)
    
    if not models_path.exists():
        console.print(f"❌ Models directory not found: {models_path}", style="red")
        raise typer.Exit(1)
    
    console.print(Panel.fit(
        "🔄 Generating schemas from Norma models",
        border_style="blue"
    ))
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning models...", total=None)
        
        # Find all Python model files
        model_files = list(models_path.glob("**/*.py"))
        model_files = [f for f in model_files if not f.name.startswith("__")]
        
        progress.update(task, description=f"Found {len(model_files)} model files")
        progress.update(task, total=len(model_files))
        
        generated_files = []
        
        for i, model_file in enumerate(model_files):
            progress.update(task, completed=i, description=f"Processing {model_file.name}...")
            
            try:
                schemas = _generate_schemas_from_file(model_file, output_path, format)
                generated_files.extend(schemas)
            except Exception as e:
                console.print(f"⚠️  Error processing {model_file.name}: {e}", style="yellow")
        
        progress.update(task, completed=len(model_files), description="Generation complete!")
    
    console.print(f"\n✅ Generated {len(generated_files)} schema files:")
    for file_path in generated_files:
        console.print(f"  📄 {file_path}")
    
    if watch:
        console.print("\n👀 Watching for changes... (Press Ctrl+C to stop)")
        _watch_and_regenerate(models_path, output_path, format)


@app.command()
def version():
    """Show Norma version information."""
    check_dependencies()
    
    try:
        from . import __version__
        version_info = __version__
    except ImportError:
        version_info = "unknown"
    
    console.print(Panel.fit(
        f"Norma ORM v{version_info}\n"
        "A modern Python ORM framework",
        title="Version Info",
        border_style="cyan"
    ))


def _create_config_files(base_dir: Path, database: str):
    """Create configuration files."""
    
    # Create database configuration
    config_content = f'''"""
Database configuration for Norma ORM.
"""

import os
from typing import Dict, Any

# Database configuration
DATABASE_CONFIG: Dict[str, Any] = {{
    "type": "{database}",
    "url": os.getenv("DATABASE_URL", _get_default_url()),
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",
}}

def _get_default_url() -> str:
    """Get default database URL based on type."""
    if "{database}" == "sqlite":
        return "sqlite:///./app.db"
    elif "{database}" == "postgresql":
        return "postgresql://user:password@localhost/dbname"
    elif "{database}" == "mongodb":
        return "mongodb://localhost:27017"
    elif "{database}" == "cassandra":
        return "localhost"
    else:
        return "sqlite:///./app.db"

# MongoDB specific configuration
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE", "norma_db")

# Cassandra specific configuration
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "norma_keyspace")
'''
    
    (base_dir / "config" / "database.py").write_text(config_content)
    
    # Create __init__.py files
    (base_dir / "__init__.py").write_text("")
    (base_dir / "models" / "__init__.py").write_text("")
    (base_dir / "schemas" / "__init__.py").write_text("")
    (base_dir / "config" / "__init__.py").write_text("")


def _create_example_models(base_dir: Path):
    """Create example model files."""
    
    user_model = '''"""
User model example.
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from uuid import uuid4

from norma import BaseModel, Field


@dataclass
class User(BaseModel):
    """User model with validation and constraints."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique user identifier"
    )
    
    name: str = Field(
        max_length=100,
        min_length=1,
        index=True,
        description="User's full name"
    )
    
    email: str = Field(
        unique=True,
        max_length=255,
        regex_pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
        description="User's email address"
    )
    
    age: int = Field(
        default=0,
        min_value=0,
        max_value=150,
        description="User's age in years"
    )
    
    is_active: bool = Field(
        default=True,
        description="Whether the user account is active"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Account creation timestamp"
    )
'''
    
    post_model = '''"""
Post model example with relationships.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from uuid import uuid4

from norma import BaseModel, Field, ManyToOne


@dataclass
class Post(BaseModel):
    """Blog post model with user relationship."""
    
    id: str = Field(
        primary_key=True,
        default_factory=lambda: uuid4().hex,
        description="Unique post identifier"
    )
    
    title: str = Field(
        max_length=200,
        min_length=1,
        index=True,
        description="Post title"
    )
    
    content: str = Field(
        min_length=1,
        description="Post content"
    )
    
    author_id: str = Field(
        relationship=ManyToOne("User", foreign_key="id"),
        description="ID of the post author"
    )
    
    published: bool = Field(
        default=False,
        index=True,
        description="Whether the post is published"
    )
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        index=True,
        description="Post creation timestamp"
    )
    
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="Last update timestamp"
    )
'''
    
    (base_dir / "models" / "user.py").write_text(user_model)
    (base_dir / "models" / "post.py").write_text(post_model)


def _create_application_template(base_dir: Path, template: str, database: str):
    """Create application template based on type."""
    
    if template == "fastapi":
        _create_fastapi_template(base_dir, database)
    elif template == "django":
        _create_django_template(base_dir, database)
    else:
        _create_basic_template(base_dir, database)


def _create_basic_template(base_dir: Path, database: str):
    """Create basic application template."""
    
    main_content = f'''"""
Basic Norma application example.
"""

import asyncio
from norma import NormaClient
from config.database import DATABASE_CONFIG, MONGODB_DATABASE_NAME, CASSANDRA_KEYSPACE
from models.user import User
from models.post import Post


async def main():
    """Main application function."""
    
    # Initialize Norma client
    if DATABASE_CONFIG["type"] == "mongodb":
        client = NormaClient(
            adapter_type="mongo",
            database_url=DATABASE_CONFIG["url"],
            database_name=MONGODB_DATABASE_NAME
        )
    elif DATABASE_CONFIG["type"] == "cassandra":
        client = NormaClient(
            adapter_type="cassandra",
            database_url=DATABASE_CONFIG["url"],
            keyspace=CASSANDRA_KEYSPACE
        )
    else:
        client = NormaClient(
            adapter_type="sql",
            database_url=DATABASE_CONFIG["url"]
        )
    
    # Connect to database
    async with client:
        # Create tables/collections
        user_client = client.get_model_client(User)
        post_client = client.get_model_client(Post)
        
        await user_client.create_table()
        await post_client.create_table()
        
        # Create a user
        user = User(
            name="John Doe",
            email="john@example.com",
            age=30
        )
        
        created_user = await user_client.insert(user)
        print(f"Created user: {{created_user}}")
        
        # Create a post
        post = Post(
            title="Hello Norma!",
            content="This is my first post using Norma ORM.",
            author_id=created_user.id,
            published=True
        )
        
        created_post = await post_client.insert(post)
        print(f"Created post: {{created_post}}")
        
        # Find users
        users = await user_client.find_many()
        print(f"Found {{len(users)}} users")
        
        # Find posts
        posts = await post_client.find_many({{"published": True}})
        print(f"Found {{len(posts)}} published posts")


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    (base_dir / "main.py").write_text(main_content)


def _create_fastapi_template(base_dir: Path, database: str):
    """Create FastAPI application template."""
    
    main_content = f'''"""
FastAPI application with Norma ORM.
"""

from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from contextlib import asynccontextmanager

from norma import NormaClient
from config.database import DATABASE_CONFIG, MONGODB_DATABASE_NAME
from models.user import User
from models.post import Post


# Global client instance
client: Optional[NormaClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global client
    
    # Initialize Norma client
    if DATABASE_CONFIG["type"] == "mongodb":
        client = NormaClient(
            adapter_type="mongo",
            database_url=DATABASE_CONFIG["url"],
            database_name=MONGODB_DATABASE_NAME
        )
    else:
        client = NormaClient(
            adapter_type="sql",
            database_url=DATABASE_CONFIG["url"]
        )
    
    # Connect and create tables
    await client.connect()
    
    user_client = client.get_model_client(User)
    post_client = client.get_model_client(Post)
    
    await user_client.create_table()
    await post_client.create_table()
    
    yield
    
    # Cleanup
    await client.disconnect()


app = FastAPI(
    title="Norma ORM API",
    description="Example API using Norma ORM",
    version="1.0.0",
    lifespan=lifespan
)


def get_client() -> NormaClient:
    """Get the global client instance."""
    if client is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return client


@app.get("/users", response_model=List[dict])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    client: NormaClient = Depends(get_client)
):
    """Get all users."""
    user_client = client.get_model_client(User)
    users = await user_client.find_many(offset=skip, limit=limit)
    return [user.to_dict() for user in users]


@app.get("/users/{{user_id}}")
async def get_user(user_id: str, client: NormaClient = Depends(get_client)):
    """Get a specific user."""
    user_client = client.get_model_client(User)
    user = await user_client.find_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user.to_dict()


@app.post("/users")
async def create_user(
    user_data: dict,
    client: NormaClient = Depends(get_client)
):
    """Create a new user."""
    user_client = client.get_model_client(User)
    
    try:
        user = User.from_dict(user_data)
        created_user = await user_client.insert(user)
        return created_user.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/posts", response_model=List[dict])
async def get_posts(
    published: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    client: NormaClient = Depends(get_client)
):
    """Get all posts."""
    post_client = client.get_model_client(Post)
    
    filters = {{}}
    if published is not None:
        filters["published"] = published
    
    posts = await post_client.find_many(filters, offset=skip, limit=limit)
    return [post.to_dict() for post in posts]


@app.post("/posts")
async def create_post(
    post_data: dict,
    client: NormaClient = Depends(get_client)
):
    """Create a new post."""
    post_client = client.get_model_client(Post)
    
    try:
        post = Post.from_dict(post_data)
        created_post = await post_client.insert(post)
        return created_post.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
'''
    
    (base_dir / "main.py").write_text(main_content)


def _create_django_template(base_dir: Path, database: str):
    """Create Django integration template."""
    # This would be more complex and is simplified for the example
    _create_basic_template(base_dir, database)


def _create_requirements_file(base_dir: Path, template: str, database: str):
    """Create requirements.txt file."""
    
    requirements = [
        "norma-orm>=0.1.0",
        "pydantic>=2.0.0",
    ]
    
    if database == "postgresql":
        requirements.extend([
            "psycopg2-binary>=2.9.0",
            "asyncpg>=0.28.0",
        ])
    elif database == "mongodb":
        requirements.extend([
            "motor>=3.0.0",
            "pymongo>=4.0.0",
        ])
    elif database == "cassandra":
        requirements.append("cassandra-driver>=3.25.0")
    
    if template == "fastapi":
        requirements.extend([
            "fastapi>=0.100.0",
            "uvicorn[standard]>=0.22.0",
        ])
    elif template == "django":
        requirements.append("django>=4.2.0")
    
    requirements_content = "\n".join(requirements) + "\n"
    (base_dir / "requirements.txt").write_text(requirements_content)


def _create_readme_file(base_dir: Path, project_name: str, template: str, database: str):
    """Create README.md file."""
    
    readme_content = f'''# {project_name}

A Norma ORM project using {template} template with {database} database.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate schemas:
   ```bash
   norma generate --models ./models --output ./schemas
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `models/` - Norma model definitions
- `schemas/` - Generated Pydantic schemas
- `config/` - Configuration files
- `main.py` - Main application file

## Norma ORM Features

- Type-safe dataclass-based models
- Automatic Pydantic schema generation
- Support for PostgreSQL, SQLite, and MongoDB
- Async and sync operations
- Field validation and constraints

## Models

### User
- `id`: Primary key (auto-generated)
- `name`: User's full name (indexed)
- `email`: Unique email address with validation
- `age`: Age with range validation (0-150)
- `is_active`: Account status
- `created_at`: Creation timestamp

### Post
- `id`: Primary key (auto-generated)
- `title`: Post title (indexed)
- `content`: Post content
- `author_id`: Foreign key to User
- `published`: Publication status (indexed)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Usage Examples

```python
from norma import NormaClient
from models.user import User

# Initialize client
client = NormaClient(
    adapter_type="sql",  # or "mongo"
    database_url="sqlite:///./app.db"
)

# Create a user
user = User(name="John Doe", email="john@example.com", age=30)
created_user = await client.insert(user)

# Find users
users = await client.find_many(User, {{"age": {{"$gte": 18}}}})
```

For more information, visit: https://github.com/Geoion/Norma
'''
    
    (base_dir / "README.md").write_text(readme_content)


def _generate_schemas_from_file(model_file: Path, output_path: Path, format: str) -> List[Path]:
    """Generate schemas from a model file."""
    # This is a simplified implementation
    # In a real implementation, you would parse the Python file,
    # extract model classes, and generate schemas
    
    generated_files = []
    
    # For now, create a placeholder schema file
    schema_file = output_path / f"{model_file.stem}_schemas.py"
    
    schema_content = f'''"""
Generated schemas for {model_file.name}

This file is auto-generated by Norma CLI.
Do not modify manually.
"""

# TODO: Implement actual schema generation
# from norma.schema import generate_schemas
# from models.{model_file.stem} import *

# Generated schemas would be here
'''
    
    schema_file.write_text(schema_content)
    generated_files.append(schema_file)
    
    return generated_files


def _watch_and_regenerate(models_path: Path, output_path: Path, format: str):
    """Watch for file changes and regenerate schemas."""
    # This would implement file watching using watchdog or similar
    # For now, just a placeholder
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n👋 Stopped watching for changes")


if __name__ == "__main__":
    if not TYPER_AVAILABLE:
        check_dependencies()
    app() 