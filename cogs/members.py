# Cog - members.py
# Contains commands related to membership in Krigssvinen.
# started: 2021-01-24

import discord
import json
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
from KrigsBot import logger
from KrigsBot import logCommand

# Data variables
MEMBERS = "./Data/members.json"
GOOGLE_CREDS_KRIGSBOT = "./Auth/Google-KrigsBot-creds.json"

class Members(commands.Cog, name="Members"):
    def __init__(self, bot):
        self.bot = bot



    ### Helper function: is_member(query)
    # Checks if a given person is a member of Krigssvinen.
    # Accepts:
    #   - An INT, for searching by Discord ID
    #   - A string, for searching by name
    ###
    def is_member(self, query):
        
        # Load the member list.
        with open(MEMBERS) as file:
            member_data = json.load(file)

        # Were we passed an Int?
        # In that case, query the member_data by discord.Id
        if isinstance(query, int):
            if member_data[str(query)]:
                return True
            else:
                return False

        # Were we passed a string?
        # In that case, iterate the names of all members and check for match.
        elif isinstance(query, str):
            if [element for element in memberdata if member_data[element]['name'] == query]:
                return True
            else:
                return False



    ### Helper-function: get_member(member)
    # Returns the json object that represents a member
    # Accepts:
    #   - member as Int, for querying by Discord ID
    #   - member as String, for querying by registered name
    ###
    def get_member(self, member):
        
        # Sanity check; Is this member actually a member?
        if not self.is_member(member):
            return false
        
        with open(MEMBERS) as file:
            member_data = json.load(file)

        if isinstance(member, int):
            specific_member = member_data[str(member)]

        elif isinstance(member, str):
            specific_member = [element for element in member_data if member_data[element]["name"] == member]

        return specific_member

    ### Helper-function: has_member_role(member, role: str)
    # Check the member.json and returns whether that member has a queried role
    # Accepts:
    #   - member as Int, for querying by Discord ID
    #   - member as string, for querying by registered name.
    #   - role as string, for querying by registered role
    ###
    def has_member_role(self, member, role: str):
        
        # Load the member data.
        with open(MEMBERS) as file:
            member_data = json.load(file)
        
        #Sanity check; Is this member actually a member?
        if not self.is_member(member):
            return False

        # Check if member was passed by discord ID
        if isinstance(member, int):
            
            #Check if member has any roles to begin with.
            if not "roles" in member_data[str(member)]:
                return False

            # Assuming the member has any roles, is one of the the queried role?
            else:
                if role in member_data[str(member)]["roles"]:
                    return True
                else:
                    return False

        #Check if member was passed by registered full name
        elif isinstance(member, str):

            specific_member = [element for element in member_data if member_data[element]["name"] == member]

            if "roles" in specific_member:
                if role in specific_member["roles"]:
                    return True
                else:
                    return False
            else:
                return False



    # Helper-function: get_all_roles(member)
    # Returns a list with all the roles registered by a user
    # Accepts:
    #   - member as Int, for querying by Discord ID
    #   - member as String, for quering by registered name
    ###
    def get_all_roles(self, member):

        if not self.is_member(member):
            return False
        
        memberdata = self.get_member(member)

        if "roles" in memberdata:
            return memberdata["roles"]
        else:
            return False



    @commands.command(
            name='Whoami',
            help='Checks user records kept by the bot.',
            case_insensitive=True)
    async def whoami(self,ctx):
        logCommand(ctx)

        with open(MEMBERS) as file:
            data = json.load(file)

        if not str(ctx.author.id) in data:
            await ctx.send(f"{ctx.author.name} is not a member of Krigssvinen (yet).")
            return

        responseEmbed = discord.Embed(
            title=f"User Records for {ctx.author.name}",
            color = discord.Color.orange(),
            description="This command lists all the records associated with a member of Krigssvinen."
            )

        responseEmbed.add_field(name="Membership",inline=True,value=f"{data[str(ctx.author.id)]['membership_type']}")
        
        if self.get_all_roles(ctx.author.id):
            list_of_roles = self.get_all_roles(ctx.author.id)
            responseEmbed.add_field(name="Roles",inline=True,value=', '.join([str(x) for x in list_of_roles]))

        await ctx.send(embed=responseEmbed)


    @commands.command(
        name='ShowMembership',
        aliases=['membership'],
        help='Shows membership dues paid.'
        )
    async def ShowMembership(self, ctx,* , member=None):
        async with ctx.typing():
            logCommand(ctx)

            with open(MEMBERS) as file:
                member_data = json.load(file)

            gc = gspread.service_account(filename=GOOGLE_CREDS_KRIGSBOT)
            gsheet = gc.open('Budget 2020')
            kassan = gsheet.worksheet('Kassaflöde')
            data = kassan.get_all_records()

            # Case 1: Invoked without arguement - Get records of the invoker.
            if member == None:
            
                if str(ctx.author.id) in member_data:

                    filter = [element for element in data if element['Avsändare'] == member_data[str(ctx.author.id)]['name']]

                else:
                    await ctx.send(f'No records found for {ctx.author.name} in the books.')

            # Case 2: Invoked with an argument; Only allow this for Styrelse-members
            else:
                if isinstance(ctx.channel, discord.channel.DMChannel):
                    if not ctx.author.id in [376108819954008065,187291501288488960,431321574273056778]:
                        await ctx.send('Sorry, only Styrelsen gets to peak at others.')
                        return

                elif isinstance(ctx.channel, discord.channel.GroupChannel):
                    if not 749704716539265126 in [element.id for element in ctx.author.roles]:
                        await ctx.send('Sorry, only Styrelsen gets to peak at others.')
                        return

                filter = [element for element in data if element['Avsändare'] == member]

            if not filter:
                await ctx.send(f'No records for {member} in the books.')
                return

            summary = [[]]
            for entry in filter:
                summary.append([entry['Datum'], entry['Kommentar'], entry['Summa (SEK)']])

            #result = tabulate(summary, headers=['Datum', 'Kommentar', 'Summa (SEK)'])
           
            # Send the result as part of a codeblock; this allows us to include more horizontal data.
            await ctx.send("```" + "\n".join(map(str,summary)) + "```")



def setup(bot):
    bot.add_cog(Members(bot))
