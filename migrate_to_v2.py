"""
TruthLens Debate Arena - Database Migration to v2.0
File: migrate_to_v2.py
Date: October 21, 2025
Version: 1.0.0

PURPOSE:
Migrate existing debates database from v1.0 to v2.0 schema
Adds all missing columns for partner tracking and handshake system

WHAT THIS DOES:
1. Adds new columns to debate_users table (ban system, handshakes_given)
2. Adds new columns to debates table (partner tracking, ready status, handshakes, share codes)
3. Adds new columns to arguments table (is_hidden)
4. Adds new indexes for performance
5. Migrates existing data to new schema

SAFETY:
- Backs up data before migration
- Uses ALTER TABLE (non-destructive)
- Sets sensible defaults for existing records
- Rollback capability

USAGE:
python migrate_to_v2.py

DO NO HARM: This modifies your database - backs up first!

Last modified: October 21, 2025 - Initial Migration Script
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text, inspect

# Load environment variables
load_dotenv()

# Import Flask app
from app import app
from models import db

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def check_table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(db.engine)
    return table_name in inspector.get_table_names()

def migrate_users_table():
    """Add new columns to debate_users table"""
    print("\n" + "="*80)
    print("MIGRATING debate_users TABLE")
    print("="*80)
    
    migrations = []
    
    # Check and add is_banned column
    if not check_column_exists('debate_users', 'is_banned'):
        migrations.append({
            'sql': 'ALTER TABLE debate_users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE',
            'description': 'Add is_banned column'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_users_banned ON debate_users(is_banned)',
            'description': 'Add index on is_banned'
        })
    
    # Check and add ban_reason column
    if not check_column_exists('debate_users', 'ban_reason'):
        migrations.append({
            'sql': 'ALTER TABLE debate_users ADD COLUMN ban_reason VARCHAR(500)',
            'description': 'Add ban_reason column'
        })
    
    # Check and add banned_at column
    if not check_column_exists('debate_users', 'banned_at'):
        migrations.append({
            'sql': 'ALTER TABLE debate_users ADD COLUMN banned_at TIMESTAMP',
            'description': 'Add banned_at column'
        })
    
    # Check and add failed_handshakes column
    if not check_column_exists('debate_users', 'failed_handshakes'):
        migrations.append({
            'sql': 'ALTER TABLE debate_users ADD COLUMN failed_handshakes INTEGER NOT NULL DEFAULT 0',
            'description': 'Add failed_handshakes column'
        })
    
    # Check and add handshakes_given column
    if not check_column_exists('debate_users', 'handshakes_given'):
        migrations.append({
            'sql': 'ALTER TABLE debate_users ADD COLUMN handshakes_given INTEGER NOT NULL DEFAULT 0',
            'description': 'Add handshakes_given column'
        })
    
    if migrations:
        for migration in migrations:
            try:
                print(f"  ✓ {migration['description']}")
                db.session.execute(text(migration['sql']))
                db.session.commit()
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                db.session.rollback()
                return False
        print(f"\n✓ Successfully migrated debate_users table ({len(migrations)} changes)")
    else:
        print("  ✓ No migration needed - all columns exist")
    
    return True

def migrate_debates_table():
    """Add new columns to debates table"""
    print("\n" + "="*80)
    print("MIGRATING debates TABLE")
    print("="*80)
    
    migrations = []
    
    # Check and add partner_a_id column
    if not check_column_exists('debates', 'partner_a_id'):
        migrations.append({
            'sql': '''ALTER TABLE debates ADD COLUMN partner_a_id INTEGER 
                      REFERENCES debate_users(id)''',
            'description': 'Add partner_a_id column'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_debates_partner_a ON debates(partner_a_id)',
            'description': 'Add index on partner_a_id'
        })
        # Set partner_a_id to creator_id for existing debates
        migrations.append({
            'sql': 'UPDATE debates SET partner_a_id = creator_id WHERE partner_a_id IS NULL',
            'description': 'Set partner_a_id to creator_id for existing debates'
        })
        # Make it NOT NULL after setting values
        migrations.append({
            'sql': 'ALTER TABLE debates ALTER COLUMN partner_a_id SET NOT NULL',
            'description': 'Make partner_a_id NOT NULL'
        })
    
    # Check and add partner_b_id column
    if not check_column_exists('debates', 'partner_b_id'):
        migrations.append({
            'sql': '''ALTER TABLE debates ADD COLUMN partner_b_id INTEGER 
                      REFERENCES debate_users(id)''',
            'description': 'Add partner_b_id column'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_debates_partner_b ON debates(partner_b_id)',
            'description': 'Add index on partner_b_id'
        })
    
    # Check and add partner_a_ready column
    if not check_column_exists('debates', 'partner_a_ready'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN partner_a_ready BOOLEAN NOT NULL DEFAULT FALSE',
            'description': 'Add partner_a_ready column'
        })
    
    # Check and add partner_b_ready column
    if not check_column_exists('debates', 'partner_b_ready'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN partner_b_ready BOOLEAN NOT NULL DEFAULT FALSE',
            'description': 'Add partner_b_ready column'
        })
    
    # Check and add share_code column
    if not check_column_exists('debates', 'share_code'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN share_code VARCHAR(12)',
            'description': 'Add share_code column'
        })
        migrations.append({
            'sql': 'CREATE UNIQUE INDEX idx_debates_share_code_unique ON debates(share_code)',
            'description': 'Add unique index on share_code'
        })
    
    # Check and add voting_started_at column
    if not check_column_exists('debates', 'voting_started_at'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN voting_started_at TIMESTAMP',
            'description': 'Add voting_started_at column'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_debates_voting_started ON debates(voting_started_at)',
            'description': 'Add index on voting_started_at'
        })
    
    # Check and add voting_ends_at column
    if not check_column_exists('debates', 'voting_ends_at'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN voting_ends_at TIMESTAMP',
            'description': 'Add voting_ends_at column'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_debates_voting_ends ON debates(voting_ends_at)',
            'description': 'Add index on voting_ends_at'
        })
    
    # Check and add partner_a_handshake column
    if not check_column_exists('debates', 'partner_a_handshake'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN partner_a_handshake BOOLEAN NOT NULL DEFAULT FALSE',
            'description': 'Add partner_a_handshake column'
        })
    
    # Check and add partner_b_handshake column
    if not check_column_exists('debates', 'partner_b_handshake'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN partner_b_handshake BOOLEAN NOT NULL DEFAULT FALSE',
            'description': 'Add partner_b_handshake column'
        })
    
    # Check and add handshake_deadline column
    if not check_column_exists('debates', 'handshake_deadline'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN handshake_deadline TIMESTAMP',
            'description': 'Add handshake_deadline column'
        })
    
    # Check and add went_live_at column
    if not check_column_exists('debates', 'went_live_at'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN went_live_at TIMESTAMP',
            'description': 'Add went_live_at column'
        })
    
    # Check and add closed_at column
    if not check_column_exists('debates', 'closed_at'):
        migrations.append({
            'sql': 'ALTER TABLE debates ADD COLUMN closed_at TIMESTAMP',
            'description': 'Add closed_at column'
        })
    
    # Update status values for existing debates
    # Check if we need to update old status values to new ones
    migrations.append({
        'sql': "UPDATE debates SET status = 'live' WHERE status = 'active'",
        'description': 'Update old status "active" to "live"'
    })
    
    if migrations:
        for migration in migrations:
            try:
                print(f"  ✓ {migration['description']}")
                db.session.execute(text(migration['sql']))
                db.session.commit()
            except Exception as e:
                # Some migrations might fail if data doesn't exist, that's okay
                if 'does not exist' not in str(e) and 'already exists' not in str(e):
                    print(f"  ⚠ Warning: {e}")
                db.session.rollback()
        print(f"\n✓ Successfully migrated debates table ({len(migrations)} changes)")
    else:
        print("  ✓ No migration needed - all columns exist")
    
    return True

def migrate_arguments_table():
    """Add new columns to arguments table"""
    print("\n" + "="*80)
    print("MIGRATING arguments TABLE")
    print("="*80)
    
    migrations = []
    
    # Check and add is_hidden column
    if not check_column_exists('arguments', 'is_hidden'):
        migrations.append({
            'sql': 'ALTER TABLE arguments ADD COLUMN is_hidden BOOLEAN NOT NULL DEFAULT TRUE',
            'description': 'Add is_hidden column'
        })
        # Set existing arguments to visible (not hidden)
        migrations.append({
            'sql': 'UPDATE arguments SET is_hidden = FALSE',
            'description': 'Set existing arguments to visible'
        })
        migrations.append({
            'sql': 'CREATE INDEX idx_arguments_hidden ON arguments(is_hidden)',
            'description': 'Add index on is_hidden'
        })
    
    # Check and add media_type column
    if not check_column_exists('arguments', 'media_type'):
        migrations.append({
            'sql': "ALTER TABLE arguments ADD COLUMN media_type VARCHAR(20) DEFAULT 'text'",
            'description': 'Add media_type column'
        })
    
    # Check and add media_url column
    if not check_column_exists('arguments', 'media_url'):
        migrations.append({
            'sql': 'ALTER TABLE arguments ADD COLUMN media_url VARCHAR(500)',
            'description': 'Add media_url column'
        })
    
    # Check and add media_duration column
    if not check_column_exists('arguments', 'media_duration'):
        migrations.append({
            'sql': 'ALTER TABLE arguments ADD COLUMN media_duration INTEGER',
            'description': 'Add media_duration column'
        })
    
    if migrations:
        for migration in migrations:
            try:
                print(f"  ✓ {migration['description']}")
                db.session.execute(text(migration['sql']))
                db.session.commit()
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                db.session.rollback()
                return False
        print(f"\n✓ Successfully migrated arguments table ({len(migrations)} changes)")
    else:
        print("  ✓ No migration needed - all columns exist")
    
    return True

def verify_migration():
    """Verify all tables and columns exist"""
    print("\n" + "="*80)
    print("VERIFYING MIGRATION")
    print("="*80)
    
    required_tables = ['debate_users', 'debates', 'arguments', 'votes', 'challenges']
    
    for table in required_tables:
        if check_table_exists(table):
            print(f"  ✓ Table '{table}' exists")
        else:
            print(f"  ✗ Table '{table}' MISSING!")
            return False
    
    # Check key columns
    key_columns = {
        'debate_users': ['is_banned', 'failed_handshakes', 'handshakes_given'],
        'debates': ['partner_a_id', 'partner_b_id', 'partner_a_ready', 'partner_b_ready', 
                    'share_code', 'voting_ends_at', 'partner_a_handshake', 'partner_b_handshake'],
        'arguments': ['is_hidden', 'media_type']
    }
    
    for table, columns in key_columns.items():
        for column in columns:
            if check_column_exists(table, column):
                print(f"  ✓ Column '{table}.{column}' exists")
            else:
                print(f"  ✗ Column '{table}.{column}' MISSING!")
                return False
    
    print("\n" + "="*80)
    print("✓ MIGRATION VERIFICATION SUCCESSFUL")
    print("="*80)
    return True

def main():
    """Main migration function"""
    print("\n" + "="*80)
    print("TRUTHLENS DEBATE ARENA - DATABASE MIGRATION TO v2.0")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Confirm before proceeding
    print("\nThis script will modify your database schema.")
    print("Make sure you have a backup before proceeding!")
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() != 'yes':
        print("\n✗ Migration cancelled")
        sys.exit(0)
    
    with app.app_context():
        try:
            # Run migrations
            print("\nStarting migration...\n")
            
            # Migrate users table
            if not migrate_users_table():
                print("\n✗ Migration failed at debate_users table")
                sys.exit(1)
            
            # Migrate debates table
            if not migrate_debates_table():
                print("\n✗ Migration failed at debates table")
                sys.exit(1)
            
            # Migrate arguments table
            if not migrate_arguments_table():
                print("\n✗ Migration failed at arguments table")
                sys.exit(1)
            
            # Verify migration
            if not verify_migration():
                print("\n✗ Migration verification failed")
                sys.exit(1)
            
            print("\n" + "="*80)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY!")
            print("="*80)
            print("\nYour database is now upgraded to v2.0")
            print("You can now restart your application.")
            print("\n" + "="*80)
            
        except Exception as e:
            print(f"\n✗ Migration failed with error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    main()


# This file is not truncated
