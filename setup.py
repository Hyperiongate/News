#!/usr/bin/env python3
"""
Setup script for News Analyzer project
Run this after updating your code to set up the database and dependencies
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} - Success!")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e}")
        return False
    return True

def main():
    print("""
    News Analyzer Setup Script
    =========================
    This will set up your development environment.
    """)
    
    # Step 1: Install Python dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        print("\n⚠️  Failed to install dependencies. Please check requirements.txt")
        return
    
    # Step 2: Set up environment file
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ Created .env file. Please edit it with your API keys!")
        else:
            print("⚠️  No .env.example found. Please create .env manually.")
    else:
        print("\n✅ .env file already exists")
    
    # Step 3: Initialize database
    print("\n🗄️  Setting up database...")
    
    # Create a temporary script to initialize the database
    init_db_script = """
from app import app
from models import db, seed_sources

with app.app_context():
    # Create all tables
    db.create_all()
    print("✅ Database tables created")
    
    # Seed initial data
    seed_sources()
    print("✅ Initial source data seeded")
"""
    
    with open('temp_init_db.py', 'w') as f:
        f.write(init_db_script)
    
    try:
        subprocess.run([sys.executable, 'temp_init_db.py'], check=True)
        os.remove('temp_init_db.py')
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("You may need to initialize it manually")
        if os.path.exists('temp_init_db.py'):
            os.remove('temp_init_db.py')
    
    # Step 4: Create necessary directories
    directories = [
        'static/css/components',
        'static/js/components',
        'templates',
        'services'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("\n✅ Directory structure verified")
    
    # Step 5: Final instructions
    print("""
    
    🎉 Setup Complete!
    ================
    
    Next steps:
    1. Edit .env file with your API keys:
       - OPENAI_API_KEY (required for AI analysis)
       - GOOGLE_FACT_CHECK_API_KEY (optional but recommended)
       - NEWS_API_KEY (optional)
    
    2. Run the application:
       python app.py
    
    3. Access the app at:
       http://localhost:5000
    
    Optional: To get a Google Fact Check API key:
    - Go to https://console.cloud.google.com
    - Create a new project or select existing
    - Enable "Fact Check Tools API"
    - Create credentials (API Key)
    
    Happy analyzing! 🔍
    """)

if __name__ == '__main__':
    main()
