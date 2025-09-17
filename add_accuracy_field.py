#!/usr/bin/env python3
"""
Script to add accuracy field to TriPoint table
Run this script to add the accuracy field to existing database
"""

import sqlite3
import os

def add_accuracy_field():
    """Add accuracy field to TriPoint table"""
    
    # Check if instance folder exists
    if not os.path.exists('instance'):
        print("Instance folder not found. Please run the app first to create the database.")
        return
    
    db_path = 'instance/fuel_tracker.db'
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Detect actual table name
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_name = None
        if 'tri_points' in tables:
            table_name = 'tri_points'
        elif 'tri_point' in tables:
            table_name = 'tri_point'
        else:
            print("TriPoint table not found (checked: tri_points, tri_point).")
            return
        
        # Check if accuracy column already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'accuracy' in columns:
            print(f"Accuracy column already exists in {table_name} table.")
            return
        
        # Add accuracy column
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN accuracy REAL")
        
        # Commit changes
        conn.commit()
        print(f"Successfully added accuracy column to {table_name} table.")
        
        # Verify the change
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns in {table_name}: {columns}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("Adding accuracy field to TriPoint table...")
    add_accuracy_field()
    print("Done.")
