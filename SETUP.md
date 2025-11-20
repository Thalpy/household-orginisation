# Quick Setup Guide

## Step 1: Get Discord Bot Token

1. Go to https://discord.com/developers/applications
2. Click "New Application" → Name it "Household Bot"
3. Go to "Bot" tab → Click "Add Bot"
4. Enable these intents:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Click "Reset Token" → Copy the token (save it!)

## Step 2: Invite Bot to Server

1. Go to "OAuth2" → "URL Generator"
2. Select:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Embed Links`, `Read Message History`
3. Copy the generated URL
4. Open URL in browser → Select your server → Authorize

## Step 3: Setup on Wispbyte

1. Sign up at https://wispbyte.com
2. Create a new server (Node.js/Python)
3. Upload all bot files
4. Create `.env` file with:
   ```
   DISCORD_BOT_TOKEN=paste_your_token_here
   ```
5. Set startup command: `python3 main.py`
6. Start the server!

## Step 4: Test the Bot

In Discord, type:
- `/settings help` - See all commands
- `/todo quick test task` - Add a task
- `/event create` - Create an event

## Optional: Add AI Features

1. Get API key from https://console.anthropic.com/
2. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```
3. Restart bot
4. Try:
   - `/cooking quick dish:Lasagna` - AI generates recipe!
   - `/todo quick buy groceries tomorrow, important` - AI parses it!
   - `/plan day` - AI optimizes your schedule!

## Commands Cheat Sheet

**Events:**
- `/event create` → Create event
- `/event list` → View events

**Cooking:**
- `/cooking quick` → Quick add (AI recipe)
- `/cooking view` → See schedule
- `/cooking view schedule_id:X` → Full recipe

**Todo:**
- `/todo quick <text>` → Quick add (AI parse)
- `/todo list` → View tasks
- `/todo complete <id>` → Mark done

**Planner:**
- `/plan day` → AI daily schedule
- `/plan view` → See your plan

## Troubleshooting

**Commands not showing?**
- Wait 5-10 minutes for Discord to register them
- Kick and re-invite the bot

**Bot offline?**
- Check Wispbyte server status
- Verify `.env` file has correct token
- Check logs for errors

**AI not working?**
- Verify ANTHROPIC_API_KEY in `.env`
- Bot works fine without AI (uses fallbacks)

## Need Help?

Check the full README.md for detailed documentation!
