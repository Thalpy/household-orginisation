"""
AI Helper module using Claude API for intelligent suggestions
Used for: cooking ingredients/instructions, task parsing, smart categorization
"""

import os
import json
import logging
from typing import Optional, Dict, List

logger = logging.getLogger('HouseholdBot.AI')

class AIHelper:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            logger.info("AI Helper enabled with Claude API")
        else:
            logger.info("AI Helper running in fallback mode (no API key)")
    
    async def generate_recipe(self, dish_name: str, servings: int = 4) -> Dict:
        """
        Generate recipe with ingredients and instructions for a dish
        
        Returns:
        {
            'dish_name': str,
            'servings': int,
            'ingredients': List[str],
            'instructions': List[str],
            'prep_time': int (minutes),
            'cook_time': int (minutes)
        }
        """
        if not self.enabled:
            return self._fallback_recipe(dish_name, servings)
        
        try:
            import aiohttp
            
            prompt = f"""Generate a recipe for {dish_name} (serves {servings}).

Return ONLY a JSON object with this exact structure (no markdown, no extra text):
{{
  "dish_name": "{dish_name}",
  "servings": {servings},
  "ingredients": ["ingredient 1 with quantity", "ingredient 2 with quantity", ...],
  "instructions": ["step 1", "step 2", ...],
  "prep_time": <minutes as integer>,
  "cook_time": <minutes as integer>
}}

Make it practical and realistic. Use common ingredients."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-sonnet-4-20250514',
                        'max_tokens': 1500,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }
                ) as response:
                    if response.status != 200:
                        logger.error(f"Claude API error: {response.status}")
                        return self._fallback_recipe(dish_name, servings)
                    
                    data = await response.json()
                    recipe_text = data['content'][0]['text']
                    
                    # Parse JSON from response
                    recipe = json.loads(recipe_text.strip())
                    logger.info(f"Generated recipe for {dish_name}")
                    return recipe
                    
        except Exception as e:
            logger.error(f"Error generating recipe: {e}")
            return self._fallback_recipe(dish_name, servings)
    
    async def suggest_ingredients_from_dish(self, dish_name: str) -> List[str]:
        """Quick ingredient suggestion for a dish name"""
        if not self.enabled:
            return self._fallback_ingredients(dish_name)
        
        try:
            import aiohttp
            
            prompt = f"""List the main ingredients needed for {dish_name}.

Return ONLY a JSON array of ingredient strings with quantities, like:
["2 cups flour", "1 lb chicken", "3 eggs"]

Keep it concise (5-10 main ingredients)."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-sonnet-4-20250514',
                        'max_tokens': 500,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }
                ) as response:
                    if response.status != 200:
                        return self._fallback_ingredients(dish_name)
                    
                    data = await response.json()
                    ingredients_text = data['content'][0]['text']
                    
                    # Parse JSON array
                    ingredients = json.loads(ingredients_text.strip())
                    return ingredients
                    
        except Exception as e:
            logger.error(f"Error suggesting ingredients: {e}")
            return self._fallback_ingredients(dish_name)
    
    async def parse_natural_task(self, task_text: str) -> Dict:
        """
        Parse natural language task into structured format
        Example: "buy groceries tomorrow, should take about an hour, pretty important"
        
        Returns:
        {
            'title': str,
            'description': str,
            'estimated_minutes': int,
            'importance': int (1-5),
            'category': str,
            'due_date': str (YYYY-MM-DD) or None
        }
        """
        if not self.enabled:
            return self._fallback_task_parse(task_text)
        
        try:
            import aiohttp
            from datetime import datetime, timedelta
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            prompt = f"""Parse this task description into structured data: "{task_text}"

Today's date is {today}.

Return ONLY a JSON object:
{{
  "title": "<concise task title>",
  "description": "<optional details or null>",
  "estimated_minutes": <integer, default 30>,
  "importance": <1-5 integer, default 3>,
  "category": "<one of: chore, personal, work, shopping, health, other>",
  "due_date": "<YYYY-MM-DD or null>"
}}

Extract due dates from phrases like "tomorrow", "next week", "by Friday"."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-sonnet-4-20250514',
                        'max_tokens': 300,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }
                ) as response:
                    if response.status != 200:
                        return self._fallback_task_parse(task_text)
                    
                    data = await response.json()
                    task_text = data['content'][0]['text']
                    
                    task_data = json.loads(task_text.strip())
                    logger.info(f"Parsed task: {task_data['title']}")
                    return task_data
                    
        except Exception as e:
            logger.error(f"Error parsing task: {e}")
            return self._fallback_task_parse(task_text)
    
    async def optimize_schedule(self, tasks: List[Dict], available_hours: int = 8) -> List[Dict]:
        """
        AI-optimized task scheduling considering context and task relationships
        
        tasks format: [{'todo_id': int, 'title': str, 'estimated_minutes': int, 'importance': int, 'category': str}, ...]
        
        Returns: [{'todo_id': int, 'start_time': 'HH:MM', 'reasoning': str}, ...]
        """
        if not self.enabled or len(tasks) == 0:
            return self._fallback_schedule(tasks, available_hours)
        
        try:
            import aiohttp
            
            # Format tasks for prompt
            task_list = "\n".join([
                f"- ID {t['todo_id']}: {t['title']} ({t['estimated_minutes']}min, importance: {t['importance']}/5, category: {t.get('category', 'general')})"
                for t in tasks[:15]  # Limit to prevent token overflow
            ])
            
            prompt = f"""You have {available_hours} hours available (09:00 to {9+available_hours}:00).

Schedule these tasks optimally:
{task_list}

Consider:
- Batch similar categories together
- High-importance tasks during peak energy hours
- Include 10% buffer time between tasks
- Don't overpack the schedule

Return ONLY a JSON array:
[
  {{"todo_id": 1, "start_time": "09:00", "reasoning": "brief reason"}},
  ...
]

Only schedule tasks that fit in the available time."""

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'https://api.anthropic.com/v1/messages',
                    headers={
                        'x-api-key': self.api_key,
                        'anthropic-version': '2023-06-01',
                        'content-type': 'application/json',
                    },
                    json={
                        'model': 'claude-sonnet-4-20250514',
                        'max_tokens': 1000,
                        'messages': [
                            {'role': 'user', 'content': prompt}
                        ]
                    }
                ) as response:
                    if response.status != 200:
                        return self._fallback_schedule(tasks, available_hours)
                    
                    data = await response.json()
                    schedule_text = data['content'][0]['text']
                    
                    schedule = json.loads(schedule_text.strip())
                    logger.info(f"AI-optimized schedule for {len(schedule)} tasks")
                    return schedule
                    
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return self._fallback_schedule(tasks, available_hours)
    
    # Fallback methods (no AI)
    
    def _fallback_recipe(self, dish_name: str, servings: int) -> Dict:
        """Fallback recipe generation without AI"""
        return {
            'dish_name': dish_name,
            'servings': servings,
            'ingredients': [
                f"Main ingredients for {dish_name}",
                "Seasonings (salt, pepper, etc.)",
                "Cooking oil/butter as needed"
            ],
            'instructions': [
                "Prepare all ingredients",
                f"Cook {dish_name} according to your preferred method",
                "Season to taste and serve"
            ],
            'prep_time': 15,
            'cook_time': 30
        }
    
    def _fallback_ingredients(self, dish_name: str) -> List[str]:
        """Fallback ingredient list"""
        return [
            f"Main ingredients for {dish_name}",
            "Seasonings (salt, pepper)",
            "Cooking oil"
        ]
    
    def _fallback_task_parse(self, task_text: str) -> Dict:
        """Fallback task parsing"""
        return {
            'title': task_text[:100],
            'description': None,
            'estimated_minutes': 30,
            'importance': 3,
            'category': 'general',
            'due_date': None
        }
    
    def _fallback_schedule(self, tasks: List[Dict], available_hours: int) -> List[Dict]:
        """Fallback scheduling algorithm (simple greedy)"""
        from datetime import datetime, timedelta
        
        schedule = []
        current_time = datetime.strptime('09:00', '%H:%M')
        end_time = current_time + timedelta(hours=available_hours)
        
        # Sort by importance
        sorted_tasks = sorted(tasks, key=lambda x: x.get('importance', 3), reverse=True)
        
        for task in sorted_tasks:
            duration = task.get('estimated_minutes', 30)
            buffer = max(5, int(duration * 0.1))
            
            task_end = current_time + timedelta(minutes=duration + buffer)
            
            if task_end <= end_time:
                schedule.append({
                    'todo_id': task['todo_id'],
                    'start_time': current_time.strftime('%H:%M'),
                    'reasoning': f"Priority task (importance: {task.get('importance', 3)})"
                })
                current_time = task_end
            
            if len(schedule) >= 10:  # Max 10 tasks per day
                break
        
        return schedule
