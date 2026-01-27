#!/usr/bin/env python3
"""
Script to update the database schema for user separation.
This adds user_id columns to existing tables and creates a default user.
"""

import sqlite3
import os
from datetime import datetime

def update_database():
    db_path = 'instance/fuel_tracker.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if user table exists
        default_license = "0000AAA"
        default_password_hash = "pbkdf2:sha256:600000$default$default_hash"
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("Creating user table...")
            cursor.execute("""
                CREATE TABLE user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_number VARCHAR(64) UNIQUE NOT NULL,
                    password_hash VARCHAR(256) NOT NULL,
                    created_at DATETIME NOT NULL
                )
            """)
            
            # Create a default user for existing data
            cursor.execute("""
                INSERT INTO user (license_number, password_hash, created_at)
                VALUES (?, ?, ?)
            """, (default_license, default_password_hash, datetime.utcnow()))
            default_user_id = cursor.lastrowid
            print(f"Created default user with ID: {default_user_id}")
        else:
            # Get the first user ID
            cursor.execute("SELECT id FROM user LIMIT 1")
            result = cursor.fetchone()
            if result:
                default_user_id = result[0]
                print(f"Using existing user with ID: {default_user_id}")
            else:
                print("No users found in database")
                return
        
        # Add user_id column to TriPoint table if it doesn't exist
        cursor.execute("PRAGMA table_info(tri_point)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            print("Adding user_id column to tri_point table...")
            cursor.execute("ALTER TABLE tri_point ADD COLUMN user_id INTEGER")
            cursor.execute("UPDATE tri_point SET user_id = ?", (default_user_id,))
            print("Updated tri_point table")
        
        # Add user_id column to Vehicle table if it doesn't exist
        cursor.execute("PRAGMA table_info(vehicle)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            print("Adding user_id column to vehicle table...")
            cursor.execute("ALTER TABLE vehicle ADD COLUMN user_id INTEGER")
            cursor.execute("UPDATE vehicle SET user_id = ?", (default_user_id,))
            print("Updated vehicle table")
        
        # Add user_id column to FillUp table if it doesn't exist
        cursor.execute("PRAGMA table_info(fill_up)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in columns:
            print("Adding user_id column to fill_up table...")
            cursor.execute("ALTER TABLE fill_up ADD COLUMN user_id INTEGER")
            cursor.execute("UPDATE fill_up SET user_id = ?", (default_user_id,))
            print("Updated fill_up table")
        
        # Commit changes
        conn.commit()
        print("Database updated successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM fill_up")
        fillup_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM vehicle")
        vehicle_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tri_point")
        tripoint_count = cursor.fetchone()[0]
        
        print(f"\nDatabase summary:")
        print(f"Users: {user_count}")
        print(f"Fill-ups: {fillup_count}")
        print(f"Vehicles: {vehicle_count}")
        print(f"Trip points: {tripoint_count}")
        print(f"\nDefault user license number: {default_license}")
        print("You can now log in with this license number and any password, or create new users.")
        
    except Exception as e:
        print(f"Error updating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    update_database()
