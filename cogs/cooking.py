"""
Cooking schedule management cog with AI-generated recipes
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
from utils.ai_helper import AIHelper
import logging

logger = logging.getLogger('HouseholdBot.Cooking')

class CookingScheduleModal(discord.ui.Modal, title='Schedule Cooking'):
    def __init__(self, cook_date, meal_type, cook_id):
        super().__init__()
        self.cook_date = cook_date
        self.meal_type = meal_type
        self.cook_id = cook_id
        
    dish_name = discord.ui.TextInput(
        label='Dish Name',
        placeholder='e.g., Spaghetti Carbonara',
        required=True,
        max_length=100
    )
    
    notes = discord.ui.TextInput(
        label='Notes (optional)',
        placeholder='Any special notes or dietary considerations',
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Get AI helper
        ai_helper = AIHelper()
        
        # Generate recipe with AI
        recipe = await ai_helper.generate_recipe(self.dish_name.value, servings=4)
        
        # Format ingredients and instructions as JSON strings
        import json
        ingredients_json = json.dumps(recipe['ingredients'])
        instructions_json = json.dumps(recipe['instructions'])
        
        # Save to database
        schedule_id = interaction.client.db.add_cooking_schedule(
            cook_date=self.cook_date,
            meal_type=self.meal_type,
            cook_id=self.cook_id,
            dish_name=self.dish_name.value,
            ingredients=ingredients_json,
            instructions=instructions_json,
            notes=self.notes.value
        )
        
        # Create confirmation embed
        embed = discord.Embed(
            title="✅ Cooking Schedule Added",
            description=f"**{self.dish_name.value}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📅 Date", value=self.cook_date, inline=True)
        embed.add_field(name="🍽️ Meal", value=self.meal_type.title(), inline=True)
        embed.add_field(name="👨‍🍳 Cook", value=interaction.user.mention, inline=True)
        
        # Show ingredients
        ingredients_list = "\n".join([f"• {ing}" for ing in recipe['ingredients'][:5]])
        if len(recipe['ingredients']) > 5:
            ingredients_list += f"\n*...and {len(recipe['ingredients']) - 5} more*"
        
        embed.add_field(
            name="🛒 Ingredients (AI Generated)",
            value=ingredients_list,
            inline=False
        )
        
        # Show cooking time
        total_time = recipe.get('prep_time', 15) + recipe.get('cook_time', 30)
        embed.add_field(
            name="⏱️ Estimated Time",
            value=f"{total_time} minutes",
            inline=True
        )
        
        if self.notes.value:
            embed.add_field(name="📝 Notes", value=self.notes.value, inline=False)
        
        embed.set_footer(text=f"Schedule ID: {schedule_id} | Use /cooking view to see full recipe")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Notify channel
        channel = interaction.channel
        if channel:
            notify_embed = discord.Embed(
                title="🍳 New Cooking Schedule",
                description=f"{interaction.user.mention} is cooking **{self.dish_name.value}** on {self.cook_date}",
                color=discord.Color.orange()
            )
            notify_embed.add_field(name="Meal", value=self.meal_type.title(), inline=True)
            notify_embed.add_field(name="Time", value=f"~{total_time} min", inline=True)
            
            await channel.send(embed=notify_embed)

class MealTypeSelect(discord.ui.Select):
    def __init__(self, cook_date):
        self.cook_date = cook_date
        
        options = [
            discord.SelectOption(label='Breakfast', emoji='🍳', value='breakfast'),
            discord.SelectOption(label='Lunch', emoji='🥗', value='lunch'),
            discord.SelectOption(label='Dinner', emoji='🍝', value='dinner'),
            discord.SelectOption(label='Snacks', emoji='🍪', value='snacks'),
        ]
        
        super().__init__(
            placeholder='Select meal type',
            options=options,
            custom_id='meal_type_select'
        )
    
    async def callback(self, interaction: discord.Interaction):
        meal_type = self.values[0]
        
        # Get or create user
        user_id = interaction.client.db.get_or_create_user(
            str(interaction.user.id),
            interaction.user.name
        )
        
        # Show modal for dish details
        modal = CookingScheduleModal(self.cook_date, meal_type, user_id)
        await interaction.response.send_modal(modal)

class Cooking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_helper = AIHelper()
    
    cooking = app_commands.Group(name="cooking", description="Manage cooking schedule")
    
    @cooking.command(name="schedule", description="Schedule a meal to cook")
    @app_commands.describe(date="Date to cook (YYYY-MM-DD) or leave empty for today")
    async def schedule_cooking(self, interaction: discord.Interaction, date: str = None):
        """Schedule a cooking session"""
        
        # Parse date
        if date:
            try:
                cook_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid date format. Use YYYY-MM-DD (e.g., 2024-11-20)",
                    ephemeral=True
                )
                return
        else:
            cook_date = datetime.now().strftime('%Y-%m-%d')
        
        # Create view with meal type selector
        view = discord.ui.View(timeout=300)
        view.add_item(MealTypeSelect(cook_date))
        
        embed = discord.Embed(
            title="📅 Schedule Cooking",
            description=f"**Date:** {cook_date}\n\nSelect the meal type:",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @cooking.command(name="view", description="View cooking schedule")
    @app_commands.describe(
        date="Specific date (YYYY-MM-DD) or leave empty for upcoming",
        schedule_id="Specific schedule ID to view full recipe"
    )
    async def view_schedule(
        self,
        interaction: discord.Interaction,
        date: str = None,
        schedule_id: int = None
    ):
        """View cooking schedule or specific recipe"""
        
        # View specific recipe
        if schedule_id:
            with self.bot.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT cs.*, u.username as cook_name
                    FROM cooking_schedule cs
                    JOIN users u ON cs.cook_id = u.user_id
                    WHERE cs.schedule_id = ?
                ''', (schedule_id,))
                meal = cursor.fetchone()
            
            if not meal:
                await interaction.response.send_message(
                    "❌ Schedule not found",
                    ephemeral=True
                )
                return
            
            # Parse ingredients and instructions
            import json
            ingredients = json.loads(meal['ingredients']) if meal['ingredients'] else []
            instructions = json.loads(meal['instructions']) if meal['instructions'] else []
            
            embed = discord.Embed(
                title=f"🍳 {meal['dish_name']}",
                description=f"**{meal['meal_type'].title()}** on {meal['cook_date']}",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="👨‍🍳 Cook", value=meal['cook_name'], inline=True)
            embed.add_field(name="📅 Date", value=meal['cook_date'], inline=True)
            
            # Ingredients
            if ingredients:
                ingredients_text = "\n".join([f"• {ing}" for ing in ingredients])
                # Split if too long
                if len(ingredients_text) > 1024:
                    embed.add_field(
                        name="🛒 Ingredients (Part 1)",
                        value=ingredients_text[:1024],
                        inline=False
                    )
                    embed.add_field(
                        name="🛒 Ingredients (Part 2)",
                        value=ingredients_text[1024:2048],
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="🛒 Ingredients",
                        value=ingredients_text,
                        inline=False
                    )
            
            # Instructions
            if instructions:
                instructions_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(instructions)])
                # Split if too long
                if len(instructions_text) > 1024:
                    embed.add_field(
                        name="📝 Instructions (Part 1)",
                        value=instructions_text[:1024],
                        inline=False
                    )
                    if len(instructions_text) > 1024:
                        embed.add_field(
                            name="📝 Instructions (Part 2)",
                            value=instructions_text[1024:2048],
                            inline=False
                        )
                else:
                    embed.add_field(
                        name="📝 Instructions",
                        value=instructions_text,
                        inline=False
                    )
            
            if meal['notes']:
                embed.add_field(name="📌 Notes", value=meal['notes'], inline=False)
            
            embed.set_footer(text=f"Schedule ID: {schedule_id}")
            
            await interaction.response.send_message(embed=embed)
            return
        
        # View schedule for date range
        if date:
            try:
                view_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
                meals = self.bot.db.get_cooking_schedule(start_date=view_date)
            except ValueError:
                await interaction.response.send_message(
                    "❌ Invalid date format. Use YYYY-MM-DD",
                    ephemeral=True
                )
                return
        else:
            # Show next 7 days
            meals = self.bot.db.get_cooking_schedule()
        
        if not meals:
            await interaction.response.send_message(
                "📭 No cooking scheduled for this period",
                ephemeral=True
            )
            return
        
        # Create schedule embed
        embed = discord.Embed(
            title="🗓️ Cooking Schedule",
            color=discord.Color.blue()
        )
        
        # Group by date
        from collections import defaultdict
        schedule_by_date = defaultdict(list)
        
        for meal in meals:
            schedule_by_date[meal['cook_date']].append(meal)
        
        for date, day_meals in sorted(schedule_by_date.items())[:7]:
            day_text = []
            for meal in day_meals:
                day_text.append(
                    f"**{meal['meal_type'].title()}**: {meal['dish_name']}\n"
                    f"👨‍🍳 {meal['cook_name']} • ID: {meal['schedule_id']}"
                )
            
            embed.add_field(
                name=date,
                value="\n\n".join(day_text),
                inline=False
            )
        
        embed.set_footer(text="Use /cooking view schedule_id:<ID> to see full recipe")
        
        await interaction.response.send_message(embed=embed)
    
    @cooking.command(name="quick", description="Quick add with AI ingredient suggestion")
    @app_commands.describe(
        dish="Name of the dish",
        date="Date (YYYY-MM-DD)",
        meal="Meal type"
    )
    @app_commands.choices(meal=[
        app_commands.Choice(name="Breakfast", value="breakfast"),
        app_commands.Choice(name="Lunch", value="lunch"),
        app_commands.Choice(name="Dinner", value="dinner"),
        app_commands.Choice(name="Snacks", value="snacks"),
    ])
    async def quick_add(
        self,
        interaction: discord.Interaction,
        dish: str,
        meal: app_commands.Choice[str],
        date: str = None
    ):
        """Quickly add a dish with AI-generated ingredients"""
        
        await interaction.response.defer()
        
        # Parse date
        if date:
            try:
                cook_date = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                await interaction.followup.send(
                    "❌ Invalid date format. Use YYYY-MM-DD",
                    ephemeral=True
                )
                return
        else:
            cook_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get or create user
        user_id = self.bot.db.get_or_create_user(
            str(interaction.user.id),
            interaction.user.name
        )
        
        # Generate recipe with AI
        recipe = await self.ai_helper.generate_recipe(dish, servings=4)
        
        # Save to database
        import json
        schedule_id = self.bot.db.add_cooking_schedule(
            cook_date=cook_date,
            meal_type=meal.value,
            cook_id=user_id,
            dish_name=dish,
            ingredients=json.dumps(recipe['ingredients']),
            instructions=json.dumps(recipe['instructions'])
        )
        
        # Create embed
        embed = discord.Embed(
            title="✅ Cooking Scheduled",
            description=f"**{dish}** for {meal.name}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="📅 Date", value=cook_date, inline=True)
        embed.add_field(name="👨‍🍳 Cook", value=interaction.user.mention, inline=True)
        
        ingredients_preview = "\n".join([f"• {ing}" for ing in recipe['ingredients'][:3]])
        if len(recipe['ingredients']) > 3:
            ingredients_preview += f"\n*...and {len(recipe['ingredients']) - 3} more*"
        
        embed.add_field(
            name="🛒 Ingredients (AI Generated)",
            value=ingredients_preview,
            inline=False
        )
        
        embed.set_footer(text=f"Schedule ID: {schedule_id} | Use /cooking view schedule_id:{schedule_id} for full recipe")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Cooking(bot))
