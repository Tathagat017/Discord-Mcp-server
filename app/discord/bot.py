"""
Discord bot integration for MCP server
"""
import asyncio
from typing import List, Dict, Optional, Any
import discord
from discord.ext import commands
from loguru import logger

from ..config import get_settings


class DiscordBot:
    """Discord bot wrapper for MCP integration"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = None
        self.is_ready = False
        self.settings = get_settings()
        
        # Bot intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        # Create bot instance
        self.bot = commands.Bot(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        # Setup event handlers
        self.setup_events()
    
    def setup_events(self):
        """Setup Discord bot events"""
        
        @self.bot.event
        async def on_ready():
            logger.info(f"Discord bot logged in as {self.bot.user}")
            self.is_ready = True
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            logger.error(f"Discord bot error in {event}: {args}, {kwargs}")
        
        @self.bot.event
        async def on_command_error(ctx, error):
            logger.error(f"Command error: {error}")
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        if self.bot:
            await self.bot.close()
    
    async def send_message(self, channel_id: int, content: str, embed: Optional[Dict] = None) -> Dict:
        """Send message to a Discord channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            discord_embed = None
            if embed:
                discord_embed = discord.Embed(**embed)
            
            message = await channel.send(content=content, embed=discord_embed)
            
            return {
                "message_id": message.id,
                "channel_id": channel_id,
                "content": content,
                "timestamp": message.created_at.isoformat(),
                "author": {
                    "id": message.author.id,
                    "name": message.author.name,
                    "discriminator": message.author.discriminator
                }
            }
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def get_messages(self, channel_id: int, limit: int = 10, before: Optional[int] = None) -> List[Dict]:
        """Get messages from a Discord channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            before_message = None
            if before:
                before_message = discord.Object(id=before)
            
            messages = []
            async for message in channel.history(limit=limit, before=before_message):
                messages.append({
                    "id": message.id,
                    "content": message.content,
                    "author": {
                        "id": message.author.id,
                        "name": message.author.name,
                        "discriminator": message.author.discriminator,
                        "avatar": str(message.author.avatar) if message.author.avatar else None
                    },
                    "timestamp": message.created_at.isoformat(),
                    "edited_timestamp": message.edited_at.isoformat() if message.edited_at else None,
                    "attachments": [
                        {
                            "id": att.id,
                            "filename": att.filename,
                            "url": att.url,
                            "size": att.size
                        } for att in message.attachments
                    ],
                    "embeds": [embed.to_dict() for embed in message.embeds],
                    "reactions": [
                        {
                            "emoji": str(reaction.emoji),
                            "count": reaction.count
                        } for reaction in message.reactions
                    ]
                })
            
            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            raise
    
    async def get_channel_info(self, channel_id: int) -> Dict:
        """Get information about a Discord channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            info = {
                "id": channel.id,
                "name": channel.name,
                "type": str(channel.type),
                "guild_id": channel.guild.id if hasattr(channel, 'guild') else None,
                "guild_name": channel.guild.name if hasattr(channel, 'guild') else None,
                "created_at": channel.created_at.isoformat(),
                "member_count": len(channel.members) if hasattr(channel, 'members') else None
            }
            
            # Add channel-specific information
            if isinstance(channel, discord.TextChannel):
                info.update({
                    "topic": channel.topic,
                    "nsfw": channel.nsfw,
                    "slowmode_delay": channel.slowmode_delay,
                    "category": channel.category.name if channel.category else None
                })
            elif isinstance(channel, discord.VoiceChannel):
                info.update({
                    "user_limit": channel.user_limit,
                    "bitrate": channel.bitrate,
                    "connected_members": len(channel.members)
                })
            
            return info
        except Exception as e:
            logger.error(f"Failed to get channel info: {e}")
            raise
    
    async def search_messages(self, channel_id: int, query: str, limit: int = 50) -> List[Dict]:
        """Search messages in a Discord channel"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            messages = []
            async for message in channel.history(limit=limit):
                if query.lower() in message.content.lower():
                    messages.append({
                        "id": message.id,
                        "content": message.content,
                        "author": {
                            "id": message.author.id,
                            "name": message.author.name,
                            "discriminator": message.author.discriminator
                        },
                        "timestamp": message.created_at.isoformat(),
                        "url": message.jump_url
                    })
            
            return messages
        except Exception as e:
            logger.error(f"Failed to search messages: {e}")
            raise
    
    async def delete_message(self, channel_id: int, message_id: int) -> bool:
        """Delete a message from Discord"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            message = await channel.fetch_message(message_id)
            await message.delete()
            
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            raise
    
    async def ban_user(self, guild_id: int, user_id: int, reason: str = "Banned via MCP") -> bool:
        """Ban a user from a guild"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise ValueError(f"Guild {guild_id} not found")
            
            user = await self.bot.fetch_user(user_id)
            await guild.ban(user, reason=reason)
            
            return True
        except Exception as e:
            logger.error(f"Failed to ban user: {e}")
            raise
    
    async def kick_user(self, guild_id: int, user_id: int, reason: str = "Kicked via MCP") -> bool:
        """Kick a user from a guild"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise ValueError(f"Guild {guild_id} not found")
            
            member = guild.get_member(user_id)
            if not member:
                raise ValueError(f"Member {user_id} not found in guild")
            
            await member.kick(reason=reason)
            
            return True
        except Exception as e:
            logger.error(f"Failed to kick user: {e}")
            raise
    
    async def get_guild_info(self, guild_id: int) -> Dict:
        """Get information about a Discord guild"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                raise ValueError(f"Guild {guild_id} not found")
            
            return {
                "id": guild.id,
                "name": guild.name,
                "description": guild.description,
                "member_count": guild.member_count,
                "owner_id": guild.owner_id,
                "created_at": guild.created_at.isoformat(),
                "icon": str(guild.icon) if guild.icon else None,
                "banner": str(guild.banner) if guild.banner else None,
                "verification_level": str(guild.verification_level),
                "channels": [
                    {
                        "id": channel.id,
                        "name": channel.name,
                        "type": str(channel.type)
                    } for channel in guild.channels
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get guild info: {e}")
            raise


# Global bot instance
_bot_instance: Optional[DiscordBot] = None


async def get_discord_bot() -> DiscordBot:
    """Get or create Discord bot instance"""
    global _bot_instance
    
    if _bot_instance is None:
        settings = get_settings()
        _bot_instance = DiscordBot(settings.discord_bot_token)
        
        # Start bot in background task
        asyncio.create_task(_bot_instance.start_bot())
        
        # Wait for bot to be ready
        while not _bot_instance.is_ready:
            await asyncio.sleep(0.1)
    
    return _bot_instance


async def shutdown_discord_bot():
    """Shutdown Discord bot"""
    global _bot_instance
    
    if _bot_instance:
        await _bot_instance.stop_bot()
        _bot_instance = None 