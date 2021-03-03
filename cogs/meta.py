# Cog - meta.py
# Contains meta commands used to troubleshoot and interact with the bot.
# Started: 2021-01-17

import discord
from discord.ext import commands
import subprocess

class Meta(commands.Cog, name="Meta"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
            name='showlogs',
            aliases=['logs'],
            help='Shows last 10 bot logs')
    async def showlogs(self, ctx, number_of_lines: int=10):

        output = subprocess.run(['tail',f'-n {number_of_lines}', 'discord.log'],
                stdout=subprocess.PIPE).stdout.decode('utf-8')

        response_embed = discord.Embed(
                title=f'Log output, last {number_of_lines}',
                description=output,
                color= discord.Color.orange()
        )

        await ctx.send(embed=response_embed)

    
    @commands.command(
            name="load_cog",
            hidden=True
            )
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        """Command to load cog. Remember to use dot path; e.g cogs.cog"""

        try:
            self.bot.load_extension(cog)
        except Exception as error:
            await ctx.send(f"** ERROR: {type(error).__name__} - {error}")
        else:
            await ctx.send("** SUCCESS! **")


    @commands.command(
            name="unload_cog",
            hidden=True
            )
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        """Command to unload a cog. Remember to use dot path; e.g cogs.cog"""

        try:
            self.bot.unload_extension(cog)
        except Exception as error:
            await ctx.send(f"** ERROR: {type(error).__name__} - {error}")
        else:
            await ctx.send("** SUCCESS **")


    @commands.command(
            name="reload_cog",
            hidden=True
            )
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        """Command to reload a cog. Remember to use dot path; e.g cogs.cog"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as error:
            await ctx.send(f"** ERROR: {type(error).__name__} - {error}")
        else:
            await ctx.send("** SUCCESS **")


def setup(bot):
    bot.add_cog(Meta(bot))
