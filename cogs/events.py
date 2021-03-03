# Cog - events.py
# A module for creating and administering event bookings.
# Started: 2021-01-25

import discord
import json
import re
import os
import shlex

from random import randint
from discord.ext import commands
from datetime import datetime

from KrigsBot import logger
from KrigsBot import logCommand

# Data variables
EVENT_DIR = "./Events/"
EVENT_GUILD = 622767259466727474 # Krigssvinen
EVENT_CHANNEL = 810129199661711410 #Bokningar-och-händelser
#EVENT_CHANNEL = 795064317531127848 #Bot-fabriker - För att debug:a



class Events(commands.Cog, name="Events"):
    def __init__(self, bot):
        self.bot = bot
   
    ### Helper-function: resolveDiscordIdsToNames ()
    # Takes a list of discord ID:s and resolves them to usernames.
    # 
    # Returns a string of the concatenated usernames.
    #
    # Accepts
    #  - ids, an array of integers from discord.User.id
    ###
    def resolveDiscordIdsToNames(self, ids):
        if len(ids) == 0:
            return "None"
        else:
            resultArray = []

            for user in ids:

                user = self.bot.get_user(user)
                if user is None:
                    return "None"
                resultArray.append(user.name)

            return ','.join(map(str, resultArray)) 


    ### Helper-function: checkIfEventIDExists(event)
    # Returns whether an event file exists in the EVENT_DIR.
    # Event files are assumed to end in .json; does not have to be stated in event variable.
    #
    # Accepts:
    #   - event, a string matching an event filename (without .json)
    ###
    def getEventByID(self, eventID):

        result = []
        regex = re.compile(f".*{eventID}\.json")
        for root, dir, files in os.walk(EVENT_DIR):
            for file in files:
                if regex.match(file):
                    result.append(file)

        if len(result) == 0:
            return False
        else:
            return result[0]


    ### Helper-function: buildEventEmbed(self, data)
    # Takes a single json object representing an event booking and transforms
    # it into a discord.Embed
    #
    # Accepts:
    #  - data, a json-object representing an event
    ###
    def buildEventEmbed(self, data):
        
        responseEmbed= discord.Embed(
            title=f"Event: {data['id']} - {data['name']}",
            color=discord.Color.blue(),
            description=f"{data['description']}"
            )

        responseEmbed.add_field(name="Location",inline=True,value=f"{data['location']}")
        responseEmbed.add_field(name="Date",inline=True,value=f"{data['date']}")
        responseEmbed.add_field(name="Time",inline=True,value=f"{data['time']}")
        responseEmbed.add_field(name="Game",inline=True,value=f"{data['game']}")
        responseEmbed.add_field(name="Participants",inline=True,value=f"{self.resolveDiscordIdsToNames(data['participants'])}")
        responseEmbed.set_footer(text=f"Organiser: {data['organiser']}")

        return responseEmbed



    @commands.group(
            aliases=['events'],
            invoke_without_command=True,
            case_insensitive=True)
    async def event(self, ctx):
        await ctx.send_help(ctx.command)


    @event.command(
            help="Removes the caller from the participant list of an event."
            )
    async def leave(self, ctx, eventID):
        logCommand(ctx)

        #first, check if the event exists
        eventFile = self.getEventByID(eventID)

        if not eventFile:
            await ctx.send(f"No event found matching: {eventID}")
            return
        else:
        
            with open(f"{EVENT_DIR}{eventFile}") as file:
                data = json.load(file)

            if not ctx.author.id in data['participants']:
                await ctx.send(f"{ctx.author.name} is not participating in event: {eventID}.")
                return    

            data['participants'].remove(ctx.author.id)

            with open(f"{EVENT_DIR}{eventFile}", "w") as file:
                json.dump(data,file)

            await ctx.send(f"{ctx.author.name} is no longer participating in event: {eventID}.")
 


    @event.command(
            help="Adds the caller to the participants list of an event."
            )
    async def join(self, ctx, eventID):
        logCommand(ctx)

        #first, check if the event exists
        eventFile = self.getEventByID(eventID)

        if not eventFile:
            await ctx.send(f"No event found matching: {eventID}")
            return
        else:
        
            with open(f"{EVENT_DIR}{eventFile}") as file:
                data = json.load(file)

            if ctx.author.id in data['participants']:
                await ctx.send(f"{ctx.author.name} is already participating in event: {eventID}")
                return

            data['participants'].append(ctx.author.id)

            with open(f"{EVENT_DIR}{eventFile}", "w") as file:
                json.dump(data,file)

            await ctx.send(f"Added {ctx.author.id} to event: {eventID}.")
 

    @event.command(
            help="Removes an existing event (Organiser only)."
            )
    async def destroy(self, ctx, event):
        logCommand(ctx)

        if self.getEventByID(event):
            with open(f"{EVENT_DIR}{self.getEventByID(event)}") as file:
                data = json.load(file)

            if data['organiser'] == ctx.author.name:

                os.remove(f"{EVENT_DIR}{self.getEventByID(event)}")
                logger.info(f"{event} removed by {ctx.author.name}")
                await ctx.send(f"Event {data['id']} has been removed.")

                channel = self.bot.get_guild(EVENT_GUILD).get_channel(EVENT_CHANNEL)
                await channel.send(f"{ctx.author} has removed event: {data['id']}.")
                return

            else:
                logger.info(f"{ctx.author.name} is not authorized to remove event: {event}.")
                await ctx.send(f"Only the organiser of the event({data['organiser']}) may remove it.")
                return

        else:
            await ctx.send(f"Found no event called: {event}")
            return

    @event.command(
            help="Retrieves an event and displays it."
            )
    async def get(self, ctx, eventID):
        logCommand(ctx)

        regex = re.compile('#\d{4}$')
        if not regex.match(eventID):
            await ctx.send(f"Events must be specified with an eventID; e.g '#1234'.")
            return
    
        regex = re.compile(f'.*{eventID}\.json$')

        eventFile = None
        for root, dirs, files in os.walk(EVENT_DIR):
            for file in files:
                if regex.match(file):
                    eventFile = file

        if eventFile:

            with open(f"{EVENT_DIR}{eventFile}") as file:
                data = json.load(file)

            await ctx.send(embed= self.buildEventEmbed(data))
        else:
            logger.info(f"Did not find any event called: {eventID}.")
            await ctx.send(f"No event found called: {eventID}.")


    @event.command(
            help="List all the events currently booked.",
            aliases=['calendar']
            )
    async def list(self, ctx):
        logCommand(ctx)
        
        # First, we must determine how many events we have booked.
        # For this purpose, we load any .json files we find in the EVENT_DIR

        # Even if we do not create files in the EVENT_DIR manually, other files such as .swp may appear there.
        # This regex will allow us to select only the relevant files.
        regex = re.compile('.*json$')

        # Walk the EVENT_DIR and add any files that match our regex to the fileArray.
        fileArray = []
        for root, dirs, files in os.walk(EVENT_DIR):
            for file in files:
                if regex.match(file):
                    fileArray.append(file)

        # If we have found exactly zero .json files in the EVENT_DIR, there are no booked events.
        if len(fileArray) == 0:

            responseEmbed = discord.Embed(
                    title="No events booked",
                    color=discord.Color.red(),
                    description="There are no events booked in the grimdark future"
                    )

            await ctx.send(embed=responseEmbed)
            return

        # If there are any files found, we have booked events that must be processed.
        else:

            # We load the json of every file into a list, for later operations.
            data = []
            for file in fileArray:
                with open(f"{EVENT_DIR}{file}") as eventFile:
                    data.append(json.load(eventFile))

            # We build the Embed that will contain all of our listings.
            # Later we will add fields and codeblocks to this embed to represent bookings.
            responseEmbed = discord.Embed(
                    title="Event Calendar",
                    color=discord.Color.blue()
                    )
    

            # First, make a sorted list of all unique dates in ascending order
            dateList = sorted(set([element['date'] for element in data]))

            # Because there may be multiple events booked per day, we must go through each day and operate.
            for uniqueDate in dateList:

                # There may be multiple events booked to start at the same time.
                # Therefore we create a list of unique times for this date to process futher.
                timeList = sorted(set([element['time'] for element in data if element['date'] == uniqueDate]))
                
                # Because our calendar will breakdown events by day, we begin composing our codeblock variable here.
                schema = "```"

                # We handle each unique starting time to process further.
                for uniqueTime in timeList:
                   
                    # We create a list of unique sorted ID:s for this unique time on this unique date.
                    IDList = sorted(set([element['id'] for element in data if element['date'] == uniqueDate and element['time'] == uniqueTime]))
                    # Since the list of ID:s has been sorted, we operate on it in order and write data to our codeblock variable.
                    for uniqueID in IDList:

                        # Using a generator expression, we retrieve the unqiue event we are operating on by its ID.
                        specificEvent = next(element for element in data if element['id'] == uniqueID)

                        # We append our event details to the codeblock, representing one event on that day.
                        schema += f" {specificEvent['time']} | {specificEvent['game']}: {specificEvent['name']}({(specificEvent['id'])[10:]})\n"

                # Having looped through all the events of a specific day, we close our codeblock variable.
                schema += "```"

                # As a design affordance, we present the date and the corresponding weekday for the calender.
                dayOfWeek = datetime.strptime(uniqueDate, "%Y-%m-%d").strftime("%A") 

                # We commit our field into the embed.
                # Since the list is ordered, the events represented will appear in order on the Embed.
                responseEmbed.add_field(name=f"{uniqueDate} - {dayOfWeek}",inline=False,value=schema)

            # Having handled all events and built a field for each day, our embed is finished.
            # We send it back to the caller.
            await ctx.send(embed=responseEmbed)


    @event.command(
            aliases=['book'],
            help="""
            Creates a new event and announces it.

            Mandatory arguments:
              <DATE> - an ISO8601 date (e.g 2021-12-31)
              <TIME> - an legal 24h time with : delimiter (e.g 13:00)

            Optional arguments:
            All optional arguments must be specified as keywords (e.g name=\"My Event\").
            Multiple keywords are seperated by whitespace.
              name - The name of your event.
              game - The game to be played at your event.
              location - The place your event will take place at.
              description - A description of your event.

            Arguments containing any other keyword will be disregarded.
            """,
            usage="!event create <DATE> <TIME> (OPTIONAL: name=\"\", game=\"\", location=\"\", description=\"\")",
            rest_is_raw=True
            )
    async def create (self, ctx, date, time, *, args):

        logCommand(ctx)

        game="Warhammer"
        name="2-pers warhammerdagis"
        participants = None

        # Check if the date is valid; stop and return if it is not.
        try:
            datetime.fromisoformat(date)
        except:
            await ctx.send(f'Date give was: {date}. Date must be a valid ISO-8601 string; e.g "2021-02-15".')
            return

        # Check if the time is valid; stop and return if it is not.
        regex = r"^([01]\d|2[0-3]):([0-5]\d)$"
        match = re.compile(regex).match
    
        if not match(time):
            await ctx.send(f'Time given was {time}. Time must be a valid ISO-8601 time; e.g "13:00".')
            return
        
        # Because the event-json has attributes that we make assumptions on, only those attributes that
        # we do not make assumptions on in code may be adjusted.
        # They are whitelisted below.
        allowed_args = ['name', 'game', 'description', 'location']

        # Transform the argument-string into a dict for easier processing.
        arg_dict = dict(token.split("=") for token in shlex.split(args))
    
        # Check the arguments for any attributes that are not in our whitelist.
        disallowed_args = [element for element in arg_dict.keys() if element not in allowed_args]
        
        # If any disallowed arguments were returned, tell the invoker and abort event creation.
        if disallowed_args:

            await ctx.send(f"**Error** - optional argument: {disallowed_args} not allowed. See help for usage.")
            await ctx.send_help(ctx.command)
            return


        # TO-DO: For now, we only have one type of booking. Lets add more types in the future.
        template = "Default"
        if template == "Default":
            
            # Every event must have an ID.
            # Our ID will be a combination of <date>#<4 digits>.
            # The file containing our event will be saved as this id.
            id = f"{date}#{randint(1000,9999)}"

            if participants is None:
                participants = "No one"
            else:
                result = []
                for person in participants:
                    result.append(person.id)

                participants = result

            event={
                    'date': f'{date}',
                    'id': f'{id}',
                    'name': '2-pers warhammerdagis',
                    'game': 'Warhammer40k',
                    'event_type': f'{template}',
                    'location': 'SundbyBunker (Vegagatan 6, Sundbyberg)',
                    'time': f'{time}',
                    'participants': participants,
                    'organiser': ctx.author.name,
                    'description': """
                    *I den grymmörka framtiden, finnes endast krig!*

                    PANDEMIÅTGÄRDER:
                    - Tänk på att tvätta/sprita händera.
                    - Använd mask för att skydda dig och andra.
                    - Hångla inte med främlingar och/eller Islänningar.
                    """
                    }

            # Update the event from the template with our overridden values
            event.update(arg_dict)

            with open(f"{EVENT_DIR}{id}.json", "w") as file:
                json.dump(event,file)

            responseEmbed = self.buildEventEmbed(event)

            # Reply to the user that booked the event.
            await ctx.send(embed=responseEmbed)

            # Post the event to the event channel so that other can see.
            channel = self.bot.get_guild(EVENT_GUILD).get_channel(EVENT_CHANNEL)
            await channel.send(embed=responseEmbed)




def setup(bot):
    bot.add_cog(Events(bot))
