# Cog - warhammer.py
# Contains commands for Warhammer related content and functions
# Started: 2021-01-17

import discord
import json
import random

from discord.ext import commands

from KrigsBot import logger
from KrigsBot import logCommand

# Define Data sources

WARHAMMER_TERMS = "./Data/WarhammerTerms.json"
WARHAMMER_QUOTES = "./Data/WarhammerQuotes.txt"
WARHAMMER_SECONDARIES ="./Data/Secondaries.json"

class Warhammer(commands.Cog, name="Warhammer"):
    def __init__(self, bot):
        self.bot = bot


    ### Command - Quote ###
    @commands.command(
            name='quote',
            help='Prints a random inspirational Warhammer 40K quote'
            )

    async def quote40k(self, ctx):
        logger.info(f"{ctx.author} requested a quote.")
    
        quotes = open(WARHAMMER_QUOTES,"r")
        response = random.choice(quotes.readlines()).rstrip('\n')
        quotes.close()

        await ctx.send(response)


    ### Command - Warhammer ###
    @commands.group(
            aliases=['wh'],
            invoke_without_command=True,
            case_insensitive=True
            )

    async def Warhammer(self, ctx):
        logCommand(ctx)
        await ctx.send_help(Warhammer)


    @Warhammer.command()
    async def secondaries(self, ctx, *, query=None):
        logCommand(ctx)

        with open(WARHAMMER_SECONDARIES) as file:
            data = json.load(file)

        # If invoker passes no arguement, list all the secondaries loaded.
        if query == None or query == "list":
            
            result = ""

            for secondary in data:
                result +=f"{data[secondary]['name']:<25} - {data[secondary]['category']}\n"

            await ctx.send("```" + result + "```")

        else:

            if query in data:
                
                resultEmbed = discord.Embed(
                        title=f"{data[query]['name']}",
                        color=discord.Color.blue(),
                        description=f"{data[query]['definition']}"
                        )

                resultEmbed.add_field(name='Category', inline=True, value=f"{data[query]['category']}")
                resultEmbed.add_field(name='Scoring Type', inline=True, value=f"{data[query]['type']}")
                resultEmbed.add_field(name='Victory Points', inline=True, value=f"{data[query]['victoryPoints']}")
                resultEmbed.set_footer(text=f"Source: {data[query]['source']}")
                await ctx.send(embed=resultEmbed)

            else:

                termlist = [element for element in data]

                regex = re.compile(f'.*{query}.*')

                result = list(filter(regex.match, termlist))

                if result:
                    response = f"No eact match found for {query} but there were some partial hits:\n\n"

                    for term in result:
                        response += f"- {data[term]['name']:<15} - {data[term]['category']}\n"

                    await ctx.send("```" + response + "```")

                else:
                    logging.info(f"Did not find term: '{query}' in WarhammerTerms.json")
                    await ctx.send("Term not found; Speak to the Icelander")











    @Warhammer.command()
    async def terrain(self, ctx, *, query):
        logCommand(ctx)

        query = query.lower()

        with open(WARHAMMER_TERMS) as file:
            collection = json.load(file)

        if query == "list":

            filter = [element for element in collection if collection[element]['type'] == 'Terrain Trait']

            result = "```"

            for term in filter:
                result += f"{term.ljust(22)} - {collection[term]['type']}\n"
            
            result += "```"

            responseEmebed = discord.Embed(
                    title="Warhamer 40k, 9th Edition Terrain Traits",
                    color = discord.Color.blue(),
                    description = result
                    )
            
            await ctx.send(embed=responseEmebed)

        elif query in collection:
        
            
            responseEmbed = discord.Embed(
                    title = f"Terrain Trait: {collection[query]['name']}",
                    color = discord.Color.blue(),
                    description = collection[query]['definition']
                    )
        
            responseEmbed.set_footer(text = f"Source: {collection[query]['source']}")

            await ctx.send(embed=responseEmbed)

        

def setup(bot):
    bot.add_cog(Warhammer(bot))
