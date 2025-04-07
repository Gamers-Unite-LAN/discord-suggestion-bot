
import discord
from discord.ext import commands
import asyncio
import os
from keep_alive import keep_alive

# Bot token (replace with your bot token)
TOKEN = os.environ['TOKEN']

# Server and Channel IDs
GUILD_ID = os.environ['GUILD_ID']  # Replace this with your server ID
TARGET_CHANNEL_ID = os.environ['TARGET_CHANNEL_ID']
IGNORED_USER_ID = os.environ['IGNORED_USER_ID']  # User to ignore

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

@client.tree.command(name="suggest", description="Send a suggestion to the GUL team")
async def suggest(interaction: discord.Interaction, suggestion: str):
    """Slash command to send a suggestion"""
    if interaction.guild_id != GUILD_ID:
        embed = discord.Embed(description="This bot can only be used in the authorized server!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
        
    try:
        target_channel = client.get_channel(TARGET_CHANNEL_ID)
        if not target_channel:
            embed = discord.Embed(description="Error: Could not find target channel", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Send suggestion as embed without any text content
        embed = discord.Embed(
            title="New Suggestion",
            description=suggestion,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=interaction.user.display_name)
        await target_channel.send(embed=embed, content=None, allowed_mentions=discord.AllowedMentions.none())

        # Send confirmation
        await interaction.response.send_message("Your suggestion has been sent to the GUL team! Thank you! ☺️", ephemeral=True)

    except Exception as e:
        print(f"Error in slash command: {e}")
        await interaction.response.send_message("An error occurred while processing your suggestion", ephemeral=True)

@client.event
async def on_message(message):
    """Handle messages in source channel and DMs"""
    # Ignore bot messages
    if message.author.bot:
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
                await target_channel.send(embed=embed, content=None, allowed_mentions=discord.AllowedMentions.none())
                
                # Send confirmation to user
                confirm_embed = discord.Embed(description="Your suggestion has been sent to the GUL team! Thank you! ☺️", color=discord.Color.green())
                await message.channel.send(embed=confirm_embed)
        except Exception as e:
            print(f"Error processing DM: {e}")
    
keep_alive()
# Start the bot
client.run(TOKEN)
