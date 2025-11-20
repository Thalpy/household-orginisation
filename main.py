"""
Discord Household Manager Bot
Main entry point and bot initialization
"""

import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from database import Database
from utils.scheduler import ReminderScheduler
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HouseholdBot')

# Load environment variables
load_dotenv()

class HouseholdBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.db = Database()
        self.scheduler = None
        
    async def setup_hook(self):
        """Called when bot is starting up"""
        # Load all cogs
        cogs = ['cogs.events', 'cogs.cooking', 'cogs.todo', 'cogs.planner', 'cogs.settings']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
        
        # Initialize scheduler
        self.scheduler = ReminderScheduler(self)
        self.scheduler.start()
        logger.info("Reminder scheduler started")
        
        # Sync commands (only in dev, comment out in production)
        # await self.tree.sync()
        
    async def on_ready(self):
        """Called when bot successfully connects to Discord"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="your household 🏠"
            )
        )
        
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        else:
            logger.error(f"Command error: {error}", exc_info=error)
            await ctx.send("❌ An error occurred while processing your command.")

def main():
    """Main entry point"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        return
    
    bot = HouseholdBot()
    
    try:
        bot.run(token, log_handler=None)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=e)

if __name__ == '__main__':
    main()
