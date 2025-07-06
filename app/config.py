"""
Configuration management for FastMCP Discord Integration Server
"""
import os
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic BaseSettings"""
    
    # Server Configuration
    app_name: str = Field(default="FastMCP Discord Integration Server", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Discord Configuration
    discord_bot_token: str = Field(default="", description="Discord bot token")
    discord_client_id: Optional[str] = Field(None, description="Discord client ID")
    discord_client_secret: Optional[str] = Field(None, description="Discord client secret")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./discord_mcp.db",
        description="Database connection URL"
    )
    
    # Authentication Configuration
    api_key_secret: str = Field(default="default_secret", description="Secret key for API key generation")
    jwt_secret_key: str = Field(default="default_jwt_secret", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time")
    
    # Rate Limiting Configuration
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # MCP Configuration
    mcp_server_name: str = Field(default="Discord MCP Server", description="MCP server name")
    mcp_server_version: str = Field(default="1.0.0", description="MCP server version")
    mcp_debug: bool = Field(default=False, description="Enable MCP debugging")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", description="Log level")
    log_file: Optional[str] = Field(None, description="Log file path")
    
    # Security Configuration
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins"
    )
    
    # Discord Bot Permissions
    default_permissions: List[str] = Field(
        default=["send_messages", "view_channels", "read_message_history"],
        description="Default bot permissions"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    @validator("discord_bot_token")
    def validate_discord_token(cls, v):
        # Only validate if not empty (allows for testing)
        if v and len(v) < 50:
            raise ValueError("Discord bot token must be valid (at least 50 characters)")
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v):
        if not v:
            raise ValueError("Database URL must be provided")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings


# Environment-specific configurations
class DevelopmentSettings(Settings):
    """Development environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    mcp_debug: bool = True


class ProductionSettings(Settings):
    """Production environment settings"""
    debug: bool = False
    log_level: str = "INFO"
    mcp_debug: bool = False


class TestingSettings(Settings):
    """Testing environment settings"""
    debug: bool = True
    log_level: str = "DEBUG"
    database_url: str = "sqlite:///./test_discord_mcp.db"
    discord_bot_token: str = "test_token_for_testing_only"
    api_key_secret: str = "test_secret"
    jwt_secret_key: str = "test_jwt_secret"


def get_settings_for_env(env: str = None) -> Settings:
    """Get settings for specific environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
