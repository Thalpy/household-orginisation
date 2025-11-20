"""
Database module for SQLite operations
"""

import sqlite3
import json
from datetime import datetime, date
from contextlib import contextmanager
import logging

logger = logging.getLogger('HouseholdBot.Database')

class Database:
    def __init__(self, db_path='household.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database with schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    timezone TEXT DEFAULT 'UTC',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    event_date TEXT NOT NULL,
                    event_time TEXT,
                    created_by INTEGER,
                    reminder_24h BOOLEAN DEFAULT 1,
                    reminder_1h BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(user_id)
                )
            ''')
            
            # Event attendees
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_attendees (
                    event_id INTEGER,
                    user_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    responded_at TEXT,
                    PRIMARY KEY (event_id, user_id),
                    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Cooking schedule
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cooking_schedule (
                    schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cook_date TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    cook_id INTEGER,
                    dish_name TEXT,
                    ingredients TEXT,
                    instructions TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cook_id) REFERENCES users(user_id)
                )
            ''')
            
            # Todo items
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    todo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    estimated_minutes INTEGER DEFAULT 30,
                    importance INTEGER CHECK(importance BETWEEN 1 AND 5) DEFAULT 3,
                    category TEXT DEFAULT 'general',
                    status TEXT DEFAULT 'pending',
                    due_date TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Planner (scheduled tasks)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planner (
                    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    todo_id INTEGER,
                    scheduled_date TEXT NOT NULL,
                    scheduled_time TEXT NOT NULL,
                    duration_minutes INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (todo_id) REFERENCES todos(todo_id) ON DELETE CASCADE
                )
            ''')
            
            # Reminders queue
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    reference_id INTEGER NOT NULL,
                    user_id INTEGER,
                    trigger_time TEXT NOT NULL,
                    message TEXT,
                    sent BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            logger.info("Database initialized successfully")
    
    # User operations
    def get_or_create_user(self, discord_id, username):
        """Get existing user or create new one"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Try to get existing user
            cursor.execute(
                'SELECT user_id FROM users WHERE discord_id = ?',
                (str(discord_id),)
            )
            result = cursor.fetchone()
            
            if result:
                return result['user_id']
            
            # Create new user
            cursor.execute(
                'INSERT INTO users (discord_id, username) VALUES (?, ?)',
                (str(discord_id), username)
            )
            return cursor.lastrowid
    
    def get_user_by_discord_id(self, discord_id):
        """Get user by Discord ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE discord_id = ?',
                (str(discord_id),)
            )
            return cursor.fetchone()
    
    # Event operations
    def create_event(self, title, description, event_date, event_time, created_by, reminder_24h=True, reminder_1h=True):
        """Create a new event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (title, description, event_date, event_time, created_by, reminder_24h, reminder_1h)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, event_date, event_time, created_by, reminder_24h, reminder_1h))
            return cursor.lastrowid
    
    def get_upcoming_events(self, limit=10):
        """Get upcoming events"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT e.*, u.username as creator_name
                FROM events e
                JOIN users u ON e.created_by = u.user_id
                WHERE e.event_date >= date('now')
                ORDER BY e.event_date, e.event_time
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    
    def get_event(self, event_id):
        """Get specific event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM events WHERE event_id = ?', (event_id,))
            return cursor.fetchone()
    
    def add_event_attendee(self, event_id, user_id, status='pending'):
        """Add attendee to event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO event_attendees (event_id, user_id, status, responded_at)
                VALUES (?, ?, ?, ?)
            ''', (event_id, user_id, status, datetime.now().isoformat()))
    
    def get_event_attendees(self, event_id):
        """Get all attendees for an event"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ea.*, u.username, u.discord_id
                FROM event_attendees ea
                JOIN users u ON ea.user_id = u.user_id
                WHERE ea.event_id = ?
            ''', (event_id,))
            return cursor.fetchall()
    
    # Cooking operations
    def add_cooking_schedule(self, cook_date, meal_type, cook_id, dish_name, ingredients=None, instructions=None, notes=None):
        """Add cooking schedule entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO cooking_schedule (cook_date, meal_type, cook_id, dish_name, ingredients, instructions, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cook_date, meal_type, cook_id, dish_name, ingredients, instructions, notes))
            return cursor.lastrowid
    
    def get_cooking_schedule(self, start_date=None, end_date=None):
        """Get cooking schedule for date range"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute('''
                    SELECT cs.*, u.username as cook_name, u.discord_id
                    FROM cooking_schedule cs
                    JOIN users u ON cs.cook_id = u.user_id
                    WHERE cs.cook_date BETWEEN ? AND ?
                    ORDER BY cs.cook_date, cs.meal_type
                ''', (start_date, end_date))
            elif start_date:
                cursor.execute('''
                    SELECT cs.*, u.username as cook_name, u.discord_id
                    FROM cooking_schedule cs
                    JOIN users u ON cs.cook_id = u.user_id
                    WHERE cs.cook_date = ?
                    ORDER BY cs.meal_type
                ''', (start_date,))
            else:
                cursor.execute('''
                    SELECT cs.*, u.username as cook_name, u.discord_id
                    FROM cooking_schedule cs
                    JOIN users u ON cs.cook_id = u.user_id
                    WHERE cs.cook_date >= date('now')
                    ORDER BY cs.cook_date, cs.meal_type
                    LIMIT 20
                ''')
            
            return cursor.fetchall()
    
    # Todo operations
    def create_todo(self, user_id, title, description=None, estimated_minutes=30, importance=3, category='general', due_date=None):
        """Create a new todo item"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO todos (user_id, title, description, estimated_minutes, importance, category, due_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, estimated_minutes, importance, category, due_date))
            return cursor.lastrowid
    
    def get_todos(self, user_id, status='pending', limit=50):
        """Get user's todos"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if status == 'all':
                cursor.execute('''
                    SELECT * FROM todos
                    WHERE user_id = ?
                    ORDER BY importance DESC, due_date ASC, created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM todos
                    WHERE user_id = ? AND status = ?
                    ORDER BY importance DESC, due_date ASC, created_at DESC
                    LIMIT ?
                ''', (user_id, status, limit))
            
            return cursor.fetchall()
    
    def update_todo_status(self, todo_id, status):
        """Update todo status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            completed_at = datetime.now().isoformat() if status == 'completed' else None
            cursor.execute('''
                UPDATE todos
                SET status = ?, completed_at = ?
                WHERE todo_id = ?
            ''', (status, completed_at, todo_id))
    
    def delete_todo(self, todo_id):
        """Delete a todo"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM todos WHERE todo_id = ?', (todo_id,))
    
    # Planner operations
    def schedule_todo(self, user_id, todo_id, scheduled_date, scheduled_time, duration_minutes):
        """Schedule a todo in the planner"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO planner (user_id, todo_id, scheduled_date, scheduled_time, duration_minutes)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, todo_id, scheduled_date, scheduled_time, duration_minutes))
            return cursor.lastrowid
    
    def get_daily_plan(self, user_id, plan_date):
        """Get scheduled tasks for a specific date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.*, t.title, t.description, t.importance, t.category
                FROM planner p
                JOIN todos t ON p.todo_id = t.todo_id
                WHERE p.user_id = ? AND p.scheduled_date = ?
                ORDER BY p.scheduled_time
            ''', (user_id, plan_date))
            return cursor.fetchall()
    
    def clear_daily_plan(self, user_id, plan_date):
        """Clear all scheduled tasks for a date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM planner
                WHERE user_id = ? AND scheduled_date = ?
            ''', (user_id, plan_date))
    
    # Reminder operations
    def create_reminder(self, reminder_type, reference_id, user_id, trigger_time, message):
        """Create a reminder"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (type, reference_id, user_id, trigger_time, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (reminder_type, reference_id, user_id, trigger_time, message))
            return cursor.lastrowid
    
    def get_due_reminders(self, current_time):
        """Get reminders that should be sent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT r.*, u.discord_id
                FROM reminders r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.sent = 0 AND r.trigger_time <= ?
            ''', (current_time,))
            return cursor.fetchall()
    
    def mark_reminder_sent(self, reminder_id):
        """Mark reminder as sent"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE reminders
                SET sent = 1
                WHERE reminder_id = ?
            ''', (reminder_id,))
