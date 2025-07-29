from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="norma-orm",
    version="0.1.0",
    author="Geoion",
    author_email="eski.yin@gmail.com",
    description="A modern Python ORM framework with dataclass support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Geoion/Norma",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "typer>=0.9.0",
        "sqlalchemy>=2.0.0",
        "motor>=3.0.0",
        "pymongo>=4.0.0",
        "asyncpg>=0.28.0",  # for async PostgreSQL
        "aiosqlite>=0.19.0",  # for async SQLite
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "postgres": ["psycopg2-binary>=2.9.0"],
        "mysql": ["pymysql>=1.0.0"],
        "cassandra": ["cassandra-driver>=3.25.0"],
    },
    entry_points={
        "console_scripts": [
            "norma=norma.cli:app",
        ],
    },
) 