# Discord Household Manager Bot

A comprehensive Discord bot for managing household activities, cooking schedules, todo lists, and daily planning with optional AI enhancements.

## Features

### 🎉 Event Planning
- Create household events with automatic reminders
- 24-hour and 1-hour reminder notifications
- Event attendance tracking

### 🍳 Cooking Schedule (AI-Enhanced)
- Schedule cooking duties by meal type
- **AI-generated recipes with ingredients and instructions**
- Automatic cooking reminders 24 hours before
- View detailed recipes with full instructions

### ✅ Todo List (AI-Enhanced)
- Personal task management
- **Natural language task parsing with AI** - e.g., "buy groceries tomorrow, about an hour, important"
- Priority levels (1-5 stars)
- Category organization (chore, personal, work, shopping, health)
- Time estimation tracking

### 📊 Daily/Weekly Planner (AI-Enhanced)
- **AI-optimized schedule generation** considering task importance, categories, and energy levels
- Automatic task batching and time buffering
- Daily and weekly planning views
- Smart task distribution

## AI Features

The bot includes **optional AI integration** using Claude API for:

1. **Recipe Generation**: Full recipes with ingredients and cooking instructions
2. **Task Parsing**: Natural language → structured task data
3. **Smart Scheduling**: Context-aware daily planning with task optimization

**Note**: AI features are optional. Without an API key, the bot uses programmatic fallbacks.

## Installation

### Prerequisites
- Python 3.10+
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))
- (Optional) Anthropic API Key ([Get one here](https://console.anthropic.com/))

### Setup

1. **Clone or download this project**

2. **Install dependencies:**
```bash
pip install -r requirements.txt --break-system-packages
```

3. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` file:
```
DISCORD_BOT_TOKEN=your_discord_bot_token
ANTHROPIC_API_KEY=your_anthropic_key  # Optional
```

4. **Run the bot:**
```bash
python3 main.py
```

## Wispbyte Deployment

Perfect for free 24/7 hosting on Wispbyte:

1. Upload all files to your Wispbyte server
2. Create a `.env` file with your tokens
3. Set startup command: `python3 main.py`
4. Start the server

**Resource Usage:**
- Database: ~10-50MB
- RAM: ~100-150MB
- CPU: Minimal
- Well within Wispbyte's 1GB storage limit

## Commands

### Events
- `/event create` - Create a new household event
- `/event list` - View upcoming events

### Cooking
- `/cooking schedule [date]` - Schedule a meal (with AI recipe generation)
- `/cooking view [date]` - View cooking schedule
- `/cooking view schedule_id:<id>` - View full recipe with instructions
- `/cooking quick` - Quick add with AI ingredients

### Todo
- `/todo add` - Add a task with form
- `/todo quick <task>` - **Quick add with AI parsing** (e.g., "buy milk tomorrow, 15 min, important")
- `/todo list [filter]` - View your tasks
- `/todo complete <id>` - Mark task as complete
- `/todo delete <id>` - Delete a task

### Planner
- `/plan day [date]` - **Generate AI-optimized daily schedule**
- `/plan view [date]` - View your daily plan

### Settings
- `/settings help` - Show all commands

## AI vs Non-AI Modes

### With AI (Anthropic API Key):
✅ Full recipe generation with ingredients and instructions
✅ Natural language task parsing
✅ Context-aware schedule optimization
✅ Smart ingredient suggestions

### Without AI (Fallback Mode):
✅ Basic recipe placeholders
✅ Manual task entry with forms
✅ Simple priority-based scheduling
✅ All core features still work

**Recommendation**: Start without AI to test the bot, add API key later for enhancements.

## Database

Uses SQLite (file-based) - perfect for Wispbyte's constraints:
- `household.db` - stores all data
- Persistent across restarts
- No external database needed
- Auto-creates on first run

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application
3. Go to "Bot" section
4. Click "Add Bot"
5. Enable these Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent
6. Copy the bot token
7. Go to OAuth2 → URL Generator
8. Select scopes: `bot`, `applications.commands`
9. Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
10. Copy the generated URL and invite bot to your server

## Project Structure

```
discord-household-bot/
├── main.py              # Bot initialization
├── database.py          # SQLite operations
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── household.db         # Database (auto-created)
├── cogs/
│   ├── events.py       # Event planning
│   ├── cooking.py      # Cooking schedule (AI recipes)
│   ├── todo.py         # Todo list (AI parsing)
│   ├── planner.py      # Daily planner (AI scheduling)
│   └── settings.py     # Settings & help
└── utils/
    ├── ai_helper.py    # AI integration (Claude API)
    └── scheduler.py    # Reminder system
```

## Reminder System

- **Events**: Automatic 24h and 1h reminders to attendees
- **Cooking**: Daily midnight check creates reminders for next day's cooks
- **Runs every 5 minutes**: Checks for due reminders and sends DMs

## Tips

1. **Start Simple**: Use manual commands first, add AI features later
2. **Sync Commands**: First run might take time for Discord to register slash commands
3. **DM Permissions**: Users must allow DMs from server members for reminders
4. **Categories**: Use consistent categories for better AI scheduling
5. **Time Estimates**: Be realistic with time estimates for better planning

## Troubleshooting

**Bot doesn't respond to commands:**
- Wait 5-10 minutes for Discord to sync commands
- Check bot has proper permissions in channel
- Verify bot token is correct

**AI features not working:**
- Check ANTHROPIC_API_KEY in .env file
- Bot will automatically use fallback mode if key is missing
- Check logs for API errors

**Reminders not sending:**
- User must have DMs enabled from server members
- Check bot is still running
- Verify database has reminders table

**Database errors:**
- Delete `household.db` to reset (loses all data)
- Check file permissions
- Ensure enough disk space

## Contributing

This is a personal household bot. Feel free to fork and modify for your needs!

## License

MIT License - Use freely, modify as needed.

## Support

For issues:
1. Check logs in console
2. Verify environment variables
3. Ensure bot has proper Discord permissions
4. Check Wispbyte server status

---

**Enjoy organizing your household with AI assistance! 🏠✨**
