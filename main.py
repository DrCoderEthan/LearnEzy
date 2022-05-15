import discord
from discord import *
from discord.ext import commands
import random
import asyncio
import os
from dotenv import load_dotenv



intent = discord.Intents(members=True, guilds=True, message_content=True)


lmbot = commands.Bot(command_prefix="=", intents=intent,help_command=None)

load_dotenv()

@lmbot.event
async def on_ready():
    print("The Bot is Ready")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        lmbot.load_extension(f'cogs.{filename[:-3]}')








lmbot.run('OTc1MzkxOTM1ODIyOTY2ODQ1.G4QLK_.zvguJIerF9U12sWFyKAGH1PoCOEWCciX6pISTM')