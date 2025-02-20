import os
import shutil
import sqlite3
from datetime import datetime

# Configuration
DATABASE_PATH = "attendance.db"  # Path to your SQLite database
BACKUP_DIR = "E:\\share\\database"  # Directory to store backups

def list_tables_in_database(db_path):
    """Lists all tables in the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Query to get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if tables:
            print("Tables in the database:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("No tables found in the database.")
    except sqlite3.Error as e:
        print(f"Failed to retrieve tables: {e}")

def backup_sqlite_database():
    """Backs up the SQLite database."""
    # Ensure the backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Generate backup filename with the current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    backup_filename = f"backup_{current_date}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    # Copy the database file to the backup directory
    try:
        if os.path.exists(DATABASE_PATH):
            shutil.copy(DATABASE_PATH, backup_path)
            print(f"Backup successful: {backup_path}")
            # List tables in the database
            list_tables_in_database(DATABASE_PATH)
        else:
            print(f"Database file not found at path: {DATABASE_PATH}")
    except Exception as e:
        print(f"Failed to backup database: {e}")

def app():
    """Main application entry point."""
    print("Starting backup process...")
    backup_sqlite_database()

if __name__ == "__main__":
    app()
