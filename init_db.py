"""
TruthLens Debate Arena - Database Initialization Script
File: init_db.py
Date: October 20, 2025
Version: 1.0.0

PURPOSE:
Initialize the database for Debate Arena
Creates all tables and optionally seeds with sample data

USAGE:
python init_db.py                    # Create tables only
python init_db.py --seed             # Create tables and add sample data
python init_db.py --drop-all         # WARNING: Drops all tables first
python init_db.py --seed --drop-all  # Fresh start with sample data

DO NO HARM: This file is NEW - standalone database initialization
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Flask app
from app import app

# Import database and models
from models import (
    db, User, Debate, Argument, Vote, Challenge
)

def drop_all_tables():
    """Drop all tables - USE WITH CAUTION!"""
    print("\n" + "=" * 60)
    print("WARNING: This will DELETE ALL DATA!")
    print("=" * 60)
    response = input("Are you sure you want to drop all tables? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("✓ All tables dropped")


def create_tables():
    """Create all database tables"""
    with app.app_context():
        print("\nCreating database tables...")
        db.create_all()
        print("✓ All tables created successfully")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nCreated tables: {', '.join(tables)}")


def seed_sample_data():
    """Seed database with sample data for testing"""
    with app.app_context():
        print("\nSeeding sample data...")
        
        # Create sample users
        users = []
        
        user1 = User(
            email='alice@example.com',
            display_name='Alice Johnson',
            is_verified=True
        )
        user1.generate_session_token()
        users.append(user1)
        
        user2 = User(
            email='bob@example.com',
            display_name='Bob Smith',
            is_verified=True
        )
        user2.generate_session_token()
        users.append(user2)
        
        user3 = User(
            email='carol@example.com',
            display_name='Carol Williams',
            is_verified=True
        )
        user3.generate_session_token()
        users.append(user3)
        
        for user in users:
            db.session.add(user)
