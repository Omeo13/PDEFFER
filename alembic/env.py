from logging.config import fileConfig
from sqlalchemy import create_engine
from alembic import context
import sys
import app.core.config

import os

# Add the app root directory to sys.path so imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# in alembic/env.py near the top, after setting sys.path
import app.models  # <- important for Alembic to find all models

# Import the SQLAlchemy Base metadata from your app.db.base module
from app.db.base import Base

# Alembic Config object, provides access to values in alembic.ini
config = context.config
# Set the DB URL manually since it's missing in alembic.ini
config.set_main_option("sqlalchemy.url", app.core.config.DATABASE_URL)

# Set up logging based on config file (alembic.ini)
fileConfig(config.config_file_name)

# Get the database URL from environment variable or alembic.ini
DATABASE_URL = os.getenv('DATABASE_URL', config.get_main_option('sqlalchemy.url'))


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # Required for SQLite
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            compare_type=True,  # Detect type changes during autogenerate
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
