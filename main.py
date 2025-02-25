import os
import random
import discord
from discord.ext import commands

intents=discord.Intents.default()
intents.message_content = True

bot=commands.Bot(command_prefix="!", intents=intents)

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

token = os.environ['TOKEN_BOT_DISOCRD']

import threading
from server import run

thread = threading.Thread(target=run, daemon=True)
thread.start()

bot.run(token)