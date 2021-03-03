# Contains command for Necromunda related content and functions.
# Started: 2021-01-17

import discord
import json
import random
import re

from discord.ext import commands
from KrigsBot import logger
from KrigsBot import logCommand

### Data Variables  ###
NC_SKILLS = "./Data/Necromunda_Skills.json"


class Necromunda(commands.Cog, name="Necromunda"):
    def __init__(self, bot):
        self.bot = bot

    ### Command - Necromunda ###
    @commands.group(
            aliases=['nc', 'necro'],
            invoke_without_command=True,
            case_insensitive=True
            )
    async def Necromunda(self, ctx):
        await ctx.send_help(ctx.command)


    @Necromunda.command(
            help="Perform a roll (Injury, OOA, Recovery)"
            )
    async def roll(self, ctx, type_of_roll: str):
        logCommand(ctx)

        if type_of_roll.lower() == "injury":
            
            roll_result = random.randint(1,6)
            
            FW_descriptions =[
                    'THEY HAVE WRONGED US!',
                    '...No, what you have are bullets, and the hope that when those bullets run out I will no longer be standing...',
                    'Wounds to be tended; lessons to be learned.',
                    'THE FLESH IS WEAK!',
                    'Remind yourself that overconfidence is a *slow* and *insidious* killer.'
                    ]

            SI_descriptions =[
                    'How quickly the tide turns...',
                    'Death waits for the slightest lapse in concentration...',
                    'Dazed, reeling... about to break.',
                    'Ringing ears, blurred vision - the end approaches...',
                    'Teetering on the brink, facing the abyss...'
                    ]

            OOA_descriptions =[
                    'TELL YOUR GODS I\'M COMING!',
                    'OH, THEY\' GONNA HAVE TO GLUE YOU BACK TOGETHER... IN.HELL!',
                    'Another life wasted in the pursuit of glory and gold.',
                    'A life spent not overcharging plasma, is a life lived in cowardice.',
                    'There can be no hope in this hell, no hope at all...'
                    ]

            if roll_result in range(1,3):
                result = "Flesh Wound"
                result_text = "The fighter suffers a *Flesh Wound*, reducing their Toughness characteristic by 1.\nIf a fighter is reduced to Toughness 0, they go *Out Of Action*."
                result_color = discord.Color.green()
                result_description = random.choice(FW_descriptions)
                fileName = "necromunda_FW.png"
                file = discord.File("./Images/necromunda_FW.png", filename=fileName)


            elif roll_result in range(3,6):
                result = "Seriously Injured"
                result_text = "The fighter is *Prone* and laid face-down.\nThey may successfully recover in a later end phase. If this injury was inflicted in close combat, the fighter may be vulnerable to a *Coup De Grace* action. "
                result_color = discord.Color.gold()
                result_description = random.choice(SI_descriptions)
                fileName = "necromunda_SI.png"
                file = discord.File("./Images/necromunda_SI.png", filename=fileName)

            else:
                result = "Out Of Action"
                result_text = "The fighter is immediately removed from play."
                result_color = discord.Color.red()
                result_description = random.choice(OOA_descriptions)
                fileName = "necromunda_OOA.png"
                file = discord.File("./Images/necromunda_OOA.png", filename=fileName)

        responseEmbed = discord.Embed(
                title= f"Injury Dice: {result}",
                color = result_color,
                description = f"*{result_description}*"
                )

        responseEmbed.add_field(name="Effect",inline=False,value=result_text)
        responseEmbed.add_field(name="Dice roll",inline=True,value=roll_result)
        responseEmbed.set_image(url=f"attachment://{fileName}")

        responseEmbed.set_footer(text="Source: Necromunda Rulebook (2018); p.71")

        await ctx.send(file = file, embed=responseEmbed)


    @Necromunda.command(
            aliases=['skill']
            )
    async def skills(self, ctx, *, query=None):
        logCommand(ctx)
        

        with open(NC_SKILLS) as file:
            skillList = json.load(file)

        uniqueSkillGroup = sorted(set([skillList[skill]['skill_set'] for skill in skillList]))

        # Case 1: Invoked with no command, or the 'list' argument
        # Show the invoker a list of all available skills
        if query == None or query == "list":

            listEmbed = discord.Embed(
                        title=f"Necromunda Skill List",
                        color=discord.Color.blue(),
                        description=f"The following Skillset and skills are loaded"
                        )

            for skillgroup in uniqueSkillGroup:

                formattedskills = '\n'.join([skillList[skill]['name'] for skill in skillList if skillList[skill]['skill_set'] == skillgroup])
                listEmbed.add_field(name=f'{skillgroup}', inline=True, value=f"{formattedskills}")

            await ctx.send(embed=listEmbed)

        # Case 2: Invoked with a skill set.
        # NOTE: Because Skill Sets are values, we shift the query into Title-case to match our values.
        elif query.title() in uniqueSkillGroup:

            output = ""

            
            for entry in [[skillList[skill]['skill_number'],skillList[skill]['name']] for skill in skillList if skillList[skill]['skill_set']  == query.title()]:
                output += f"{entry[0]} -  {entry[1]}\n"

            listEmbed = discord.Embed(
                    title=f'Necromunda Skill Set: {query}',
                    color=discord.Color.blue(),
                    description=f'The {query} skill set contains the following skills:\n\n' + output)

            await ctx.send(embed=listEmbed)


        # Case 3: Invoked with a specific skill
        elif query in skillList:

            listEmbed = discord.Embed(
                    title=f"Necromunda skill: {skillList[query]['name']}",
                    color=discord.Color.blue(),
                    description=f"{skillList[query]['definition']}")

            listEmbed.add_field(name='Skill Set',inline=True,value=f"{skillList[query]['skill_set']}")
            listEmbed.add_field(name='Skill Number',inline=True,value=f"{skillList[query]['skill_number']}")
            listEmbed.set_footer(text=f"Source: {skillList[query]['source']}")

            await ctx.send(embed=listEmbed)


        # Case 4: No hit in either the skill sets or skill list; lets try a regex match or bail with an apology
        else:
            logger.info(f"No hit: Did not find term: {query} in Necromunda_Skills.json")
            termlist = [element for element in skillList]
            
            regex = re.compile(f".*{query}.*")

            resultlist = list(filter(regex.match, termlist))

            if resultlist:
                response = "```"
                for term in resultlist:
                    response += f"- {skillList[term]['name'].ljust(22)}{skillList[term]['skill_set']}\n"
                
                response += "```"

                embedResult = discord.Embed(
                        title=f"No hits for {query} in Necromunda Skills",
                        color= discord.Color.red(),
                        description=f"No exact match found for {query}, but there were some partial hits:"
                        )

                embedResult.add_field(name="Partial hits",inline=False,value=response)

                await ctx.send(embed=embedResult)

            else:

                embedResult = discord.Embed(
                        title=f"No hits at all for {query} in Necromunda Skills",
                        color=discord.Color.red(),
                        description=f"No hits at all for {query}; Perhaps it's called something else?\n\nTry '!nc skills list' for a list of all loaded skills."
                        )

                await ctx.send(embed=embedResult)





def setup(bot):
    bot.add_cog(Necromunda(bot))
