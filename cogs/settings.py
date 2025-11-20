"""
Settings and configuration cog
"""

import discord
from discord import app_commands
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    settings = app_commands.Group(name="settings", description="Bot settings")
    
    @settings.command(name="help", description="Show all available commands")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏠 Household Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📅 Events",
            value="`/event create` - Create new event\n`/event list` - View upcoming events",
            inline=False
        )
        
        embed.add_field(
            name="🍳 Cooking",
            value="`/cooking schedule` - Schedule cooking\n`/cooking view` - View schedule\n`/cooking quick` - Quick add with AI",
            inline=False
        )
        
        embed.add_field(
            name="✅ Todo",
            value="`/todo add` - Add task\n`/todo quick` - Quick add with AI parsing\n`/todo list` - View tasks\n`/todo complete` - Mark complete",
            inline=False
        )
        
        embed.add_field(
            name="📊 Planner",
            value="`/plan day` - AI-optimized daily plan\n`/plan view` - View your plan",
            inline=False
        )
        
        embed.set_footer(text="AI features: Recipe generation, task parsing, smart scheduling")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Settings(bot))
