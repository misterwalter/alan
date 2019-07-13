import discord
import datetime
import asyncio
from collections import defaultdict
import random
import re
import requests

# Load account token and dads from other file
token = open("token", "r").read().strip()
with open("dads", "r") as dad_file:
    dads = dad_file.readlines()
dads = [x.strip() for x in dads] 


# Global Initializations
global client
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
    print("{}:{}{}:{}\n{}".format(
        message.author,
        message.guild.name+":" if message.guild else "",
        message.channel,
        str(datetime.datetime.now()),
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

    def make_succ(self, count):
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
                self.make_succ(int(match.group(1))),
                subject,
            )

            await message.channel.send(response_string)
            return True
        return False


class HomophoneHelper:

    homophones = [
        ("then", "than"),
        ("there", "their", "they're"),
        ("were", "we're"),
        ("your", "you're"),
    ]

    last = datetime.datetime.now()

    async def command(self, message, lower):
        lower_split = lower.split()
        matches = [cluster for cluster in self.homophones if [word for word in cluster if word in lower_split]]
        if matches:
            correction = random.choice([option for option in matches[0] if option not in lower_split])
            await message.channel.send(
                f"{message.author.mention} *{correction}",
            )
            return True
        return False


class Oof:
    regex = re.compile("^\*\*(<@[0-9]+>)\*\* got 0", re.IGNORECASE)

    commiserations = [
        # (Response, whether to say slowly),
        ("ooof", False),
        ("That's rough, {loser}", False),
        ("F", False),
        ("F F F F F F F F F F F F F F F F F F F F F F F F", True),
        ("You tried, I guess", False),
        (":(", False),
        ("Life is hard", False),
    ]

    async def command(self, message, lower):
        match = self.regex.match(lower)
        if match:
            commiseration = random.choice(self.commiserations)
            if commiseration[1]:
                await slow_talk(
                    message,
                    commiseration[0].format(loser=match.group(1)),
                    initial_message=commiseration[0].format(loser=match.group(1))[0]
                )
            else:
                await message.channel.send(
                    commiseration[0].format(loser=match.group(1))
                )
            return True
        return False

class Question:

    defiance = [
        # (Response, whether to say slowly),
        ("{loser} No.", False),
        ("{loser} k", False),
        ("{loser} hmmmmmmmmmmmmm...let me think about it....", True),
    ]

    async def command(self, message, lower):
        regex = re.compile(f"^{client.user.mention}.*[?!]", re.IGNORECASE)
        match = regex.match(lower)
        if match and random.randrange(1, 3) == 1:
            defiance = random.choice(self.defiance)
            if defiance[1]:
                await slow_talk(
                    message,
                    defiance[0].format(loser=message.author.mention),
                    initial_message="uhhhhhhh",
                )
            else:
                await message.channel.send(
                    defiance[0].format(loser=message.author.mention)
                )
            return True
        return False

class StealFace:

    async def command(self, message, lower):
        if random.randrange(1, 5) == 1:
            member_me = message.author.guild.me
            my_name = member_me.name
            await member_me.edit(nick=message.author.nick)

            try:
                await message.author.edit(nick=my_name)
            except Exception as e:
                print(f"Tried to steal {message.author.nick}'s face, but only pirated it.")
            return True
        elif random.randrange(1, 15) == 1:
            await message.author.guild.me.edit(nick="")
        return False

# Responses to try, in order. Each response returns True if it consumes the event,
# Otherwise False is returned, and the next response is attempted.
responses = [
    Standing(),
    DontBeHasty(),
    Question(),
    LaughAtFools(),
    SaveFromChecks(),
    AlanPls(),
    HomophoneHelper(),
    Oof(),
    StealFace(),
]
# Actually kicks things off ==================================================
client.run(token)
