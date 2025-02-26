import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import json
import os
from typing import Dict, List, Optional

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def bonjour(ctx):
  await ctx.send(f"Bonjour {ctx.author} !")

@bot.command()
async def artong(ctx):
  await ctx.send(f"{ctx.author} Implore ton respect à la reine Zouzou")

@bot.command()
async def pileouface(ctx):
  await ctx.send(random.choice(["Pile", "Face"]))

@bot.command()
async def roll(ctx):
  await ctx.send(random.randint(1,100))

@bot.command()
async def ping(ctx):
  await ctx.send(f"Pong !")

@bot.command()
async def pieds(ctx):
  await ctx.send(f"https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.reddit.com%2Fr%2Fmemes%2Fcomments%2Fy3p9n6%2Fsince_we_not_using_thumbs_up_heres_a_toe_up%2F%3Ftl%3Dfr&psig=AOvVaw3ITOIA8B9FN75aAVT4kFLI&ust=1740522747829000&source=images&cd=vfe&opi=89978449&ved=0CBQQjRxqFwoTCIC42diu3YsDFQAAAAAdAAAAABAE")

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game("Zouzouland"))
    print(f"Connecté en tant que {bot.user}")

# Data storage
REMINDERS_FILE = 'reminders.json'

# Global reminders dictionary
reminders = {}

# Functions for managing reminders
def load_reminders():
    """Load reminders from a JSON file."""
    global reminders
    if os.path.exists(REMINDERS_FILE):
        try:
            with open(REMINDERS_FILE, 'r') as f:
                serialized_reminders = json.load(f)
                # Convert string times back to datetime objects
                for user_id, user_reminders in serialized_reminders.items():
                    reminders[user_id] = {}
                    for reminder_id, reminder in user_reminders.items():
                        reminders[user_id][reminder_id] = {
                            "channel_id": reminder["channel_id"],
                            "message": reminder["message"],
                            "time": datetime.datetime.fromisoformat(reminder["time"])
                        }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading reminders: {e}")
            reminders = {}

def save_reminders():
    """Save reminders to a JSON file."""
    with open(REMINDERS_FILE, 'w') as f:
        # Convert datetime objects to strings for JSON serialization
        serializable_reminders = {}
        for user_id, user_reminders in reminders.items():
            serializable_reminders[user_id] = {}
            for reminder_id, reminder in user_reminders.items():
                serializable_reminders[user_id][reminder_id] = {
                    "channel_id": reminder["channel_id"],
                    "message": reminder["message"],
                    "time": reminder["time"].isoformat()
                }
        json.dump(serializable_reminders, f, indent=2)

# Bot event handlers
@bot.event
async def on_ready():
    """Event handler for when the bot is ready."""
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("------")

    # Load existing reminders
    load_reminders()

    # Start the background task to check reminders
    check_reminders.start()

@tasks.loop(seconds=10)
async def check_reminders():
    """Background task to check and send due reminders."""
    current_time = datetime.datetime.now()
    reminders_to_remove = []  # List of (user_id, reminder_id) tuples to remove

    for user_id, user_reminders in reminders.items():
        for reminder_id, reminder in user_reminders.items():
            if reminder["time"] <= current_time:
                # Reminder is due
                channel = bot.get_channel(reminder["channel_id"])
                if channel:
                    user = await bot.fetch_user(int(user_id))
                    await channel.send(f"{user.mention} Reminder: {reminder['message']}")
                else:
                    print(f"Could not find channel {reminder['channel_id']} for reminder")

                # Mark this reminder for removal
                reminders_to_remove.append((user_id, reminder_id))

    # Remove sent reminders
    for user_id, reminder_id in reminders_to_remove:
        del reminders[user_id][reminder_id]
        if not reminders[user_id]:  # If user has no more reminders
            del reminders[user_id]

    # Save updated reminders if any were removed
    if reminders_to_remove:
        save_reminders()

@check_reminders.before_loop
async def before_check_reminders():
    """Wait until the bot is ready before starting the reminder check loop."""
    await bot.wait_until_ready()

# Bot commands
@bot.command()
async def remind(ctx, time_str: str, *, message: str):
    """
    Set a reminder
    Usage: !remind <time> <message>
    Time formats:
    - 5s (5 seconds)
    - 5m (5 minutes)
    - 5h (5 hours)
    - 5d (5 days)
    - tomorrow (1 day)
    - MM/DD/YYYY HH:MM (specific date and time)
    """
    user_id = str(ctx.author.id)
    reminder_time = None

    # Parse time string
    try:
        if time_str.endswith('s'):
            seconds = int(time_str[:-1])
            reminder_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        elif time_str.endswith('m'):
            minutes = int(time_str[:-1])
            reminder_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            reminder_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            reminder_time = datetime.datetime.now() + datetime.timedelta(days=days)
        elif time_str.lower() == 'tomorrow':
            reminder_time = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            # Try to parse as MM/DD/YYYY HH:MM
            reminder_time = datetime.datetime.strptime(time_str, "%m/%d/%Y %H:%M")
    except ValueError:
        await ctx.send("Invalid time format. Use formats like '5s', '10m', '2h', '1d', 'tomorrow', or 'MM/DD/YYYY HH:MM'")
        return

    # Initialize user's reminders if not exists
    if user_id not in reminders:
        reminders[user_id] = {}

    # Generate a unique reminder ID
    reminder_id = str(len(reminders[user_id]) + 1)

    # Store the reminder
    reminders[user_id][reminder_id] = {
        "channel_id": ctx.channel.id,
        "message": message,
        "time": reminder_time
    }

    # Save reminders to file
    save_reminders()

    # Confirm to the user
    time_until = reminder_time - datetime.datetime.now()
    hours, remainder = divmod(time_until.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    time_str = ""
    if time_until.days > 0:
        time_str += f"{time_until.days} days, "
    if hours > 0:
        time_str += f"{hours} hours, "
    if minutes > 0:
        time_str += f"{minutes} minutes, "
    if seconds > 0 or (time_until.days == 0 and hours == 0 and minutes == 0):
        time_str += f"{seconds} seconds"

    await ctx.send(f"Reminder set! I'll remind you about '{message}' in {time_str} (ID: {reminder_id})")

@bot.command()
async def reminders(ctx):
    """List all your active reminders."""
    user_id = str(ctx.author.id)

    if user_id not in reminders or not reminders[user_id]:
        await ctx.send("You don't have any active reminders.")
        return

    # Build the list of reminders
    reminder_list = "Your active reminders:\n\n"
    for reminder_id, reminder in reminders[user_id].items():
        time_until = reminder["time"] - datetime.datetime.now()

        # Format time until reminder
        if time_until.total_seconds() < 0:
            time_str = "Overdue"
        else:
            hours, remainder = divmod(time_until.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_str = ""
            if time_until.days > 0:
                time_str += f"{time_until.days} days, "
            if hours > 0:
                time_str += f"{hours} hours, "
            if minutes > 0:
                time_str += f"{minutes} minutes"
            elif seconds > 0 or (time_until.days == 0 and hours == 0):
                time_str += f"{seconds} seconds"

        reminder_list += f"ID {reminder_id}: '{reminder['message']}' - in {time_str}\n"

    await ctx.send(reminder_list)

@bot.command()
async def cancel(ctx, reminder_id: str):
    """Cancel a reminder by its ID."""
    user_id = str(ctx.author.id)

    if user_id not in reminders or reminder_id not in reminders[user_id]:
        await ctx.send(f"No reminder found with ID {reminder_id}.")
        return

    # Get the reminder message for confirmation
    reminder_message = reminders[user_id][reminder_id]["message"]

    # Remove the reminder
    del reminders[user_id][reminder_id]
    if not reminders[user_id]:  # If user has no more reminders
        del reminders[user_id]

    # Save updated reminders
    save_reminders()

    await ctx.send(f"Reminder '{reminder_message}' (ID: {reminder_id}) has been cancelled.")

@bot.command()
async def help_reminder(ctx):
    """Display help for using the reminder bot."""
    help_text = """
**Reminder Bot Commands**

`!remind <time> <message>`
Set a new reminder. Time formats:
- `5s` (5 seconds)
- `10m` (10 minutes)
- `2h` (2 hours)
- `1d` (1 day)
- `tomorrow` (1 day)
- `MM/DD/YYYY HH:MM` (specific date and time)

Example: `!remind 15m Take a break`

`!reminders`
List all your active reminders.

`!cancel <id>`
Cancel a reminder by its ID.

`!help_reminder`
Show this help message.
"""
    await ctx.send(help_text)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors."""
    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command and ctx.command.name == "remind":
            await ctx.send("Usage: !remind <time> <message>\nExample: !remind 10m Take a break")
        elif ctx.command and ctx.command.name == "cancel":
            await ctx.send("Usage: !cancel <reminder_id>\nUse !reminders to see your active reminders.")
        else:
            await ctx.send(f"Missing required argument for this command. Try !help_reminder for usage info.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Try !help_reminder to see available commands.")
    else:
        print(f"Error: {error}")
        await ctx.send(f"An error occurred: {type(error).__name__}")

# Run the bot
def main():
    bot.run(os.environ['TOKEN_BOT_DISOCRD'])

if __name__ == "__main__":
    main()

token = os.environ['TOKEN_BOT_DISOCRD']

import threading
from server import run

thread = threading.Thread(target=run, daemon=True)
thread.start()

bot.run(token)

