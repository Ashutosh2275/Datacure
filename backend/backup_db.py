#!/usr/bin/env python
"""
Database backup script for DataCure.
Creates backups of PostgreSQL database with compression and cleanup.
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DatabaseBackup:
    """
    Manages PostgreSQL database backups.
    """
    
    def __init__(self, backup_dir='./backups'):
        """
        Initialize backup manager.
        
        Args:
            backup_dir: Directory for backups
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Database connection details
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_name = os.getenv('DB_NAME', 'datacure_local')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
    
    def create_backup(self, use_compression=True):
        """
        Create database backup.
        
        Args:
            use_compression: Whether to compress backup
        
        Returns:
            (success, backup_path, error_message)
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if use_compression:
                backup_file = self.backup_dir / f'datacure_backup_{timestamp}.sql.gz'
                cmd = f'pg_dump -h {self.db_host} -U {self.db_user} -d {self.db_name} | gzip > {backup_file}'
            else:
                backup_file = self.backup_dir / f'datacure_backup_{timestamp}.sql'
                cmd = f'pg_dump -h {self.db_host} -U {self.db_user} -d {self.db_name} > {backup_file}'
            
            # Set password environment variable for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            logger.info(f"Starting backup to {backup_file}...")
            
            # Execute backup
            result = subprocess.run(
                cmd,
                shell=True,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                backup_size = backup_file.stat().st_size / (1024 * 1024)  # Size in MB
                logger.info(f"✓ Backup created successfully: {backup_file} ({backup_size:.2f} MB)")
                return True, str(backup_file), None
            else:
                error_msg = result.stderr or "Unknown error"
                logger.error(f"✗ Backup failed: {error_msg}")
                return False, None, error_msg
        
        except Exception as e:
            logger.error(f"✗ Backup error: {str(e)}")
            return False, None, str(e)
    
    def restore_backup(self, backup_file):
        """
        Restore database from backup.
        
        Args:
            backup_file: Path to backup file
        
        Returns:
            (success, error_message)
        """
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"
            
            logger.info(f"Starting restore from {backup_file}...")
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_password
            
            # Determine if file is compressed
            is_compressed = str(backup_file).endswith('.gz')
            
            if is_compressed:
                cmd = f'gunzip -c {backup_file} | psql -h {self.db_host} -U {self.db_user} -d {self.db_name}'
            else:
                cmd = f'psql -h {self.db_host} -U {self.db_user} -d {self.db_name} < {backup_file}'
            
            # Execute restore
            result = subprocess.run(
                cmd,
                shell=True,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✓ Restore completed successfully")
                return True, None
            else:
                error_msg = result.stderr or "Unknown error"
                logger.error(f"✗ Restore failed: {error_msg}")
                return False, error_msg
        
        except Exception as e:
            logger.error(f"✗ Restore error: {str(e)}")
            return False, str(e)
    
    def list_backups(self):
        """
        List all available backups.
        
        Returns:
            List of backup files with info
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob('datacure_backup_*.sql*'), reverse=True):
            try:
                stat_info = backup_file.stat()
                size_mb = stat_info.st_size / (1024 * 1024)
                modified = datetime.fromtimestamp(stat_info.st_mtime)
                
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': round(size_mb, 2),
                    'modified': modified.strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                logger.warning(f"Error reading backup file info: {str(e)}")
        
        return backups
    
    def cleanup_old_backups(self, days=7, keep_minimum=3):
        """
        Remove backups older than specified days.
        
        Args:
            days: Keep backups from last N days
            keep_minimum: Minimum backups to keep
        
        Returns:
            (deleted_count, error_message)
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            backup_files = sorted(self.backup_dir.glob('datacure_backup_*.sql*'), reverse=True)
            
            deleted_count = 0
            
            for i, backup_file in enumerate(backup_files):
                # Keep minimum backups
                if i < keep_minimum:
                    continue
                
                try:
                    modified = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    
                    if modified < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup_file.name}")
                except Exception as e:
                    logger.warning(f"Error deleting backup {backup_file.name}: {str(e)}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup completed: {deleted_count} old backups deleted")
            
            return deleted_count, None
        
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return 0, str(e)
    
    def verify_backup(self, backup_file):
        """
        Verify backup integrity.
        
        Args:
            backup_file: Path to backup file
        
        Returns:
            (is_valid, error_message)
        """
        try:
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return False, f"Backup file not found: {backup_file}"
            
            # Check file size
            file_size = backup_path.stat().st_size
            if file_size == 0:
                return False, "Backup file is empty"
            
            # For compressed files, try to decompress
            if str(backup_file).endswith('.gz'):
                try:
                    import gzip
                    with gzip.open(backup_file, 'rb') as f:
                        # Try reading first 1KB
                        f.read(1024)
                except Exception as e:
                    return False, f"Compressed backup is corrupted: {str(e)}"
            
            logger.info(f"✓ Backup verification passed: {backup_path.name}")
            return True, None
        
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False, str(e)


def main():
    """
    Main function for backup operations.
    """
    if len(sys.argv) < 2:
        print("""
        DataCure Database Backup Tool
        
        Usage:
            python backup_db.py create [--no-compress]
            python backup_db.py restore <backup_file>
            python backup_db.py list
            python backup_db.py cleanup [--days=7] [--keep=3]
            python backup_db.py verify <backup_file>
        
        Examples:
            # Create compressed backup
            python backup_db.py create
            
            # Create uncompressed backup
            python backup_db.py create --no-compress
            
            # Restore from backup
            python backup_db.py restore ./backups/datacure_backup_20250228_100000.sql.gz
            
            # List all backups
            python backup_db.py list
            
            # Clean backups older than 7 days
            python backup_db.py cleanup --days=7 --keep=3
            
            # Verify backup integrity
            python backup_db.py verify ./backups/datacure_backup_20250228_100000.sql.gz
        """)
        sys.exit(1)
    
    backup = DatabaseBackup()
    command = sys.argv[1].lower()
    
    if command == 'create':
        use_compression = '--no-compress' not in sys.argv
        success, path, error = backup.create_backup(use_compression=use_compression)
        
        if not success:
            print(f"Error: {error}")
            sys.exit(1)
        
        sys.exit(0)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("Error: Please provide backup file path")
            sys.exit(1)
        
        backup_file = sys.argv[2]
        success, error = backup.restore_backup(backup_file)
        
        if not success:
            print(f"Error: {error}")
            sys.exit(1)
        
        sys.exit(0)
    
    elif command == 'list':
        backups = backup.list_backups()
        
        if not backups:
            print("No backups found")
            sys.exit(0)
        
        print("\nAvailable Backups:")
        print("-" * 80)
        print(f"{'Filename':<40} {'Size':<10} {'Modified':<20}")
        print("-" * 80)
        
        for backup_info in backups:
            print(f"{backup_info['filename']:<40} {backup_info['size_mb']} MB     {backup_info['modified']}")
        
        print("-" * 80)
        sys.exit(0)
    
    elif command == 'cleanup':
        days = 7
        keep = 3
        
        # Parse optional arguments
        for arg in sys.argv[2:]:
            if arg.startswith('--days='):
                days = int(arg.split('=')[1])
            elif arg.startswith('--keep='):
                keep = int(arg.split('=')[1])
        
        deleted, error = backup.cleanup_old_backups(days=days, keep_minimum=keep)
        
        if error:
            print(f"Error: {error}")
            sys.exit(1)
        
        print(f"Deleted {deleted} old backups")
        sys.exit(0)
    
    elif command == 'verify':
        if len(sys.argv) < 3:
            print("Error: Please provide backup file path")
            sys.exit(1)
        
        backup_file = sys.argv[2]
        is_valid, error = backup.verify_backup(backup_file)
        
        if not is_valid:
            print(f"Error: {error}")
            sys.exit(1)
        
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
