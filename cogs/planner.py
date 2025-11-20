"""
Daily/Weekly planner with AI-optimized scheduling
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.ai_helper import AIHelper

class Planner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_helper = AIHelper()
    
    plan = app_commands.Group(name="plan", description="Plan your schedule")
    
    @plan.command(name="day", description="Plan your day")
    @app_commands.describe(date="Date (YYYY-MM-DD) or leave empty for today")
    async def plan_day(self, interaction: discord.Interaction, date: str = None):
        await interaction.response.defer(ephemeral=True)
        
        user_id = self.bot.db.get_or_create_user(str(interaction.user.id), interaction.user.name)
        
        plan_date = date if date else datetime.now().strftime('%Y-%m-%d')
        
        # Get pending todos
        todos = self.bot.db.get_todos(user_id, status='pending', limit=20)
        
        if not todos:
            await interaction.followup.send("📭 No pending tasks to schedule", ephemeral=True)
            return
        
        # Convert to dict for AI
        task_list = [
            {
                'todo_id': t['todo_id'],
                'title': t['title'],
                'estimated_minutes': t['estimated_minutes'],
                'importance': t['importance'],
                'category': t['category']
            }
            for t in todos
        ]
        
        # AI-optimized schedule
        schedule = await self.ai_helper.optimize_schedule(task_list, available_hours=8)
        
        # Clear existing plan
        self.bot.db.clear_daily_plan(user_id, plan_date)
        
        # Save schedule
        for item in schedule:
            self.bot.db.schedule_todo(
                user_id=user_id,
                todo_id=item['todo_id'],
                scheduled_date=plan_date,
                scheduled_time=item['start_time'],
                duration_minutes=next(t['estimated_minutes'] for t in task_list if t['todo_id'] == item['todo_id'])
            )
        
        # Create embed
        embed = discord.Embed(
            title=f"📅 Daily Plan - {plan_date}",
            description="AI-optimized schedule:",
            color=discord.Color.purple()
        )
        
        for item in schedule:
            task = next(t for t in task_list if t['todo_id'] == item['todo_id'])
            embed.add_field(
                name=f"{item['start_time']} - {task['title']}",
                value=f"⏱️ {task['estimated_minutes']} min | {'⭐' * task['importance']}\n💡 {item.get('reasoning', 'Scheduled')}",
                inline=False
            )
        
        embed.set_footer(text=f"Scheduled {len(schedule)} tasks")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @plan.command(name="view", description="View your daily plan")
    @app_commands.describe(date="Date (YYYY-MM-DD)")
    async def view_plan(self, interaction: discord.Interaction, date: str = None):
        user_id = self.bot.db.get_or_create_user(str(interaction.user.id), interaction.user.name)
        
        plan_date = date if date else datetime.now().strftime('%Y-%m-%d')
        plan = self.bot.db.get_daily_plan(user_id, plan_date)
        
        if not plan:
            await interaction.response.send_message(f"📭 No plan for {plan_date}", ephemeral=True)
            return
        
        embed = discord.Embed(title=f"📅 Your Plan - {plan_date}", color=discord.Color.blue())
        
        for item in plan:
            embed.add_field(
                name=f"{item['scheduled_time']} - {item['title']}",
                value=f"⏱️ {item['duration_minutes']} min | {'⭐' * item['importance']} | 📁 {item['category'].title()}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Planner(bot))
