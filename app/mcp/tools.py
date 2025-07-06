"""
MCP tools for Discord operations
"""
from typing import List, Dict, Optional, Any
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from loguru import logger

from ..discord.bot import get_discord_bot
from ..config import get_settings


# Pydantic models for tool inputs
class SendMessageInput(BaseModel):
    """Input schema for sending messages"""
    channel_id: int = Field(..., description="Discord channel ID")
    content: str = Field(..., description="Message content")
    embed: Optional[Dict] = Field(None, description="Optional embed data")


class GetMessagesInput(BaseModel):
    """Input schema for getting messages"""
    channel_id: int = Field(..., description="Discord channel ID")
    limit: int = Field(default=10, description="Number of messages to retrieve", ge=1, le=100)
    before: Optional[int] = Field(None, description="Message ID to get messages before")


class GetChannelInfoInput(BaseModel):
    """Input schema for getting channel info"""
    channel_id: int = Field(..., description="Discord channel ID")


class SearchMessagesInput(BaseModel):
    """Input schema for searching messages"""
    channel_id: int = Field(..., description="Discord channel ID")
    query: str = Field(..., description="Search query")
    limit: int = Field(default=50, description="Maximum number of messages to search", ge=1, le=100)


class DeleteMessageInput(BaseModel):
    """Input schema for deleting messages"""
    channel_id: int = Field(..., description="Discord channel ID")
    message_id: int = Field(..., description="Message ID to delete")


class BanUserInput(BaseModel):
    """Input schema for banning users"""
    guild_id: int = Field(..., description="Discord guild ID")
    user_id: int = Field(..., description="User ID to ban")
    reason: str = Field(default="Banned via MCP", description="Reason for ban")


class KickUserInput(BaseModel):
    """Input schema for kicking users"""
    guild_id: int = Field(..., description="Discord guild ID")
    user_id: int = Field(..., description="User ID to kick")
    reason: str = Field(default="Kicked via MCP", description="Reason for kick")


class GetGuildInfoInput(BaseModel):
    """Input schema for getting guild info"""
    guild_id: int = Field(..., description="Discord guild ID")


def create_discord_tools(mcp: FastMCP) -> FastMCP:
    """Create and register Discord MCP tools"""
    
    @mcp.tool
    async def send_message(input_data: SendMessageInput) -> Dict[str, Any]:
        """
        Send a message to a Discord channel.
        
        This tool allows you to send text messages and embeds to any Discord channel
        that the bot has access to. You can include rich formatting using Discord markdown.
        
        Args:
            input_data: SendMessageInput containing channel_id, content, and optional embed
            
        Returns:
            Dict containing message details including ID, timestamp, and author info
        """
        try:
            bot = await get_discord_bot()
            result = await bot.send_message(
                channel_id=input_data.channel_id,
                content=input_data.content,
                embed=input_data.embed
            )
            
            logger.info(f"Message sent to channel {input_data.channel_id}: {result['message_id']}")
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def get_messages(input_data: GetMessagesInput) -> Dict[str, Any]:
        """
        Retrieve recent messages from a Discord channel.
        
        This tool fetches the most recent messages from a specified channel.
        You can control how many messages to retrieve and paginate through older messages.
        
        Args:
            input_data: GetMessagesInput containing channel_id, limit, and optional before
            
        Returns:
            Dict containing list of messages with full details
        """
        try:
            bot = await get_discord_bot()
            messages = await bot.get_messages(
                channel_id=input_data.channel_id,
                limit=input_data.limit,
                before=input_data.before
            )
            
            logger.info(f"Retrieved {len(messages)} messages from channel {input_data.channel_id}")
            return {
                "success": True,
                "data": {
                    "messages": messages,
                    "count": len(messages)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def get_channel_info(input_data: GetChannelInfoInput) -> Dict[str, Any]:
        """
        Get detailed information about a Discord channel.
        
        This tool retrieves metadata about a channel including its name, type,
        guild information, member count, and channel-specific settings.
        
        Args:
            input_data: GetChannelInfoInput containing channel_id
            
        Returns:
            Dict containing comprehensive channel information
        """
        try:
            bot = await get_discord_bot()
            info = await bot.get_channel_info(input_data.channel_id)
            
            logger.info(f"Retrieved info for channel {input_data.channel_id}: {info['name']}")
            return {
                "success": True,
                "data": info
            }
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def search_messages(input_data: SearchMessagesInput) -> Dict[str, Any]:
        """
        Search for messages in a Discord channel by keyword.
        
        This tool searches through recent messages in a channel to find those
        containing specific keywords or phrases. Case-insensitive search.
        
        Args:
            input_data: SearchMessagesInput containing channel_id, query, and limit
            
        Returns:
            Dict containing matching messages with highlights
        """
        try:
            bot = await get_discord_bot()
            messages = await bot.search_messages(
                channel_id=input_data.channel_id,
                query=input_data.query,
                limit=input_data.limit
            )
            
            logger.info(f"Found {len(messages)} messages matching '{input_data.query}' in channel {input_data.channel_id}")
            return {
                "success": True,
                "data": {
                    "messages": messages,
                    "query": input_data.query,
                    "count": len(messages)
                }
            }
        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def delete_message(input_data: DeleteMessageInput) -> Dict[str, Any]:
        """
        Delete a specific message from a Discord channel.
        
        This tool removes a message from a channel. Requires appropriate permissions.
        This action cannot be undone.
        
        Args:
            input_data: DeleteMessageInput containing channel_id and message_id
            
        Returns:
            Dict indicating success or failure of the deletion
        """
        try:
            bot = await get_discord_bot()
            success = await bot.delete_message(
                channel_id=input_data.channel_id,
                message_id=input_data.message_id
            )
            
            logger.info(f"Deleted message {input_data.message_id} from channel {input_data.channel_id}")
            return {
                "success": True,
                "data": {
                    "deleted": success,
                    "message_id": input_data.message_id,
                    "channel_id": input_data.channel_id
                }
            }
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def ban_user(input_data: BanUserInput) -> Dict[str, Any]:
        """
        Ban a user from a Discord guild.
        
        This tool permanently bans a user from the specified guild.
        Requires ban permissions. This action can be undone by unbanning.
        
        Args:
            input_data: BanUserInput containing guild_id, user_id, and reason
            
        Returns:
            Dict indicating success or failure of the ban
        """
        try:
            bot = await get_discord_bot()
            success = await bot.ban_user(
                guild_id=input_data.guild_id,
                user_id=input_data.user_id,
                reason=input_data.reason
            )
            
            logger.info(f"Banned user {input_data.user_id} from guild {input_data.guild_id}: {input_data.reason}")
            return {
                "success": True,
                "data": {
                    "banned": success,
                    "user_id": input_data.user_id,
                    "guild_id": input_data.guild_id,
                    "reason": input_data.reason
                }
            }
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def kick_user(input_data: KickUserInput) -> Dict[str, Any]:
        """
        Kick a user from a Discord guild.
        
        This tool removes a user from the guild but allows them to rejoin
        if they have an invite. Requires kick permissions.
        
        Args:
            input_data: KickUserInput containing guild_id, user_id, and reason
            
        Returns:
            Dict indicating success or failure of the kick
        """
        try:
            bot = await get_discord_bot()
            success = await bot.kick_user(
                guild_id=input_data.guild_id,
                user_id=input_data.user_id,
                reason=input_data.reason
            )
            
            logger.info(f"Kicked user {input_data.user_id} from guild {input_data.guild_id}: {input_data.reason}")
            return {
                "success": True,
                "data": {
                    "kicked": success,
                    "user_id": input_data.user_id,
                    "guild_id": input_data.guild_id,
                    "reason": input_data.reason
                }
            }
        except Exception as e:
            logger.error(f"Failed to kick user: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @mcp.tool
    async def get_guild_info(input_data: GetGuildInfoInput) -> Dict[str, Any]:
        """
        Get detailed information about a Discord guild.
        
        This tool retrieves comprehensive information about a guild including
        member count, channels, settings, and other metadata.
        
        Args:
            input_data: GetGuildInfoInput containing guild_id
            
        Returns:
            Dict containing comprehensive guild information
        """
        try:
            bot = await get_discord_bot()
            info = await bot.get_guild_info(input_data.guild_id)
            
            logger.info(f"Retrieved info for guild {input_data.guild_id}: {info['name']}")
            return {
                "success": True,
                "data": info
            }
        except Exception as e:
            logger.error(f"Failed to get guild info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    return mcp 