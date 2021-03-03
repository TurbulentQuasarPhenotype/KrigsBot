# Krigsbot 2.0 - A modular bot for all your warhammer gaming needs
# author: asda
# started: 2021-01-17 (refactor from version 1.0)

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

### Load Basic Configuration ###
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')


### Setup basic logging ###
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

### Helper function - LogCommand(ctx) ###
def logCommand(ctx):
    logger.info(f"Activity: {ctx.author} invoked {ctx.command} with '{ctx.message.content}'")

### Configure bot ###
bot = commands.Bot(
        command_prefix='!',
        case_insensitive=True
        )


### Cogs ###
cogs = [
        'cogs.meta',
        'cogs.warhammer',
        'cogs.members',
        'cogs.events',
        'cogs.necromunda'
        ]

for cog in cogs:
    bot.load_extension(cog)

### Triggers ###

@bot.event
async def on_ready():
    logger.info('KrigBot has connected to Discord')
    print(f'{bot.user.name} has connected.')
    await bot.change_presence(activity=discord.Game(name='Only in ERROR does duty end.'))


### Runtime ###
bot.run(TOKEN, reconnect=True)

