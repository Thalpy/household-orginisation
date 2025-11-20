# AI Features Documentation

This bot includes **smart AI integration** that enhances the user experience while maintaining programmatic fallbacks.

## Where AI is Used

### 1. 🍳 Cooking - Recipe Generation

**Command**: `/cooking schedule` or `/cooking quick`

**What AI Does:**
- Generates complete recipes from dish names
- Provides realistic ingredient lists with quantities
- Creates step-by-step cooking instructions
- Estimates prep and cooking times

**Example:**
```
User: /cooking quick dish:Chicken Tikka Masala
AI Generates:
- 12 ingredients with exact quantities
- 8-step cooking instructions
- Prep time: 20 min, Cook time: 35 min
```

**Fallback (No AI):**
- Generic ingredient placeholders
- Basic cooking instructions
- User can still manually add details

**Why This Helps:**
- Saves time looking up recipes
- Standardizes recipe format
- Makes meal planning effortless

---

### 2. ✅ Todo - Natural Language Parsing

**Command**: `/todo quick <description>`

**What AI Does:**
- Extracts task title from natural language
- Identifies time estimates ("about an hour" → 60 minutes)
- Determines importance from phrases ("urgent", "important")
- Parses due dates ("tomorrow", "next Friday")
- Auto-categorizes tasks (shopping, chore, work, etc.)

**Example:**
```
User: /todo quick buy groceries tomorrow, should take about an hour, pretty important

AI Parses to:
- Title: "Buy groceries"
- Due Date: 2024-11-21
- Time: 60 minutes
- Importance: 4/5 stars
- Category: Shopping
```

**Fallback (No AI):**
- Uses raw text as title
- Default values (30 min, importance 3, category "general")
- User fills in details manually

**Why This Helps:**
- Faster task entry (one line vs multiple fields)
- Natural way to add tasks
- Captures context from how you phrase things

---

### 3. 📊 Planner - Smart Scheduling

**Command**: `/plan day`

**What AI Does:**
- Analyzes all your pending tasks
- Considers task importance, categories, and time estimates
- Optimizes schedule based on:
  - Energy levels (important tasks early)
  - Task batching (similar categories together)
  - Buffer time between tasks
  - Realistic daily capacity
- Provides reasoning for each scheduling decision

**Example:**
```
User: /plan day

AI Creates:
09:00 - Clean bathroom (30 min)
       💡 High priority task during peak energy hours

10:00 - Buy groceries (60 min)
       💡 Batched with shopping category

11:15 - Call dentist (15 min)
       💡 Quick task, fits perfectly before lunch
```

**Fallback (No AI):**
- Simple greedy algorithm (sorts by importance)
- Still creates a schedule, just less optimized
- No contextual reasoning

**Why This Helps:**
- Better task distribution throughout day
- Considers your actual working patterns
- Reduces decision fatigue
- More realistic schedules

---

## AI Configuration

### API Key Setup

1. Get free API key: https://console.anthropic.com/
2. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. Restart bot

### Cost Considerations

**Anthropic Pricing:**
- Claude Sonnet: $3 per million input tokens, $15 per million output tokens
- Average usage per command:
  - Recipe generation: ~500 tokens (~$0.008)
  - Task parsing: ~200 tokens (~$0.003)
  - Schedule optimization: ~800 tokens (~$0.012)

**Estimated Monthly Cost (Active Household):**
- 30 recipes: ~$0.24
- 50 task parses: ~$0.15
- 25 schedule optimizations: ~$0.30
- **Total: ~$0.70/month**

Very affordable for the convenience!

### Free Tier

Anthropic offers:
- $5 free credits to start
- Covers ~600 AI operations
- Perfect for testing and small households

---

## AI vs Traditional Comparison

| Feature | Traditional Bots | This Bot (with AI) |
|---------|-----------------|-------------------|
| Recipe input | Manual list of ingredients | Full recipe from dish name |
| Task entry | Fill multiple form fields | One natural sentence |
| Scheduling | Basic priority sort | Context-aware optimization |
| Learning curve | Higher | Lower |
| Flexibility | Rigid | Adaptive |

---

## When AI Helps Most

### ✅ Great For:
- **Busy households**: Quick task entry while cooking/working
- **Meal planning**: Instant recipe generation for variety
- **Organization**: Let AI handle the "figuring out" part
- **Consistency**: Standardized formats automatically

### 🤷 Less Important For:
- **Simple tasks**: "Clean kitchen" doesn't need AI parsing
- **Known recipes**: If you have your own recipe, AI isn't needed
- **Manual schedulers**: Some people prefer full control

---

## Privacy & Data

**What gets sent to AI:**
- Dish names (for recipes)
- Task descriptions (for parsing)
- Task metadata (for scheduling)

**What stays local:**
- Your Discord username/ID
- Event details
- Personal notes
- Historical data

**AI Provider:** Anthropic (Claude)
- Highly respected for privacy
- Does not train on user data
- GDPR compliant

---

## Turning AI On/Off

**Enable AI:**
1. Add `ANTHROPIC_API_KEY` to `.env`
2. Restart bot
3. AI features activate automatically

**Disable AI:**
1. Remove `ANTHROPIC_API_KEY` from `.env`
2. Restart bot
3. Fallback methods activate automatically
4. All features still work!

**No configuration changes needed** - bot detects API key presence.

---

## Future AI Enhancements (Ideas)

Potential additions:
- 🤖 **Smart reminders**: "Remind me to buy milk when eggs run low"
- 📊 **Habit analysis**: "You usually grocery shop on Saturdays"
- 🎯 **Goal suggestions**: "You haven't done any health tasks this week"
- 💬 **Natural chat**: Ask questions like "What should I cook with chicken?"
- 🔄 **Task dependencies**: "Schedule A before B automatically"

These could be added later without major changes!

---

## Conclusion

The AI features are designed to be:
- **Optional**: Works great without them
- **Practical**: Solves real problems (not gimmicky)
- **Transparent**: Clear fallbacks, no magic
- **Cost-effective**: Pennies per day
- **Privacy-conscious**: Minimal data sharing

**Recommendation**: Start without AI to learn the bot, add API key after a week to feel the difference!
