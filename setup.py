"""
Setup script for Fiapinho Bot

This script helps with the initial setup and installation of the bot.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required!")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies!")
        return False


def setup_environment():
    """Set up environment file."""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("   Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping .env setup")
            return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ .env file created from .env.example")
        print("⚠️  Please edit .env file with your configuration!")
        return True
    else:
        print("❌ .env.example file not found!")
        return False


def create_directories():
    """Create necessary directories."""
    dirs = ["logs", "app/database", "src/images"]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")
    return True


def verify_setup():
    """Verify that the setup is correct."""
    print("🔍 Verifying setup...")
    
    try:
        # Test imports
        import discord
        import dotenv
        import aiohttp
        import validators
        print("✅ All dependencies imported successfully")
        
        # Check main files
        required_files = ["main.py", "app/__init__.py", ".env"]
        missing_files = []
        
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        
        print("✅ All required files present")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up Fiapinho Bot...\n")
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Verifying setup", verify_setup),
    ]
    
    failed_steps = []
    
    for step_name, step_function in steps:
        print(f"\n{step_name}...")
        if not step_function():
            failed_steps.append(step_name)
    
    print("\n" + "="*50)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Edit .env file with your Discord token and FIAP credentials")
        print("   2. Run: python main.py")
        print("\n📖 For more information, check README.md")
    else:
        print(f"❌ Setup failed! Issues with: {', '.join(failed_steps)}")
        print("\n🔧 Please resolve the issues and run setup again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
