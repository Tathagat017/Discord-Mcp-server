"""
FastMCP Discord Integration Server
Main application entry point
"""
import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
from loguru import logger
import uvicorn

from .config import get_settings
from .auth.middleware import AuthenticationMiddleware, APIKeyAuth, generate_api_key
from .discord.bot import get_discord_bot, shutdown_discord_bot
from .mcp.tools import create_discord_tools


# Initialize settings
settings = get_settings()

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level
)

if settings.log_file:
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting FastMCP Discord Integration Server")
    
    # Initialize Discord bot
    try:
        bot = await get_discord_bot()
        logger.info("Discord bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Discord bot: {e}")
        if not settings.debug:
            raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down FastMCP Discord Integration Server")
    await shutdown_discord_bot()


# Create FastAPI application
app = FastAPI(
    title="FastMCP Discord Integration Server",
    description="A secure, scalable MCP backend server for Discord bot integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(
    AuthenticationMiddleware,
    excluded_paths=["/health", "/docs", "/openapi.json", "/redoc", "/generate-api-key"]
)

# Create FastMCP instance
mcp = FastMCP(
    name=settings.mcp_server_name,
    instructions="""
    This is a FastMCP Discord Integration Server that provides tools for interacting with Discord.
    
    Available tools:
    - send_message: Send messages to Discord channels
    - get_messages: Retrieve recent messages from channels
    - get_channel_info: Get detailed channel information
    - search_messages: Search for messages by keyword
    - delete_message: Delete specific messages (moderation)
    - ban_user: Ban users from guilds (moderation)
    - kick_user: Kick users from guilds (moderation)
    - get_guild_info: Get detailed guild information
    
    Authentication is required via API key in the X-API-Key header or Authorization header.
    All operations are logged for audit purposes.
    """,
    on_duplicate_tools="replace",
    on_duplicate_resources="warn",
    on_duplicate_prompts="replace"
)

# Register Discord tools
mcp = create_discord_tools(mcp)

# Initialize API key authentication
api_key_auth = APIKeyAuth()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if Discord bot is ready
        bot = await get_discord_bot()
        bot_status = "ready" if bot.is_ready else "not_ready"
    except Exception as e:
        bot_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "FastMCP Discord Integration Server",
        "version": "1.0.0",
        "discord_bot": bot_status,
        "timestamp": asyncio.get_event_loop().time()
    }


# API key generation endpoint (for demo purposes)
@app.post("/generate-api-key")
async def generate_api_key_endpoint(user_id: str):
    """Generate API key for a user (demo endpoint)"""
    try:
        api_key = generate_api_key(user_id, settings.api_key_secret)
        logger.info(f"Generated API key for user: {user_id}")
        
        return {
            "api_key": api_key,
            "user_id": user_id,
            "instructions": "Use this API key in the X-API-Key header or Authorization header"
        }
    except Exception as e:
        logger.error(f"Failed to generate API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate API key")


# MCP endpoints
@app.get("/mcp/tools")
async def list_mcp_tools(request: Request):
    """List available MCP tools"""
    user = getattr(request.state, 'user', None)
    logger.info(f"User {user.get('user_id', 'unknown')} requested MCP tools list")
    
    tools = []
    for tool_name, tool_func in mcp._tools.items():
        tools.append({
            "name": tool_name,
            "description": tool_func.__doc__.strip() if tool_func.__doc__ else "No description",
            "parameters": tool_func.__annotations__
        })
    
    return {
        "tools": tools,
        "count": len(tools)
    }


@app.post("/mcp/call-tool")
async def call_mcp_tool(request: Request, tool_name: str, parameters: Dict[str, Any]):
    """Call an MCP tool"""
    user = getattr(request.state, 'user', None)
    logger.info(f"User {user.get('user_id', 'unknown')} calling tool: {tool_name}")
    
    try:
        if tool_name not in mcp._tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        tool_func = mcp._tools[tool_name]
        result = await tool_func(**parameters)
        
        logger.info(f"Tool {tool_name} executed successfully")
        return {
            "tool": tool_name,
            "result": result,
            "user": user.get('user_id', 'unknown')
        }
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


# Mount MCP server
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("FastMCP Discord Integration Server started")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"MCP debug: {settings.mcp_debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("FastMCP Discord Integration Server shutting down")


def run_server():
    """Run the server"""
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


def run_mcp():
    """Run the MCP server directly"""
    logger.info("Starting MCP server in standalone mode")
    mcp.run()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # Run MCP server directly
        run_mcp()
    else:
        # Run FastAPI server
        run_server()
