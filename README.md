# FastMCP Discord Integration Server

A secure, scalable **Model Context Protocol (MCP) backend server** built with **FastAPI** and **FastMCP**, enabling AI models to interact with Discord through a comprehensive set of tools.

## 🌟 Features

- **Discord Bot Integration**: Send messages, retrieve history, search content, and moderate channels
- **MCP Protocol Support**: Full compatibility with MCP Inspector and MCP clients
- **Secure Authentication**: API key-based authentication with role-based permissions
- **Multi-tenancy**: Support for multiple Discord bots per client
- **Real-time Debugging**: Integration with MCP Inspector for request monitoring
- **Comprehensive Logging**: Structured logging with audit trail
- **Rate Limiting**: Built-in protection against abuse
- **FastAPI Integration**: RESTful API endpoints alongside MCP tools

## 🛠️ Available MCP Tools

| Tool               | Description                            | Permissions Required |
| ------------------ | -------------------------------------- | -------------------- |
| `send_message`     | Send messages to Discord channels      | Send Messages        |
| `get_messages`     | Retrieve recent messages from channels | Read Message History |
| `get_channel_info` | Get detailed channel information       | View Channels        |
| `search_messages`  | Search messages by keyword             | Read Message History |
| `delete_message`   | Delete specific messages               | Manage Messages      |
| `ban_user`         | Ban users from guilds                  | Ban Members          |
| `kick_user`        | Kick users from guilds                 | Kick Members         |
| `get_guild_info`   | Get detailed guild information         | View Channels        |

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Discord Bot Token
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd fastmcp-discord-server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the sample environment file
cp env.sample .env

# Edit .env with your configuration
nano .env
```

**Required Environment Variables:**

- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `API_KEY_SECRET`: Secret for API key generation
- `JWT_SECRET_KEY`: Secret for JWT tokens

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable the following bot permissions:
   - Send Messages
   - Read Message History
   - View Channels
   - Manage Messages (for moderation)
   - Ban Members (for moderation)
   - Kick Members (for moderation)

### 5. Running the Server

```bash
# Run FastAPI server (recommended for development)
python -m app.main

# Or run MCP server directly
python -m app.main mcp

# Or using uvicorn directly
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📡 API Usage

### Authentication

All API calls require authentication via API key:

```bash
# Generate an API key
curl -X POST "http://localhost:8000/generate-api-key" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "your_user_id"}'
```

### Using MCP Tools

```bash
# List available tools
curl -X GET "http://localhost:8000/mcp/tools" \
  -H "X-API-Key: your_api_key"

# Call a tool
curl -X POST "http://localhost:8000/mcp/call-tool" \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "send_message",
    "parameters": {
      "channel_id": 123456789,
      "content": "Hello from MCP!"
    }
  }'
```

### Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 🔧 MCP Client Integration

### Using with MCP Inspector

1. Install MCP Inspector
2. Configure connection to `http://localhost:8000`
3. Use API key for authentication
4. Monitor real-time requests and responses

### Using with AI Models

Configure your AI model client to use the MCP server:

```json
{
  "server_url": "http://localhost:8000",
  "api_key": "your_api_key",
  "tools": ["send_message", "get_messages", "search_messages"]
}
```

## 🏗️ Project Structure

```
fastmcp_backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main FastAPI + MCP server
│   ├── config.py            # Configuration management
│   ├── auth/
│   │   ├── __init__.py
│   │   └── middleware.py    # Authentication middleware
│   ├── discord/
│   │   ├── __init__.py
│   │   └── bot.py          # Discord bot integration
│   ├── mcp/
│   │   ├── __init__.py
│   │   └── tools.py        # MCP tools implementation
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── db/
│   │   └── __init__.py
│   └── tests/
│       └── __init__.py
├── requirements.txt
├── env.sample
└── README.md
```

## 🔐 Security Features

- **API Key Authentication**: Secure HMAC-based API keys
- **Rate Limiting**: Configurable request limits
- **CORS Protection**: Configurable allowed origins
- **Input Validation**: Pydantic schema validation
- **Audit Logging**: Complete action logging
- **Permission Checks**: Role-based access control

## 🧪 Testing

```bash
# Run tests
pytest app/tests/

# Run with coverage
pytest --cov=app app/tests/

# Run specific test
pytest app/tests/test_discord.py
```

## 📊 Monitoring

### Logs

Logs are structured and include:

- Request/response details
- User actions
- Error tracking
- Performance metrics

### Health Monitoring

The `/health` endpoint provides:

- Server status
- Discord bot status
- System metrics
- Timestamp information

## 🚀 Deployment

### Development

```bash
python -m app.main
```

### Production

```bash
# Using gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker (create Dockerfile)
docker build -t fastmcp-discord .
docker run -p 8000:8000 fastmcp-discord
```

## 📚 Examples

### Send a Message

```python
import httpx

async def send_discord_message():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/call-tool",
            headers={"X-API-Key": "your_api_key"},
            json={
                "tool_name": "send_message",
                "parameters": {
                    "channel_id": 123456789,
                    "content": "Hello from FastMCP!"
                }
            }
        )
        return response.json()
```

### Search Messages

```python
async def search_messages():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp/call-tool",
            headers={"X-API-Key": "your_api_key"},
            json={
                "tool_name": "search_messages",
                "parameters": {
                    "channel_id": 123456789,
                    "query": "important",
                    "limit": 10
                }
            }
        )
        return response.json()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- Check the [Issues](https://github.com/your-repo/issues) page
- Read the [Documentation](https://docs.fastmcp.com)
- Join our [Discord Community](https://discord.gg/your-server)

## 🔄 Changelog

### v1.0.0

- Initial release
- Full MCP protocol support
- Discord bot integration
- Authentication system
- Comprehensive logging
- Rate limiting
- Health monitoring
