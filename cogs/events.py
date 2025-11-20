"""
Event planning cog with reminders
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

class EventModal(discord.ui.Modal, title='Create Event'):
    event_title = discord.ui.TextInput(label='Event Title', required=True, max_length=100)
    description = discord.ui.TextInput(label='Description', required=False, style=discord.TextStyle.paragraph, max_length=500)
    event_date = discord.ui.TextInput(label='Date (YYYY-MM-DD)', placeholder='2024-11-25', required=True)
    event_time = discord.ui.TextInput(label='Time (HH:MM)', placeholder='18:00', required=False)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        user_id = interaction.client.db.get_or_create_user(str(interaction.user.id), interaction.user.name)
        
        event_id = interaction.client.db.create_event(
            title=self.event_title.value,
            description=self.description.value or None,
            event_date=self.event_date.value,
            event_time=self.event_time.value or None,
            created_by=user_id,
            reminder_24h=True,
            reminder_1h=True
        )
        
        # Create reminders
        if self.event_time.value:
            try:
                event_dt = datetime.strptime(f"{self.event_date.value} {self.event_time.value}", '%Y-%m-%d %H:%M')
                interaction.client.scheduler.schedule_event_reminders(event_id, event_dt, True, True)
            except:
                pass
        
        embed = discord.Embed(title="✅ Event Created", description=self.event_title.value, color=discord.Color.green())
        embed.add_field(name="Date", value=self.event_date.value, inline=True)
        if self.event_time.value:
            embed.add_field(name="Time", value=self.event_time.value, inline=True)
        embed.set_footer(text=f"Event ID: {event_id} | Reminders enabled")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    event = app_commands.Group(name="event", description="Manage household events")
    
    @event.command(name="create", description="Create a new event")
    async def create_event(self, interaction: discord.Interaction):
        modal = EventModal()
        await interaction.response.send_modal(modal)
    
    @event.command(name="list", description="View upcoming events")
    async def list_events(self, interaction: discord.Interaction):
        events = self.bot.db.get_upcoming_events(limit=10)
        
        if not events:
            await interaction.response.send_message("📭 No upcoming events", ephemeral=True)
            return
        
        embed = discord.Embed(title="📅 Upcoming Events", color=discord.Color.blue())
        
        for event in events:
            value = f"📅 {event['event_date']}"
            if event['event_time']:
                value += f" at {event['event_time']}"
            value += f"\n👤 Created by {event['creator_name']}"
            
            embed.add_field(name=event['title'], value=value, inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))
