#!/usr/bin/env python3
"""
Test script to verify FastMCP Discord Integration Server setup
"""
import os
import sys
import asyncio
from typing import Dict, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.config import get_settings, TestingSettings
    from app.auth.middleware import generate_api_key, APIKeyAuth
    from app.mcp.tools import create_discord_tools
    from fastmcp import FastMCP
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_configuration():
    """Test configuration management"""
    print("\n🔧 Testing Configuration...")
    
    try:
        # Test with testing settings
        settings = TestingSettings()
        print(f"✅ Settings loaded: {settings.app_name}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_authentication():
    """Test authentication system"""
    print("\n🔐 Testing Authentication...")
    
    try:
        # Test API key generation
        api_key = generate_api_key("test_user", "test_secret")
        print(f"✅ API key generated: {api_key[:20]}...")
        
        # Test API key auth
        auth = APIKeyAuth(auto_error=False)
        print("✅ API key auth initialized")
        return True
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False


def test_mcp_tools():
    """Test MCP tools creation"""
    print("\n🛠️  Testing MCP Tools...")
    
    try:
        # Create MCP instance
        mcp = FastMCP(name="Test Server")
        print("✅ FastMCP instance created")
        
        # Add Discord tools
        mcp = create_discord_tools(mcp)
        print("✅ Discord tools added")
        
        # Check if tools were registered
        tool_names = list(mcp._tools.keys())
        print(f"✅ {len(tool_names)} tools registered:")
        for tool_name in tool_names:
            print(f"   - {tool_name}")
        
        return True
    except Exception as e:
        print(f"❌ MCP tools test failed: {e}")
        return False


def test_imports():
    """Test all critical imports"""
    print("\n📦 Testing Imports...")
    
    imports_to_test = [
        ("fastapi", "FastAPI"),
        ("pydantic", "BaseModel"),
        ("discord", "discord"),
        ("loguru", "logger"),
        ("uvicorn", "uvicorn"),
        ("fastmcp", "FastMCP"),
    ]
    
    failed_imports = []
    
    for module_name, import_name in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {import_name} imported successfully")
        except ImportError as e:
            print(f"❌ {import_name} import failed: {e}")
            failed_imports.append(import_name)
    
    return len(failed_imports) == 0


def main():
    """Run all tests"""
    print("🧪 FastMCP Discord Integration Server - Setup Test")
    print("=" * 55)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Authentication", test_authentication),
        ("MCP Tools", test_mcp_tools),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test passed")
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print("\n" + "=" * 55)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Setup is working correctly.")
        print("\n🚀 Next steps:")
        print("1. Copy env.sample to .env")
        print("2. Configure your Discord bot token in .env")
        print("3. Run: python -m app.main")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 