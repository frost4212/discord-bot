import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import random
from collections import defaultdict

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Track if bot is ready
bot_ready = False

# Load & save functions for streaks
def load_streaks():
    try:
        with open("Discord bot/streaks.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_streaks(data):
    with open("Discord bot/streaks.json", "w") as f:
        json.dump(data, f, indent=4)

# Load & save functions for study points
def load_points():
    try:
        with open("Discord bot/points.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_points(data):
    with open("Discord bot/points.json", "w") as f:
        json.dump(data, f, indent=4)

# Load & save functions for todo lists
def load_todos():
    try:
        with open("Discord bot/todos.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_todos(data):
    with open("Discord bot/todos.json", "w") as f:
        json.dump(data, f, indent=4)

# Load & save functions for study sessions
def load_sessions():
    try:
        with open("Discord bot/sessions.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_sessions(data):
    with open("Discord bot/sessions.json", "w") as f:
        json.dump(data, f, indent=4)

# Load & save functions for daily reminders
def load_reminders():
    try:
        with open("Discord bot/reminders.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_reminders(data):
    with open("Discord bot/reminders.json", "w") as f:
        json.dump(data, f, indent=4)

# Motivation quotes
quotes = [
    "🌟 Keep going — progress is progress!",
    "📚 One page at a time.",
    "💪 You're stronger than you think!",
    "🚀 Small steps lead to big results.",
    "🔥 Your future self will thank you.",
    "✨ Consistency beats perfection!",
    "🎯 Focus on progress, not perfection.",
    "💡 Every expert was once a beginner.",
    "🌈 Believe in yourself!",
    "⚡ You've got this!"
]

# Rank system based on points (harder progression)
def get_rank(points):
    if points < 100:
        return "📗 Novice"
    elif points < 250:
        return "📘 Beginner"
    elif points < 500:
        return "📙 Apprentice"
    elif points < 1000:
        return "📕 Student"
    elif points < 2000:
        return "🟦 Scholar"
    elif points < 3500:
        return "🟧 Expert"
    elif points < 5000:
        return "🟪 Specialist"
    elif points < 7500:
        return "🏆 Master"
    elif points < 10000:
        return "💎 Grandmaster"
    elif points < 15000:
        return "👑 Legend"
    elif points < 25000:
        return "⭐ Elite"
    else:
        return "🌟 Mythic"

# Study partners waiting list
study_partners = []

@bot.event
async def on_ready():
    global bot_ready
    if bot_ready:
        return
    bot_ready = True
    print(f"Study Buddy is online as {bot.user}")
    if not daily_reminder.is_running():
        daily_reminder.start()
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)

# Daily reminder task
@tasks.loop(hours=24)
async def daily_reminder():
    reminders = load_reminders()
    for user_id, data in reminders.items():
        if data.get("enabled", False):
            user = await bot.fetch_user(int(user_id))
            await user.send(f"📚 Good morning! Don't forget to study today. Use `!studied` to log your progress!")

@daily_reminder.before_loop
async def before_daily_reminder():
    await bot.wait_until_ready()

# PHASE 3 — Study Reminder Command
@bot.command(name='remindme', help='Set a study reminder', brief='Remind you to study after X minutes')
async def remindme(ctx, minutes: int):
    """Set a reminder to study. Usage: !remindme 30"""
    if minutes > 1440:
        return await ctx.send("⚠️ Please set a reminder for less than 24 hours (1440 minutes).")
    await ctx.send(f"⏳ Okay! I'll remind you in {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await ctx.send(f"⏰ {ctx.author.mention} Time to study!")

# PHASE 4 — Pomodoro Study Session (with customization)
@bot.command(name='pomodoro', help='Start a Pomodoro study session', brief='25min work + 5min break (customizable)')
async def pomodoro(ctx, work_min: int = 25, break_min: int = 5):
    """Start a Pomodoro timer. Usage: !pomodoro or !pomodoro 50 10"""
    if work_min > 120 or break_min > 60:
        return await ctx.send("⚠️ Work time max: 120 min, Break time max: 60 min")
    
    await ctx.send(f"🍅 **Pomodoro started!** {work_min} minutes of focus begins now!")
    
    # Award points for starting session
    points = load_points()
    user = str(ctx.author.id)
    points[user] = points.get(user, 0) + work_min
    save_points(points)
    
    # Log session
    sessions = load_sessions()
    if user not in sessions:
        sessions[user] = []
    sessions[user].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": work_min,
        "type": "pomodoro"
    })
    save_sessions(sessions)
    
    await asyncio.sleep(work_min * 60)
    await ctx.send(f"🧘 **Break time!** Take {break_min} minutes to relax.")
    await asyncio.sleep(break_min * 60)
    await ctx.send("🚀 Break over! Ready for another session?")

# PHASE 5 — Daily Study Streak Tracking
@bot.command(name='studied', help='Log that you studied today', brief='Track daily study streak')
async def studied(ctx):
    """Log your daily study session. Usage: !studied"""
    streaks = load_streaks()
    points = load_points()
    user = str(ctx.author.id)
    today = datetime.now().strftime("%Y-%m-%d")

    if user not in streaks:
        streaks[user] = {"last_day": today, "streak": 1}
        points[user] = points.get(user, 0) + 10
        save_streaks(streaks)
        save_points(points)
        return await ctx.send("🔥 First day tracked! +10 points! Keep it going!")

    if streaks[user]["last_day"] == today:
        return await ctx.send("✔ You already logged study for today!")

    # Check if streak continues or breaks
    last_date = datetime.strptime(streaks[user]["last_day"], "%Y-%m-%d")
    if (datetime.now() - last_date).days == 1:
        streaks[user]["streak"] += 1
        bonus = streaks[user]["streak"] * 2
        points[user] = points.get(user, 0) + 10 + bonus
        save_streaks(streaks)
        save_points(points)
        await ctx.send(f"🔥 Study logged! You're on a **{streaks[user]['streak']} day streak!** (+{10 + bonus} points)")
    else:
        streaks[user]["streak"] = 1
        points[user] = points.get(user, 0) + 10
        save_points(points)
        await ctx.send("📘 Streak broken, but don't give up! Starting fresh. (+10 points)")
    
    streaks[user]["last_day"] = today
    save_streaks(streaks)

@bot.command(name='streak', help='View your current study streak', brief='See your streak count')
async def streak(ctx):
    """Check your study streak. Usage: !streak"""
    streaks = load_streaks()
    user = str(ctx.author.id)

    if user not in streaks:
        return await ctx.send("📘 No streak yet. Use `!studied` to start!")

    await ctx.send(f"📚 Your current streak: **{streaks[user]['streak']} days**")

# PHASE 6 — Motivation Messages
@bot.command(name='motivate', help='Get a motivational quote', brief='Boost your motivation')
async def motivate(ctx):
    """Get a random motivational message. Usage: !motivate"""
    await ctx.send(random.choice(quotes))

# ADVANCED FEATURE 1 — Study Leaderboard
@bot.command(name='leaderboard', help='View the top 10 students', brief='Top 10 leaderboard')
async def leaderboard(ctx):
    """See the top 10 students by points. Usage: !leaderboard"""
    points = load_points()
    if not points:
        return await ctx.send("📊 No one has earned points yet!")
    
    sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Study Leaderboard", color=discord.Color.gold())
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, pts) in enumerate(sorted_users):
        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[i] if i < 3 else f"#{i+1}"
            rank = get_rank(pts)
            embed.add_field(
                name=f"{medal} {user.name}",
                value=f"{rank} — {pts} points",
                inline=False
            )
        except:
            pass
    
    await ctx.send(embed=embed)

# ADVANCED FEATURE 2 — Points and Rank System
@bot.command(name='points', help='View your points and rank', brief='Check your stats')
async def points(ctx):
    """See your total points and current rank. Usage: !points"""
    points = load_points()
    user = str(ctx.author.id)
    pts = points.get(user, 0)
    rank = get_rank(pts)
    
    embed = discord.Embed(title="📊 Your Stats", color=discord.Color.blue())
    embed.add_field(name="Points", value=f"⭐ {pts}", inline=True)
    embed.add_field(name="Rank", value=rank, inline=True)
    
    await ctx.send(embed=embed)

# ADVANCED FEATURE 3 — Daily Reminder Toggle
@bot.command(name='dailyreminder', help='Toggle daily study reminders', brief='Enable/disable daily DM reminders')
async def dailyreminder(ctx, status: str = "on"):
    """Enable or disable daily reminders. Usage: !dailyreminder on/off"""
    reminders = load_reminders()
    user = str(ctx.author.id)
    
    if status.lower() == "on":
        reminders[user] = {"enabled": True}
        save_reminders(reminders)
        await ctx.send("✅ Daily reminders enabled! I'll DM you every day to study.")
    elif status.lower() == "off":
        reminders[user] = {"enabled": False}
        save_reminders(reminders)
        await ctx.send("🔕 Daily reminders disabled.")
    else:
        await ctx.send("⚠️ Use `!dailyreminder on` or `!dailyreminder off`")

# ADVANCED FEATURE 4 — Custom Study Schedule
@bot.command(name='schedule', help='Create a custom study schedule', brief='Multiple study cycles')
async def schedule(ctx, work_min: int, break_min: int, cycles: int):
    """Create a custom study schedule. Usage: !schedule 25 5 4"""
    if cycles > 10:
        return await ctx.send("⚠️ Maximum 10 cycles allowed!")
    
    await ctx.send(f"📅 **Custom Schedule Started!**\n{cycles} cycles of {work_min}min work + {break_min}min break")
    
    for i in range(cycles):
        await ctx.send(f"🍅 **Cycle {i+1}/{cycles}** — {work_min} minutes of focus starts now!")
        await asyncio.sleep(work_min * 60)
        
        if i < cycles - 1:
            await ctx.send(f"🧘 Break time! {break_min} minutes.")
            await asyncio.sleep(break_min * 60)
    
    # Award points
    points = load_points()
    user = str(ctx.author.id)
    total_points = work_min * cycles
    points[user] = points.get(user, 0) + total_points
    save_points(points)
    
    await ctx.send(f"🎉 Schedule complete! +{total_points} points earned!")

# ADVANCED FEATURE 5 — Study Partner Pairing
@bot.command(name='findpartner', help='Find a study partner', brief='Get matched with another student')
async def findpartner(ctx):
    """Get matched with a study partner. Usage: !findpartner"""
    user_id = ctx.author.id
    
    if user_id in study_partners:
        return await ctx.send("⏳ You're already in the queue!")
    
    if len(study_partners) > 0:
        partner_id = study_partners.pop(0)
        partner = await bot.fetch_user(partner_id)
        
        await ctx.send(f"🤝 Match found! {ctx.author.mention} ↔️ {partner.mention}")
        await partner.send(f"🤝 Study partner found! You've been matched with {ctx.author.name}")
        await ctx.author.send(f"🤝 Study partner found! You've been matched with {partner.name}")
    else:
        study_partners.append(user_id)
        await ctx.send("🔍 Added to partner queue! Waiting for a match...")

# ADVANCED FEATURE 6 — To-Do List System
@bot.command(name='addtodo', help='Add a task to your to-do list', brief='Create a new task')
async def addtodo(ctx, *, task: str):
    """Add a task to your list. Usage: !addtodo Finish chapter 5"""
    todos = load_todos()
    user = str(ctx.author.id)
    
    if user not in todos:
        todos[user] = []
    
    todos[user].append({"task": task, "done": False})
    save_todos(todos)
    
    await ctx.send(f"✅ Added to your to-do list: **{task}**")

@bot.command(name='listtodo', help='View your to-do list', brief='See all your tasks')
async def listtodo(ctx):
    """View all your tasks. Usage: !listtodo"""
    todos = load_todos()
    user = str(ctx.author.id)
    
    if user not in todos or not todos[user]:
        return await ctx.send("📝 Your to-do list is empty!")
    
    embed = discord.Embed(title="📝 Your To-Do List", color=discord.Color.green())
    
    for i, item in enumerate(todos[user], 1):
        status = "✅" if item["done"] else "⬜"
        embed.add_field(name=f"{i}. {status}", value=item["task"], inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='donetodo', help='Mark a task as complete', brief='Complete a task (+5 points)')
async def donetodo(ctx, task_num: int):
    """Mark a task as done. Usage: !donetodo 1"""
    todos = load_todos()
    user = str(ctx.author.id)
    
    if user not in todos or task_num < 1 or task_num > len(todos[user]):
        return await ctx.send("⚠️ Invalid task number!")
    
    todos[user][task_num - 1]["done"] = True
    save_todos(todos)
    
    # Award points
    points = load_points()
    points[user] = points.get(user, 0) + 5
    save_points(points)
    
    await ctx.send(f"✅ Task {task_num} marked as done! +5 points")

@bot.command(name='cleartodo', help='Clear all tasks', brief='Delete entire to-do list')
async def cleartodo(ctx):
    """Clear your entire to-do list. Usage: !cleartodo"""
    todos = load_todos()
    user = str(ctx.author.id)
    todos[user] = []
    save_todos(todos)
    await ctx.send("🗑️ To-do list cleared!")

# ADVANCED FEATURE 7 — Weekly Report
@bot.command(name='weeklyreport', help='View your weekly study summary', brief='Last 7 days stats')
async def weeklyreport(ctx):
    """Get your weekly study report. Usage: !weeklyreport"""
    sessions = load_sessions()
    user = str(ctx.author.id)
    
    if user not in sessions or not sessions[user]:
        return await ctx.send("📊 No study sessions recorded yet!")
    
    # Calculate last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    weekly_sessions = [s for s in sessions[user] 
                      if datetime.strptime(s["date"], "%Y-%m-%d %H:%M") >= week_ago]
    
    total_time = sum(s["duration"] for s in weekly_sessions)
    total_sessions = len(weekly_sessions)
    
    points = load_points()
    streaks = load_streaks()
    
    embed = discord.Embed(title="📈 Your Weekly Report", color=discord.Color.purple())
    embed.add_field(name="Study Sessions", value=f"🍅 {total_sessions}", inline=True)
    embed.add_field(name="Total Time", value=f"⏱️ {total_time} minutes", inline=True)
    embed.add_field(name="Current Streak", value=f"🔥 {streaks.get(user, {}).get('streak', 0)} days", inline=True)
    embed.add_field(name="Total Points", value=f"⭐ {points.get(user, 0)}", inline=True)
    embed.add_field(name="Rank", value=get_rank(points.get(user, 0)), inline=True)
    
    await ctx.send(embed=embed)

# ADVANCED FEATURE 8 — Study Session Log
@bot.command(name='logsession', help='Manually log a study session', brief='Log minutes studied')
async def logsession(ctx, minutes: int, *, subject: str = "General"):
    """Log a study session manually. Usage: !logsession 60 Math"""
    if minutes > 300:
        return await ctx.send("⚠️ Maximum 300 minutes per session!")
    
    sessions = load_sessions()
    points = load_points()
    user = str(ctx.author.id)
    
    if user not in sessions:
        sessions[user] = []
    
    sessions[user].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": minutes,
        "type": "manual",
        "subject": subject
    })
    save_sessions(sessions)
    
    points[user] = points.get(user, 0) + minutes
    save_points(points)
    
    await ctx.send(f"📚 Logged {minutes} minutes studying **{subject}**! +{minutes} points")

# ADVANCED FEATURE 9 — Study Goals
@bot.command(name='setgoal', help='Set your daily study goal', brief='Set daily minutes target')
async def setgoal(ctx, daily_minutes: int):
    """Set your daily study goal. Usage: !setgoal 120"""
    reminders = load_reminders()
    user = str(ctx.author.id)
    
    if user not in reminders:
        reminders[user] = {}
    
    reminders[user]["daily_goal"] = daily_minutes
    save_reminders(reminders)
    
    await ctx.send(f"🎯 Daily goal set to {daily_minutes} minutes!")

@bot.command(name='goalcheck', help='Check your daily goal progress', brief='See goal completion %')
async def goalcheck(ctx):
    """Check your progress toward daily goal. Usage: !goalcheck"""
    sessions = load_sessions()
    reminders = load_reminders()
    user = str(ctx.author.id)
    
    goal = reminders.get(user, {}).get("daily_goal", 0)
    if goal == 0:
        return await ctx.send("⚠️ Set a goal first with `!setgoal <minutes>`")
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in sessions.get(user, []) 
                     if s["date"].startswith(today)]
    
    total = sum(s["duration"] for s in today_sessions)
    percentage = (total / goal) * 100
    
    embed = discord.Embed(title="🎯 Daily Goal Progress", color=discord.Color.orange())
    embed.add_field(name="Goal", value=f"{goal} minutes", inline=True)
    embed.add_field(name="Completed", value=f"{total} minutes", inline=True)
    embed.add_field(name="Progress", value=f"{percentage:.1f}%", inline=True)
    
    if total >= goal:
        embed.add_field(name="Status", value="✅ Goal achieved!", inline=False)
    else:
        embed.add_field(name="Remaining", value=f"{goal - total} minutes", inline=False)
    
    await ctx.send(embed=embed)

# Clear Points Command
@bot.command(name='clearpoints', help='Reset your points to zero', brief='Clear all your points')
async def clearpoints(ctx):
    """Reset your points to zero. Usage: !clearpoints"""
    points = load_points()
    user = str(ctx.author.id)
    
    if user not in points or points[user] == 0:
        return await ctx.send("❌ You don't have any points to clear!")
    
    old_points = points[user]
    points[user] = 0
    save_points(points)
    
    await ctx.send(f"🗑️ Your points have been reset! (Lost {old_points} points)")

# Help Command
@bot.command(name='help', help='Show all available commands', brief='View command list')
async def help(ctx):
    """Display all available commands. Usage: !help"""
    embed = discord.Embed(
        title="📚 Study Buddy Commands",
        description="Your personal study assistant!",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="⏰ Timers", value="`!remindme <min>` `!pomodoro [work] [break]` `!schedule <work> <break> <cycles>`", inline=False)
    embed.add_field(name="🔥 Tracking", value="`!studied` `!streak` `!logsession <min> [subject]`", inline=False)
    embed.add_field(name="📊 Stats", value="`!points` `!leaderboard` `!weeklyreport` `!goalcheck` `!clearpoints`", inline=False)
    embed.add_field(name="📝 To-Do", value="`!addtodo <task>` `!listtodo` `!donetodo <#>` `!cleartodo`", inline=False)
    embed.add_field(name="🎯 Goals", value="`!setgoal <daily_min>` `!goalcheck`", inline=False)
    embed.add_field(name="🤝 Social", value="`!findpartner` `!motivate`", inline=False)
    embed.add_field(name="⚙️ Settings", value="`!dailyreminder on/off`", inline=False)
    
    await ctx.send(embed=embed)

# Admin command to manually sync slash commands
@bot.command(name='sync', help='[Admin] Manually sync slash commands')
@commands.is_owner()
async def sync(ctx):
    """Manually sync slash commands. Usage: !sync"""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} slash commands!")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync: {e}")

# ============================================
# SLASH COMMANDS (/) - Same functionality as ! commands
# ============================================

@bot.tree.command(name="motivate", description="Get a motivational quote")
async def slash_motivate(interaction: discord.Interaction):
    await interaction.response.send_message(random.choice(quotes))

@bot.tree.command(name="studied", description="Log that you studied today")
async def slash_studied(interaction: discord.Interaction):
    streaks = load_streaks()
    points = load_points()
    user = str(interaction.user.id)
    today = datetime.now().strftime("%Y-%m-%d")

    if user not in streaks:
        streaks[user] = {"last_day": today, "streak": 1}
        points[user] = points.get(user, 0) + 10
        save_streaks(streaks)
        save_points(points)
        return await interaction.response.send_message("🔥 First day tracked! +10 points! Keep it going!")

    if streaks[user]["last_day"] == today:
        return await interaction.response.send_message("✔ You already logged study for today!")

    last_date = datetime.strptime(streaks[user]["last_day"], "%Y-%m-%d")
    if (datetime.now() - last_date).days == 1:
        streaks[user]["streak"] += 1
        bonus = streaks[user]["streak"] * 2
        points[user] = points.get(user, 0) + 10 + bonus
        save_streaks(streaks)
        save_points(points)
        await interaction.response.send_message(f"🔥 Study logged! You're on a **{streaks[user]['streak']} day streak!** (+{10 + bonus} points)")
    else:
        streaks[user]["streak"] = 1
        points[user] = points.get(user, 0) + 10
        save_points(points)
        await interaction.response.send_message("📘 Streak broken, but don't give up! Starting fresh. (+10 points)")
    
    streaks[user]["last_day"] = today
    save_streaks(streaks)

@bot.tree.command(name="streak", description="View your current study streak")
async def slash_streak(interaction: discord.Interaction):
    streaks = load_streaks()
    user = str(interaction.user.id)

    if user not in streaks:
        return await interaction.response.send_message("📘 No streak yet. Use `/studied` to start!")

    await interaction.response.send_message(f"📚 Your current streak: **{streaks[user]['streak']} days**")

@bot.tree.command(name="points", description="View your points and rank")
async def slash_points(interaction: discord.Interaction):
    points = load_points()
    user = str(interaction.user.id)
    pts = points.get(user, 0)
    rank = get_rank(pts)
    
    embed = discord.Embed(title="📊 Your Stats", color=discord.Color.blue())
    embed.add_field(name="Points", value=f"⭐ {pts}", inline=True)
    embed.add_field(name="Rank", value=rank, inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="View the top 10 students")
async def slash_leaderboard(interaction: discord.Interaction):
    points = load_points()
    if not points:
        return await interaction.response.send_message("📊 No one has earned points yet!")
    
    sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)[:10]
    
    embed = discord.Embed(title="🏆 Study Leaderboard", color=discord.Color.gold())
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (user_id, pts) in enumerate(sorted_users):
        try:
            user = await bot.fetch_user(int(user_id))
            medal = medals[i] if i < 3 else f"#{i+1}"
            rank = get_rank(pts)
            embed.add_field(
                name=f"{medal} {user.name}",
                value=f"{rank} — {pts} points",
                inline=False
            )
        except:
            pass
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pomodoro", description="Start a Pomodoro study session")
@app_commands.describe(work_min="Work time in minutes (default: 25)", break_min="Break time in minutes (default: 5)")
async def slash_pomodoro(interaction: discord.Interaction, work_min: int = 25, break_min: int = 5):
    if work_min > 120 or break_min > 60:
        return await interaction.response.send_message("⚠️ Work time max: 120 min, Break time max: 60 min")
    
    await interaction.response.send_message(f"🍅 **Pomodoro started!** {work_min} minutes of focus begins now!")
    
    points = load_points()
    user = str(interaction.user.id)
    points[user] = points.get(user, 0) + work_min
    save_points(points)
    
    sessions = load_sessions()
    if user not in sessions:
        sessions[user] = []
    sessions[user].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": work_min,
        "type": "pomodoro"
    })
    save_sessions(sessions)
    
    await asyncio.sleep(work_min * 60)
    await interaction.followup.send(f"🧘 **Break time!** Take {break_min} minutes to relax.")
    await asyncio.sleep(break_min * 60)
    await interaction.followup.send("🚀 Break over! Ready for another session?")

@bot.tree.command(name="remindme", description="Set a study reminder")
@app_commands.describe(minutes="Minutes until reminder")
async def slash_remindme(interaction: discord.Interaction, minutes: int):
    if minutes > 1440:
        return await interaction.response.send_message("⚠️ Please set a reminder for less than 24 hours (1440 minutes).")
    await interaction.response.send_message(f"⏳ Okay! I'll remind you in {minutes} minutes.")
    await asyncio.sleep(minutes * 60)
    await interaction.followup.send(f"⏰ {interaction.user.mention} Time to study!")

@bot.tree.command(name="addtodo", description="Add a task to your to-do list")
@app_commands.describe(task="The task to add")
async def slash_addtodo(interaction: discord.Interaction, task: str):
    todos = load_todos()
    user = str(interaction.user.id)
    
    if user not in todos:
        todos[user] = []
    
    todos[user].append({"task": task, "done": False})
    save_todos(todos)
    
    await interaction.response.send_message(f"✅ Added to your to-do list: **{task}**")

@bot.tree.command(name="listtodo", description="View your to-do list")
async def slash_listtodo(interaction: discord.Interaction):
    todos = load_todos()
    user = str(interaction.user.id)
    
    if user not in todos or not todos[user]:
        return await interaction.response.send_message("📝 Your to-do list is empty!")
    
    embed = discord.Embed(title="📝 Your To-Do List", color=discord.Color.green())
    
    for i, item in enumerate(todos[user], 1):
        status = "✅" if item["done"] else "⬜"
        embed.add_field(name=f"{i}. {status}", value=item["task"], inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="donetodo", description="Mark a task as complete")
@app_commands.describe(task_number="The task number to complete")
async def slash_donetodo(interaction: discord.Interaction, task_number: int):
    todos = load_todos()
    user = str(interaction.user.id)
    
    if user not in todos or task_number < 1 or task_number > len(todos[user]):
        return await interaction.response.send_message("⚠️ Invalid task number!")
    
    todos[user][task_number - 1]["done"] = True
    save_todos(todos)
    
    points = load_points()
    points[user] = points.get(user, 0) + 5
    save_points(points)
    
    await interaction.response.send_message(f"✅ Task {task_number} marked as done! +5 points")

@bot.tree.command(name="cleartodo", description="Clear all tasks from your to-do list")
async def slash_cleartodo(interaction: discord.Interaction):
    todos = load_todos()
    user = str(interaction.user.id)
    todos[user] = []
    save_todos(todos)
    await interaction.response.send_message("🗑️ To-do list cleared!")

@bot.tree.command(name="logsession", description="Manually log a study session")
@app_commands.describe(minutes="Minutes studied", subject="Subject studied (optional)")
async def slash_logsession(interaction: discord.Interaction, minutes: int, subject: str = "General"):
    if minutes > 300:
        return await interaction.response.send_message("⚠️ Maximum 300 minutes per session!")
    
    sessions = load_sessions()
    points = load_points()
    user = str(interaction.user.id)
    
    if user not in sessions:
        sessions[user] = []
    
    sessions[user].append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "duration": minutes,
        "type": "manual",
        "subject": subject
    })
    save_sessions(sessions)
    
    points[user] = points.get(user, 0) + minutes
    save_points(points)
    
    await interaction.response.send_message(f"📚 Logged {minutes} minutes studying **{subject}**! +{minutes} points")

@bot.tree.command(name="weeklyreport", description="View your weekly study summary")
async def slash_weeklyreport(interaction: discord.Interaction):
    sessions = load_sessions()
    user = str(interaction.user.id)
    
    if user not in sessions or not sessions[user]:
        return await interaction.response.send_message("📊 No study sessions recorded yet!")
    
    week_ago = datetime.now() - timedelta(days=7)
    weekly_sessions = [s for s in sessions[user] 
                      if datetime.strptime(s["date"], "%Y-%m-%d %H:%M") >= week_ago]
    
    total_time = sum(s["duration"] for s in weekly_sessions)
    total_sessions = len(weekly_sessions)
    
    points = load_points()
    streaks = load_streaks()
    
    embed = discord.Embed(title="📈 Your Weekly Report", color=discord.Color.purple())
    embed.add_field(name="Study Sessions", value=f"🍅 {total_sessions}", inline=True)
    embed.add_field(name="Total Time", value=f"⏱️ {total_time} minutes", inline=True)
    embed.add_field(name="Current Streak", value=f"🔥 {streaks.get(user, {}).get('streak', 0)} days", inline=True)
    embed.add_field(name="Total Points", value=f"⭐ {points.get(user, 0)}", inline=True)
    embed.add_field(name="Rank", value=get_rank(points.get(user, 0)), inline=True)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="setgoal", description="Set your daily study goal")
@app_commands.describe(daily_minutes="Daily goal in minutes")
async def slash_setgoal(interaction: discord.Interaction, daily_minutes: int):
    reminders = load_reminders()
    user = str(interaction.user.id)
    
    if user not in reminders:
        reminders[user] = {}
    
    reminders[user]["daily_goal"] = daily_minutes
    save_reminders(reminders)
    
    await interaction.response.send_message(f"🎯 Daily goal set to {daily_minutes} minutes!")

@bot.tree.command(name="goalcheck", description="Check your daily goal progress")
async def slash_goalcheck(interaction: discord.Interaction):
    sessions = load_sessions()
    reminders = load_reminders()
    user = str(interaction.user.id)
    
    goal = reminders.get(user, {}).get("daily_goal", 0)
    if goal == 0:
        return await interaction.response.send_message("⚠️ Set a goal first with `/setgoal <minutes>`")
    
    today = datetime.now().strftime("%Y-%m-%d")
    today_sessions = [s for s in sessions.get(user, []) 
                     if s["date"].startswith(today)]
    
    total = sum(s["duration"] for s in today_sessions)
    percentage = (total / goal) * 100
    
    embed = discord.Embed(title="🎯 Daily Goal Progress", color=discord.Color.orange())
    embed.add_field(name="Goal", value=f"{goal} minutes", inline=True)
    embed.add_field(name="Completed", value=f"{total} minutes", inline=True)
    embed.add_field(name="Progress", value=f"{percentage:.1f}%", inline=True)
    
    if total >= goal:
        embed.add_field(name="Status", value="✅ Goal achieved!", inline=False)
    else:
        embed.add_field(name="Remaining", value=f"{goal - total} minutes", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clearpoints", description="Reset your points to zero")
async def slash_clearpoints(interaction: discord.Interaction):
    points = load_points()
    user = str(interaction.user.id)
    
    if user not in points or points[user] == 0:
        return await interaction.response.send_message("❌ You don't have any points to clear!")
    
    old_points = points[user]
    points[user] = 0
    save_points(points)
    
    await interaction.response.send_message(f"🗑️ Your points have been reset! (Lost {old_points} points)")

@bot.tree.command(name="findpartner", description="Find a study partner")
async def slash_findpartner(interaction: discord.Interaction):
    user_id = interaction.user.id
    
    if user_id in study_partners:
        return await interaction.response.send_message("⏳ You're already in the queue!")
    
    if len(study_partners) > 0:
        partner_id = study_partners.pop(0)
        partner = await bot.fetch_user(partner_id)
        
        await interaction.response.send_message(f"🤝 Match found! {interaction.user.mention} ↔️ {partner.mention}")
        await partner.send(f"🤝 Study partner found! You've been matched with {interaction.user.name}")
        await interaction.user.send(f"🤝 Study partner found! You've been matched with {partner.name}")
    else:
        study_partners.append(user_id)
        await interaction.response.send_message("🔍 Added to partner queue! Waiting for a match...")

@bot.tree.command(name="help", description="Show all available commands")
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Study Buddy Commands",
        description="Use `/` to see all slash commands!",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="⏰ Timers", value="`/remindme` `/pomodoro`", inline=False)
    embed.add_field(name="🔥 Tracking", value="`/studied` `/streak` `/logsession`", inline=False)
    embed.add_field(name="📊 Stats", value="`/points` `/leaderboard` `/weeklyreport` `/goalcheck` `/clearpoints`", inline=False)
    embed.add_field(name="📝 To-Do", value="`/addtodo` `/listtodo` `/donetodo` `/cleartodo`", inline=False)
    embed.add_field(name="🎯 Goals", value="`/setgoal` `/goalcheck`", inline=False)
    embed.add_field(name="🤝 Social", value="`/findpartner` `/motivate`", inline=False)
    
    await interaction.response.send_message(embed=embed)

# Run the bot
bot.run(os.getenv("DISCORD_TOKEN"))
