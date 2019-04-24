import discord
import datetime
import asyncio
from collections import defaultdict
import random
import re
import requests

# Load account token from other file
token = open("token", "r").read().strip()
dads = [open("dads", "r").read().strip()]

# Global Initializations
client = discord.Client()
known_emoji = []

# Events =====================================================================
@client.event
async def on_ready():
    print('ALAN RISES')
    print(client.user.name, client.user.mention)
    print(client.user.id)
    print('--------')


@client.event
async def on_message(message):
    print("{}:{}{}:{}".format(
        message.author,
        message.guild.name+":" if message.guild else "",
        message.channel,
        message.content,
    ))
    # Never reply to yourself
    if message.author == client.user:
        print("Das me")
        return

    # Most commands need this, might as well cache it
    lower = message.content.lower()

    for response in responses:
        print(response)
        if (await response.command(message, lower)):
            break


# These should be their own class
@client.event
async def on_reaction_add(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await reaction.message.remove_reaction(reaction.emoji, client.user)
    print(F"{len(known_emoji)} emoji known!")

@client.event
async def on_reaction_remove(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await reaction.message.add_reaction(reaction.emoji)


# General Utils ==============================================================
async def slow_talk(message, response, initial_message="hmmmmmmmmm...", delay=5, spacing=2):
    msg = await message.channel.send(initial_message)
    await asyncio.sleep(delay)
    for i in range(len(response)+1):
        await msg.edit(content=response[:i])
        await asyncio.sleep(spacing)


# Responses ==================================================================
class Standing:
    wait_until = datetime.datetime.now()

    async def command(self, message, lower):
        if "stand down" in lower:
            if message.author.mention in dads:
                self.wait_until = datetime.datetime.now() + datetime.timedelta(minutes=random.randrange(10, 1000))
                await message.channel.send(content=f"{message.author.mention} o7")
        elif "stand up" in lower:
            self.wait_until = datetime.datetime.now()
            await message.channel.send(content=f"{message.author.mention} o7")
        if datetime.datetime.now() < self.wait_until:
            print(f"STANDING DOWN UNTIL {self.wait_until}")
            return True
        return False

    
class DontBeHasty:
    async def command(self, message, lower):
        if "now" in lower and random.randrange(1, 10) is 1:
            await slow_talk(
                message,
                "Now, don't be hasty young {}.".format(message.author.mention),
            )
            return True
        return False


class LaughAtFools:
    regex = re.compile("(done)", re.IGNORECASE)
    
    async def command(self, message, lower):
        match = self.regex.search(lower)
        haha = "".join([random.choice(["H", "h"]) + random.choice(["A", "a"]) for c in range(random.randrange(10, 50))])
        if match:
            await slow_talk(
                message,
                haha,
                initial_message=f"\"{match.group(1)}\"",
                delay=3,
                spacing=.5,
            )
            return True
        return False


class SaveFromChecks:
    regex = re.compile("^[cs](\d{1,3})", re.IGNORECASE)
    async def command(self, message, lower):
        if self.regex.match(lower):
            await slow_talk(
                message,
                f"hey {message.author.mention}, just so you know, we're switching over to a nice new simplified system for rolling. Now that we've simplified things and made them simpler, you don't have to roll checks or saves! 8) You just need to roll! You can roll by typing 'r' at the start of your message instead of typing 'c' or 's' at the start of your message like you used to. This was done to make the game more fun! We hope you have a nice day, and you enjoy your thrills and spills in the Imperial Dawn Dice Role Playing Game System! 'Don't just have a good game, have a great game!' -Our Board of Directors, to you.", # NO QA
                initial_message=f"r{message.content[1:]} to lend a little helping hand to {message.author.mention} <3",
            )
            return True
        return False


class AlanPls:
    regex = re.compile("^r(\d{1,3})(.*(pls|please).*)", re.IGNORECASE)

    def make_succ(count):
        result = "**"
        for i in range(count):
            result += f" [{random.randrange(3, 7)}]"
        return result + "**"

    async def command(self, message, lower):
        match = self.regex.match(lower)
        if match and random.randrange(1, 30):
            subject = " re: " + match.group(2) if match.group(2) else ""
            response_string = "**{0}** got {1} successes {2}{3}".format(
                message.author.mention,
                match.group(1),
                make_succ(int(match.group(1))),
                subject,
            )

            await client.send_message(
                message.channel,
                response_string,
            )
            return True
        return False

# Responses to try, in order. Each response returns True if it consumes the event,
# Otherwise False is returned, and the next response is attempted.
responses = [
    Standing(),
    DontBeHasty(),
    LaughAtFools(),
    SaveFromChecks(),
    AlanPls(),
]
# Actually kicks things off ==================================================
client.run(token)
