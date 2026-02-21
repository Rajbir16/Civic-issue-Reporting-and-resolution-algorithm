"""
Quick fix script to add missing columns to SQLite database.
Run this once to fix the database schema.
"""
import sqlite3
import os

DB_PATH = os.path.join('instance', 'civic_issues.db')

def fix_database():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run app.py to create it.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check and add columns
    try:
        cursor.execute("ALTER TABLE complaint ADD COLUMN original_description TEXT")
        print("✓ Added original_description column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ original_description column already exists")
        else:
            print(f"✗ Error: {e}")
    
    try:
        cursor.execute("ALTER TABLE complaint ADD COLUMN translated_description TEXT")
        print("✓ Added translated_description column")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("✓ translated_description column already exists")
        else:
            print(f"✗ Error: {e}")
    
    conn.commit()
    conn.close()
    print("\nDatabase fix complete!")

if __name__ == '__main__':
    fix_database()
