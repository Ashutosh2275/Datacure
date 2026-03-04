#!/usr/bin/env python
"""
Database migration management script for DataCure.

Usage:
    python manage_migrations.py init          # Initialize Alembic (one-time)
    python manage_migrations.py migrate       # Apply pending migrations
    python manage_migrations.py downgrade     # Rollback last migration
    python manage_migrations.py generate      # Generate new migration (auto-detect)
    python manage_migrations.py current       # Show current migration version
    python manage_migrations.py history       # Show migration history
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))


def run_command(cmd):
    """Run shell command and return result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(project_root / 'backend'))
    return result.returncode


def init_migrations():
    """Initialize Alembic migration system."""
    print("Initializing Alembic migrations...")
    cmd = [sys.executable, '-m', 'alembic', 'stamp', 'head']
    return run_command(cmd)


def apply_migrations():
    """Apply pending database migrations."""
    print("Applying pending migrations...")
    cmd = [sys.executable, '-m', 'alembic', 'upgrade', 'head']
    return run_command(cmd)


def downgrade_migration():
    """Downgrade to previous migration."""
    print("Downgrading to previous migration...")
    cmd = [sys.executable, '-m', 'alembic', 'downgrade', '-1']
    return run_command(cmd)


def generate_migration(message='auto'):
    """Generate new migration based on model changes."""
    print(f"Generating migration: {message}")
    cmd = [sys.executable, '-m', 'alembic', 'revision', '--autogenerate', '-m', message]
    return run_command(cmd)


def show_current():
    """Show current migration version."""
    print("Current migration version:")
    cmd = [sys.executable, '-m', 'alembic', 'current']
    return run_command(cmd)


def show_history():
    """Show migration history."""
    print("Migration history:")
    cmd = [sys.executable, '-m', 'alembic', 'history']
    return run_command(cmd)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'init':
        sys.exit(init_migrations())
    elif command == 'migrate':
        sys.exit(apply_migrations())
    elif command == 'downgrade':
        sys.exit(downgrade_migration())
    elif command == 'generate':
        message = sys.argv[2] if len(sys.argv) > 2 else 'auto'
        sys.exit(generate_migration(message))
    elif command == 'current':
        sys.exit(show_current())
    elif command == 'history':
        sys.exit(show_history())
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
