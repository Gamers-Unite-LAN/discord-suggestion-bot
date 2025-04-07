import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive
from dotenv import load_dotenv

load_dotenv()

# Bot token (replace with your bot token)
TOKEN = os.getenv('TOKEN')

# Server and Channel IDs
GUILD_ID = int(os.getenv('GUILD_ID'))  # Replace this with your server ID
TARGET_CHANNEL_ID = int(os.getenv('TARGET_CHANNEL_ID'))
IGNORED_USER_ID = int(os.getenv('IGNORED_USER_ID'))

# Enable necessary Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Create a bot instance with a command prefix
client = commands.Bot(command_prefix="!", intents=intents, application_commands=True)

@client.event
async def on_ready():
    """Triggered when the bot is successfully connected and ready."""
    print(f'Logged in as {client.user}')
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@client.event
async def on_message(message):
    """Handle messages in source channel and DMs"""
    print(f"Received message from {message.author}: {message.content}")

    # Ignore bot messages and a specific user
    if message.author.bot or message.author.id == IGNORED_USER_ID:
        return
        
    # Handle DMs
    if isinstance(message.channel, discord.DMChannel):
        try:
            target_channel = client.get_channel(TARGET_CHANNEL_ID)
            if target_channel:
                embed = discord.Embed(
                    description=message.content,
                    color=discord.Color.blue(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_author(name=message.author.display_name)
                await target_channel.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())
                
                # Send confirmation to user
                confirm_embed = discord.Embed(
                    description="Your suggestion has been sent to the GUL team! Thank you! ☺️",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=confirm_embed)
            else:
                print(f"Could not find target channel with ID {TARGET_CHANNEL_ID}")

        except Exception as e:
            print(f"Error processing DM: {e}")

# Keep the bot alive if running in a hosted environment
keep_alive()

# Start the bot with graceful shutdown
if __name__ == "__main__":
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print("Bot is shutting down...")
