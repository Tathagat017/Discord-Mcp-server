#!/bin/bash

# FastMCP Discord Integration Server Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 FastMCP Discord Integration Server${NC}"
echo -e "${GREEN}======================================${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Install dependencies
echo -e "${GREEN}📦 Installing dependencies...${NC}"
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from sample...${NC}"
    cp env.sample .env
    echo -e "${RED}❗ Please edit .env file with your Discord bot token and other settings${NC}"
    echo -e "${RED}❗ Then run this script again${NC}"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Check for required environment variables
if ! grep -q "DISCORD_BOT_TOKEN=your_discord_bot_token_here" .env; then
    echo -e "${GREEN}✅ Environment file appears to be configured${NC}"
else
    echo -e "${RED}❗ Please configure your .env file with actual values${NC}"
    exit 1
fi

# Start the server
echo -e "${GREEN}🚀 Starting FastMCP Discord Integration Server...${NC}"
echo -e "${GREEN}📡 Server will be available at: http://localhost:8000${NC}"
echo -e "${GREEN}📚 API Documentation: http://localhost:8000/docs${NC}"
echo -e "${GREEN}🏥 Health Check: http://localhost:8000/health${NC}"
echo ""

# Check if we should run MCP mode or FastAPI mode
if [ "$1" = "mcp" ]; then
    echo -e "${GREEN}🔧 Running in MCP mode (stdio transport)${NC}"
    python -m app.main mcp
else
    echo -e "${GREEN}🔧 Running in FastAPI mode (HTTP transport)${NC}"
    python -m app.main
fi 