#!/usr/bin/env python3
"""
Simple test to verify basic imports work
"""
import sys

def test_basic_imports():
    """Test basic imports"""
    print("Testing basic imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import discord
        print("✅ Discord.py imported")
    except ImportError as e:
        print(f"❌ Discord.py import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic imported")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import loguru
        print("✅ Loguru imported")
    except ImportError as e:
        print(f"❌ Loguru import failed: {e}")
        return False
    
    try:
        from pydantic_settings import BaseSettings
        print("✅ Pydantic Settings imported")
    except ImportError as e:
        print(f"❌ Pydantic Settings import failed: {e}")
        return False
    
    return True

def test_fastmcp():
    """Test FastMCP import"""
    print("\nTesting FastMCP...")
    
    try:
        from fastmcp import FastMCP
        print("✅ FastMCP imported")
        
        # Try to create an instance
        mcp = FastMCP(name="Test")
        print("✅ FastMCP instance created")
        return True
    except ImportError as e:
        print(f"❌ FastMCP import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ FastMCP creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 FastMCP Discord Server - Basic Tests")
    print("=" * 40)
    
    if not test_basic_imports():
        print("❌ Basic imports failed")
        return 1
    
    if not test_fastmcp():
        print("❌ FastMCP test failed")
        return 1
    
    print("\n✅ All basic tests passed!")
    print("🚀 You can now proceed with the full setup")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 