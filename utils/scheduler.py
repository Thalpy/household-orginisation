"""
Reminder scheduler using APScheduler
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import logging
import discord

logger = logging.getLogger('HouseholdBot.Scheduler')

class ReminderScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        
        # Add reminder check job (every 5 minutes)
        self.scheduler.add_job(
            self.check_reminders,
            'interval',
            minutes=5,
            id='reminder_check'
        )
        
        # Add cooking reminder job (daily at midnight)
        self.scheduler.add_job(
            self.check_cooking_reminders,
            'cron',
            hour=0,
            minute=0,
            id='cooking_reminder'
        )
        
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")
    
    async def check_reminders(self):
        """Check for due reminders and send them"""
        try:
            current_time = datetime.now().isoformat()
            reminders = self.bot.db.get_due_reminders(current_time)
            
            for reminder in reminders:
                await self.send_reminder(reminder)
                self.bot.db.mark_reminder_sent(reminder['reminder_id'])
                
            if reminders:
                logger.info(f"Sent {len(reminders)} reminders")
                
        except Exception as e:
            logger.error(f"Error checking reminders: {e}")
    
    async def send_reminder(self, reminder):
        """Send a reminder to user"""
        try:
            discord_id = int(reminder['discord_id'])
            user = await self.bot.fetch_user(discord_id)
            
            if not user:
                logger.warning(f"User {discord_id} not found for reminder")
                return
            
            # Create embed based on reminder type
            if reminder['type'] == 'event':
                event = self.bot.db.get_event(reminder['reference_id'])
                if not event:
                    return
                
                embed = discord.Embed(
                    title="🔔 Event Reminder",
                    description=event['title'],
                    color=discord.Color.blue()
                )
                embed.add_field(name="Date", value=event['event_date'], inline=True)
                embed.add_field(name="Time", value=event['event_time'] or "TBD", inline=True)
                
                if event['description']:
                    embed.add_field(name="Details", value=event['description'], inline=False)
                
                embed.set_footer(text=reminder['message'])
                
            elif reminder['type'] == 'cooking':
                from datetime import datetime
                meals = self.bot.db.get_cooking_schedule(
                    start_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                )
                
                if not meals:
                    return
                
                embed = discord.Embed(
                    title="👨‍🍳 Cooking Reminder",
                    description="You're scheduled to cook tomorrow!",
                    color=discord.Color.orange()
                )
                
                for meal in meals:
                    if meal['cook_id'] == reminder['user_id']:
                        embed.add_field(
                            name=f"{meal['meal_type'].title()}",
                            value=f"**Dish:** {meal['dish_name']}\n{reminder['message']}",
                            inline=False
                        )
            
            elif reminder['type'] == 'todo':
                # Future: todo reminders
                return
            
            else:
                # Generic reminder
                embed = discord.Embed(
                    title="🔔 Reminder",
                    description=reminder['message'],
                    color=discord.Color.purple()
                )
            
            await user.send(embed=embed)
            logger.info(f"Sent {reminder['type']} reminder to user {discord_id}")
            
        except discord.Forbidden:
            logger.warning(f"Cannot send DM to user {discord_id} (DMs disabled)")
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    async def check_cooking_reminders(self):
        """Check cooking schedule and create reminders for tomorrow"""
        try:
            from datetime import datetime
            
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            meals = self.bot.db.get_cooking_schedule(start_date=tomorrow)
            
            for meal in meals:
                # Create reminder at 8 AM tomorrow (24h before cooking time)
                trigger_time = f"{tomorrow} 08:00:00"
                
                message = f"Don't forget to prepare ingredients for {meal['dish_name']}!"
                
                self.bot.db.create_reminder(
                    reminder_type='cooking',
                    reference_id=meal['schedule_id'],
                    user_id=meal['cook_id'],
                    trigger_time=trigger_time,
                    message=message
                )
            
            if meals:
                logger.info(f"Created {len(meals)} cooking reminders for {tomorrow}")
                
        except Exception as e:
            logger.error(f"Error creating cooking reminders: {e}")
    
    def schedule_event_reminders(self, event_id, event_datetime, reminder_24h, reminder_1h):
        """Schedule reminders for an event"""
        try:
            # Get event attendees
            attendees = self.bot.db.get_event_attendees(event_id)
            
            if reminder_24h:
                trigger_time = (event_datetime - timedelta(hours=24)).isoformat()
                for attendee in attendees:
                    if attendee['status'] == 'accepted':
                        self.bot.db.create_reminder(
                            reminder_type='event',
                            reference_id=event_id,
                            user_id=attendee['user_id'],
                            trigger_time=trigger_time,
                            message="Event starts in 24 hours"
                        )
            
            if reminder_1h:
                trigger_time = (event_datetime - timedelta(hours=1)).isoformat()
                for attendee in attendees:
                    if attendee['status'] == 'accepted':
                        self.bot.db.create_reminder(
                            reminder_type='event',
                            reference_id=event_id,
                            user_id=attendee['user_id'],
                            trigger_time=trigger_time,
                            message="Event starts in 1 hour"
                        )
            
            logger.info(f"Scheduled reminders for event {event_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling event reminders: {e}")
