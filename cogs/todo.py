"""
Todo list management with AI-enhanced task parsing
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils.ai_helper import AIHelper
import logging

logger = logging.getLogger('HouseholdBot.Todo')

class TodoAddModal(discord.ui.Modal, title='Add Todo Task'):
    title_input = discord.ui.TextInput(
        label='Task Title',
        placeholder='e.g., Buy groceries',
        required=True,
        max_length=100
    )
    
    description = discord.ui.TextInput(
        label='Description (optional)',
        placeholder='Additional details',
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    estimated_time = discord.ui.TextInput(
        label='Estimated Time (minutes)',
        placeholder='30',
        required=False,
        default='30',
        max_length=4
    )
    
    due_date = discord.ui.TextInput(
        label='Due Date (optional)',
        placeholder='YYYY-MM-DD',
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Get or create user
        user_id = interaction.client.db.get_or_create_user(
            str(interaction.user.id),
            interaction.user.name
        )
        
        # Parse estimated time
        try:
            est_minutes = int(self.estimated_time.value) if self.estimated_time.value else 30
        except ValueError:
            est_minutes = 30
        
        # Parse due date
        due = None
        if self.due_date.value:
            try:
                due = datetime.strptime(self.due_date.value, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                pass
        
        # Create todo (default importance 3, category 'general')
        todo_id = interaction.client.db.create_todo(
            user_id=user_id,
            title=self.title_input.value,
            description=self.description.value or None,
            estimated_minutes=est_minutes,
            importance=3,
            category='general',
            due_date=due
        )
        
        # Create embed
        embed = discord.Embed(
            title="✅ Task Added",
            description=self.title_input.value,
            color=discord.Color.green()
        )
        
        embed.add_field(name="⏱️ Time", value=f"{est_minutes} min", inline=True)
        embed.add_field(name="⭐ Importance", value="⭐⭐⭐", inline=True)
        
        if due:
            embed.add_field(name="📅 Due", value=due, inline=True)
        
        embed.set_footer(text=f"Todo ID: #{todo_id}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class ImportanceSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='1 - Low Priority', emoji='⭐', value='1'),
            discord.SelectOption(label='2 - Below Average', emoji='⭐', value='2'),
            discord.SelectOption(label='3 - Normal', emoji='⭐', value='3'),
            discord.SelectOption(label='4 - Important', emoji='⭐', value='4'),
            discord.SelectOption(label='5 - Critical', emoji='⭐', value='5'),
        ]
        
        super().__init__(
            placeholder='Select importance level',
            options=options,
            custom_id='importance_select'
        )
    
    async def callback(self, interaction: discord.Interaction):
        importance = int(self.values[0])
        # Store in view for later use
        self.view.importance = importance
        await interaction.response.send_message(
            f"✅ Importance set to: {'⭐' * importance}",
            ephemeral=True
        )

class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Chore', emoji='🧹', value='chore'),
            discord.SelectOption(label='Personal', emoji='👤', value='personal'),
            discord.SelectOption(label='Work', emoji='💼', value='work'),
            discord.SelectOption(label='Shopping', emoji='🛒', value='shopping'),
            discord.SelectOption(label='Health', emoji='🏥', value='health'),
            discord.SelectOption(label='Other', emoji='📌', value='other'),
        ]
        
        super().__init__(
            placeholder='Select category',
            options=options,
            custom_id='category_select'
        )
    
    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        self.view.category = category
        await interaction.response.send_message(
            f"✅ Category set to: {category.title()}",
            ephemeral=True
        )

class Todo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_helper = AIHelper()
    
    todo = app_commands.Group(name="todo", description="Manage your todo list")
    
    @todo.command(name="add", description="Add a new task")
    async def add_todo(self, interaction: discord.Interaction):
        """Add a new todo task"""
        modal = TodoAddModal()
        await interaction.response.send_modal(modal)
    
    @todo.command(name="quick", description="Quick add task with AI parsing")
    @app_commands.describe(task="Describe your task naturally")
    async def quick_add(self, interaction: discord.Interaction, task: str):
        """Quick add with AI parsing of natural language"""
        
        await interaction.response.defer(ephemeral=True)
        
        # Get or create user
        user_id = self.bot.db.get_or_create_user(
            str(interaction.user.id),
            interaction.user.name
        )
        
        # Parse task with AI
        parsed = await self.ai_helper.parse_natural_task(task)
        
        # Create todo
        todo_id = self.bot.db.create_todo(
            user_id=user_id,
            title=parsed['title'],
            description=parsed.get('description'),
            estimated_minutes=parsed.get('estimated_minutes', 30),
            importance=parsed.get('importance', 3),
            category=parsed.get('category', 'general'),
            due_date=parsed.get('due_date')
        )
        
        # Create embed
        embed = discord.Embed(
            title="✅ Task Added (AI Parsed)",
            description=parsed['title'],
            color=discord.Color.green()
        )
        
        if parsed.get('description'):
            embed.add_field(name="Details", value=parsed['description'], inline=False)
        
        embed.add_field(
            name="⏱️ Time",
            value=f"{parsed.get('estimated_minutes', 30)} min",
            inline=True
        )
        embed.add_field(
            name="⭐ Importance",
            value='⭐' * parsed.get('importance', 3),
            inline=True
        )
        embed.add_field(
            name="📁 Category",
            value=parsed.get('category', 'general').title(),
            inline=True
        )
        
        if parsed.get('due_date'):
            embed.add_field(name="📅 Due", value=parsed['due_date'], inline=True)
        
        embed.set_footer(text=f"Todo ID: #{todo_id} | AI extracted details from your input")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @todo.command(name="list", description="View your todo list")
    @app_commands.describe(filter="Filter by status")
    @app_commands.choices(filter=[
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Completed", value="completed"),
        app_commands.Choice(name="All", value="all"),
    ])
    async def list_todos(
        self,
        interaction: discord.Interaction,
        filter: app_commands.Choice[str] = None
    ):
        """List your todos"""
        
        # Get or create user
        user_id = self.bot.db.get_or_create_user(
            str(interaction.user.id),
            interaction.user.name
        )
        
        status = filter.value if filter else 'pending'
        todos = self.bot.db.get_todos(user_id, status=status, limit=20)
        
        if not todos:
            await interaction.response.send_message(
                f"📭 No {status} tasks found",
                ephemeral=True
            )
            return
        
        # Create embed
        embed = discord.Embed(
            title=f"📋 Your Tasks ({status.title()})",
            color=discord.Color.blue()
        )
        
        for todo in todos[:10]:  # Show first 10
            importance_stars = '⭐' * todo['importance']
            
            value = f"⏱️ {todo['estimated_minutes']} min | 📁 {todo['category'].title()}"
            if todo['due_date']:
                value += f" | 📅 Due: {todo['due_date']}"
            if todo['completed_at']:
                value += f" | ✅ Completed"
            
            embed.add_field(
                name=f"{importance_stars} #{todo['todo_id']} {todo['title']}",
                value=value,
                inline=False
            )
        
        if len(todos) > 10:
            embed.set_footer(text=f"Showing 10 of {len(todos)} tasks")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @todo.command(name="complete", description="Mark a task as complete")
    @app_commands.describe(todo_id="Task ID to complete")
    async def complete_todo(self, interaction: discord.Interaction, todo_id: int):
        """Complete a todo"""
        
        self.bot.db.update_todo_status(todo_id, 'completed')
        
        await interaction.response.send_message(
            f"✅ Task #{todo_id} marked as complete!",
            ephemeral=True
        )
    
    @todo.command(name="delete", description="Delete a task")
    @app_commands.describe(todo_id="Task ID to delete")
    async def delete_todo(self, interaction: discord.Interaction, todo_id: int):
        """Delete a todo"""
        
        self.bot.db.delete_todo(todo_id)
        
        await interaction.response.send_message(
            f"🗑️ Task #{todo_id} deleted",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Todo(bot))
