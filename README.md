#ReadMe writen by AI
# Study Buddy Discord Bot 📚

A feature-rich Discord bot to help students track their study sessions, maintain streaks, manage to-do lists, and stay motivated!

## Features ✨

### ⏰ Study Timers
- **Pomodoro Timer** - Customizable work/break sessions (default: 25min work, 5min break)
- **Custom Schedules** - Create multi-cycle study sessions
- **Study Reminders** - Get reminded to study after X minutes

### 🔥 Progress Tracking
- **Daily Streaks** - Track consecutive study days
- **Study Sessions** - Log manual or automatic study sessions
- **Points & Ranks** - Earn points and climb through ranks (Beginner → Student → Scholar → Expert → Master → Legend)

### 📊 Statistics
- **Leaderboard** - See top 10 students by points
- **Weekly Reports** - View your last 7 days of studying
- **Goal Tracking** - Set daily goals and monitor progress

### 📝 Productivity Tools
- **To-Do Lists** - Add, view, complete, and clear tasks
- **Study Partner Matching** - Find other students to study with
- **Motivational Quotes** - Get random motivation when you need it

### 🎯 Customization
- **Daily Reminders** - Optional DM reminders to study
- **Custom Goals** - Set personalized daily study targets
- **Subject Tracking** - Log sessions by subject

## Commands 🎮

Both `!` (prefix) and `/` (slash) commands are supported!

### Basic Commands
- `!motivate` / `/motivate` - Get a motivational quote
- `!help` / `/help` - Show all available commands

### Study Tracking
- `!studied` / `/studied` - Log that you studied today (+10 points)
- `!streak` / `/streak` - View your current study streak
- `!logsession <minutes> [subject]` / `/logsession` - Manually log a study session

### Timers
- `!remindme <minutes>` / `/remindme` - Set a study reminder
- `!pomodoro [work_min] [break_min]` / `/pomodoro` - Start Pomodoro timer (default: 25/5)
- `!schedule <work> <break> <cycles>` - Create custom study schedule

### Stats & Progress
- `!points` / `/points` - View your points and rank
- `!leaderboard` / `/leaderboard` - See top 10 students
- `!weeklyreport` / `/weeklyreport` - Get your weekly summary

### To-Do List
- `!addtodo <task>` / `/addtodo` - Add a task
- `!listtodo` / `/listtodo` - View all tasks
- `!donetodo <number>` / `/donetodo` - Mark task complete (+5 points)
- `!cleartodo` / `/cleartodo` - Clear all tasks

### Goals & Social
- `!setgoal <minutes>` / `/setgoal` - Set daily study goal
- `!goalcheck` / `/goalcheck` - Check goal progress
- `!findpartner` / `/findpartner` - Get matched with a study buddy
- `!dailyreminder on/off` - Toggle daily DM reminders

## Installation 🚀

### Prerequisites
- Python 3.8 or higher (3.12 recommended, NOT 3.13+)
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

### Setup Steps

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/study-buddy-bot.git
cd study-buddy-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

4. **Run the bot**
```bash
python bot.py
```

## Discord Bot Setup 🤖

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and create a bot
4. Enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
5. Go to OAuth2 → URL Generator
6. Select scopes:
   - ✅ bot
   - ✅ applications.commands
7. Select permissions (or use Administrator for simplicity)
8. Copy the generated URL and invite the bot to your server

## File Structure 📁

```
study-buddy-bot/
├── bot.py                 # Main bot code
├── .env                   # Environment variables (DO NOT COMMIT)
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── streaks.json          # User streak data
├── points.json           # User points data
├── sessions.json         # Study session logs
├── todos.json            # User to-do lists
└── reminders.json        # User reminder settings
```

## Deployment 🌐

### Option 1: Railway.app (Recommended)
1. Fork this repository
2. Sign up at [Railway.app](https://railway.app)
3. Create new project → Deploy from GitHub
4. Add environment variable: `DISCORD_TOKEN`
5. Deploy!

### Option 2: Render.com
1. Fork this repository
2. Sign up at [Render.com](https://render.com)
3. Create new Web Service
4. Connect your GitHub repository
5. Add environment variable: `DISCORD_TOKEN`
6. Deploy!

### Option 3: Self-Hosting
Keep your computer running with the bot, or use a VPS/cloud server.

## Technologies Used 💻

- **discord.py 2.6+** - Discord API wrapper
- **Python 3.12** - Programming language
- **asyncio** - Asynchronous programming
- **JSON** - Data storage

## Rank System 🏆

Earn points by studying and climb through the ranks:
- 📗 Beginner (0-49 points)
- 📘 Student (50-149 points)
- 📙 Scholar (150-299 points)
- 📕 Expert (300-499 points)
- 🏆 Master (500-999 points)
- 👑 Legend (1000+ points)

### How to Earn Points
- Daily study log: 10 points + streak bonus
- Pomodoro session: Points = work minutes
- Manual session log: Points = minutes logged
- Complete a task: 5 points

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support ⭐

If you find this bot helpful, please give it a star ⭐ on GitHub!

## Author 👨‍💻

Created with ❤️ for students who want to stay motivated and track their study progress.

---

**Note:** This bot stores data locally in JSON files. For production use, consider implementing a proper database (PostgreSQL, MongoDB, etc.).
