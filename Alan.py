import asyncio
from collections import defaultdict
import datetime
from pprint import pprint
import random
import re

import discord
from emoji import EMOJI_ALIAS_UNICODE
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load account token and dads from other file
token = open("token", "r").read().strip()
with open("dads", "r") as dad_file:
    dads = dad_file.readlines()
dads = [x.strip() for x in dads]


# Global Initializations
global client
client = discord.Client()
known_emoji = []

# Process Dictionaries
EMOJI_ALIAS_UNICODE = {k.lower(): v for k, v in EMOJI_ALIAS_UNICODE.items()}


# Events =====================================================================
@client.event
async def on_ready():
    print("ALAN RISES")
    print(client.user.name, client.user.mention)
    print(client.user.id)
    print("--------")


@client.event
async def on_message(message):
    print(
        "{}:{}{}:{}\n{}".format(
            message.author,
            message.guild.name + ":" if message.guild else "",
            message.channel,
            str(datetime.datetime.now()),
            message.content,
        )
    )
    # Never reply to yourself
    if message.author == client.user:
        print("Das me")
        return

    # Most commands need this, might as well cache it
    lower = message.content.lower()

    for response in responses:
        print(type(response).__name__, end=" | ")
        if await response.command(message, lower):
            break
    print()


# These should be their own class
@client.event
async def on_reaction_add(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await reaction.message.remove_reaction(reaction.emoji, client.user)
    print(f"{len(known_emoji)} emoji known!")


@client.event
async def on_reaction_remove(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await reaction.message.add_reaction(reaction.emoji)


# General Utils ==============================================================
async def slow_talk(
    message, response, initial_message="hmmmmmmmmm...", delay=4, spacing=2
):
    msg = await message.channel.send(initial_message)
    await asyncio.sleep(delay)
    for i in range(len(response) + 1):
        await msg.edit(content=response[:i])
        await asyncio.sleep(spacing)


# Responses ==================================================================
class Standing:
    wait_until = datetime.datetime.now()

    async def command(self, message, lower):
        if "stand down" in lower:
            if message.author.mention in dads:
                self.wait_until = datetime.datetime.now() + datetime.timedelta(
                    minutes=random.randrange(10, 1000)
                )
                await message.channel.send(content=f"{message.author.mention} o7")
        elif "stand up" in lower:
            self.wait_until = datetime.datetime.now()
            await message.channel.send(content=f"{message.author.mention} o7")
        if datetime.datetime.now() < self.wait_until:
            print(f"STANDING DOWN UNTIL {self.wait_until}")
            return True
        return False


class IgnoreMe:
    regex = re.compile(f"Alan.*(fuck off|let me live|go away)", re.IGNORECASE)

    def __init__(self):
        try:
            with open("ignored_users", "r") as ignore_file:
                ignored_lines = ignore_file.readlines()
            self.ignored_users = set([x.strip() for x in ignored_lines])
            pprint(self.ignored_users)
        except Exception as e:
            print(e)
            self.ignored_users = set()

    async def command(self, message, lower):
        print(f"MENTION: {client.user.mention}")
        print(f"LOWER: {lower}")
        if client.user.mention in lower and message.author.id in self.ignored_users:
            self.ignored_users.remove(message.author.id)
            self.save()
            await message.channel.send(f"{message.author.mention}!!!")
            await asyncio.sleep(1)
            await message.channel.send("<3")
            return False
        elif message.author.id in self.ignored_users:
            return True  # Eat the event
        elif self.regex.search(lower):
            await message.channel.send(content="Oh shit, I'm sorry.")
            self.ignored_users.add(message.author.id)
            self.save()
            return True
        else:
            return False

    def save(self):
        with open("ignored_users", "w") as ignore_file:
            for ignore_id in self.ignored_users:
                ignore_file.write(str(ignore_id) + "\n")


class FeelingsDotExe:

    retry_count = 5

    def __init__(self):
        self.anal = SentimentIntensityAnalyzer()
        self.sentimantcher = defaultdict(list)
        for e in EMOJI_ALIAS_UNICODE:
            self.sentimantcher[
                round(
                    self.anal.polarity_scores(e[1:-1].replace("_", " "))["compound"], 2
                )
            ].append(e)
        del self.sentimantcher[0.0]  # Yachttsy
        print(f"SENTIMATNCHDFSKJ IS {len(self.sentimantcher)} LONG")
        pprint(self.sentimantcher)

    async def command(self, message, lower):
        reactions_to_send = []
        words = lower.split()
        for word1, word2 in zip(words, words[1:]):
            words.append(f"{word1}_{word2}")
        words = [word for word in words if len(word) > 2]
        # Check single words
        for word in words:
            if f":{word}:" in EMOJI_ALIAS_UNICODE:
                reactions_to_send.append(f":{word}:")

        # Add sentimental
        reaction = self.sentimantcher[
            round(self.anal.polarity_scores(message.content)["compound"], 2)
        ]
        print(reaction)
        if reaction:
            reactions_to_send.append(random.choice(reaction))

        for react in reactions_to_send:
            try:
                await message.add_reaction(EMOJI_ALIAS_UNICODE[react])
            except:
                print(f"FAILED EMOJI: {react}")
        return False  # Never consume the event

class Blizzard:
    keywords = [
        "blizzard",
        "diablo",
        "hearthstone",
        "heroes of the storm", # Yeah, cuz people are gonna type all that out.
        "hots",
        "overwatch",
        "starcraft",
        "nba",
        "warcraft",
    ]

    async def command(self, message, lower):
        for keyword in self.keywords:
            if keyword in lower:
                await message.add_reaction("🇭🇰")
                return True
        return False

class DontBeHasty:
    async def command(self, message, lower):
        if "now" in lower and random.randrange(1, 20) is 1:
            await slow_talk(
                message, "Now, don't be hasty young {}.".format(message.author.mention)
            )
            return True
        return False


class LaughAtFools:
    regex = re.compile("(done)", re.IGNORECASE)

    async def command(self, message, lower):
        match = self.regex.search(lower)
        if match and random.randrange(1, 10) == 1:
            haha = "".join(
                [
                    random.choice(["H", "h"]) + random.choice(["A", "a"])
                    for c in range(random.randrange(10, 50))
                ]
            )
            await slow_talk(
                message,
                haha,
                initial_message=f'"{match.group(1)}"',
                delay=3,
                spacing=0.5,
            )
            return True
        return False


class SaveFromChecks:
    regex = re.compile("^[cs](\d{1,3})", re.IGNORECASE)

    async def command(self, message, lower):
        if self.regex.match(lower):
            await slow_talk(
                message,
                f"hey {message.author.mention}, just so you know, we're switching over to a nice new simplified system for rolling. Now that we've simplified things and made them simpler, you don't have to roll checks or saves! 8) You just need to roll! You can roll by typing 'r' at the start of your message instead of typing 'c' or 's' at the start of your message like you used to. This was done to make the game more fun! We hope you have a nice day, and you enjoy your thrills and spills in the Imperial Dawn Dice Role Playing Game System! 'Don't just have a good game, have a great game!' -Our Board of Directors, to you.",  # NO QA
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
        if match and random.randrange(1, 30) == 1:
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
        if random.randrange(1, 50) != 1:
            return False  # Good jeezy this got annoying fast

        lower_split = lower.split()
        matches = [
            cluster
            for cluster in self.homophones
            if [word for word in cluster if word in lower_split]
        ]
        if matches:
            correction = random.choice(
                [option for option in matches[0] if option not in lower_split]
            )
            await message.channel.send(f"{message.author.mention} *{correction}")
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
        if match and random.randrange(1, 5) == 1:
            commiseration = random.choice(self.commiserations)
            if commiseration[1]:
                await slow_talk(
                    message,
                    commiseration[0].format(loser=match.group(1)),
                    initial_message=commiseration[0].format(loser=match.group(1))[0],
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


class PleaseClap:
    async def command(self, message, lower):
        slow = "slow clap" in lower
        if "please clap" in lower or slow:
            text = ":clap:"
            msg = await message.channel.send(text)
            try:
                while True:
                    text += ":clap:"
                    await msg.edit(content=text)
                    if slow:
                        await asyncio.sleep(1)
                        print("SLOW CLAPPING")
                    else:
                        await asyncio.sleep(0.3)
                        print("CLAPPING")
            except Exception:
                return True
            return True
        return False


class StealFace:
    async def command(self, message, lower):
        if random.randrange(1, 500) == 1:
            member_me = message.author.guild.me
            my_name = member_me.name
            new_name = message.author.nick or message.author.name
            await member_me.edit(nick=new_name)

            try:
                await message.author.edit(nick=my_name)
            except Exception as e:
                print(
                    f"Tried to steal {message.author.nick}'s face, but only pirated it."
                )
            return True
        return False


# Responses to try, in order. Each response returns True if it consumes the event,
# Otherwise False is returned, and the next response is attempted.
responses = [
    Standing(),
    IgnoreMe(),
    FeelingsDotExe(),
    Blizzard(),
    DontBeHasty(),
    Question(),
    LaughAtFools(),
    SaveFromChecks(),
    AlanPls(),
    HomophoneHelper(),
    Oof(),
    PleaseClap(),
    StealFace(),
]
# Actually kicks things off ==================================================
client.run(token)
