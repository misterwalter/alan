import asyncio
from collections import defaultdict
import datetime
from pprint import pprint
import random
import re
import time

import discord
from emoji import EMOJI_UNICODE_ENGLISH
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from alan_speaks import AlanSpeaks

# Load account token and dads from other file
token = open("token", "r").read().strip()
with open("dads", "r") as dad_file:
    dads = dad_file.readlines()
dads = [x.strip() for x in dads]


# Global Initializations
global client
client = AlanSpeaks()
known_emoji = []

# Process Dictionaries
EMOJI_UNICODE_ENGLISH = {k.lower(): v for k, v in EMOJI_UNICODE_ENGLISH.items()}

# In this house we nice kirby
kirby_url = "https://www.models-resource.com/resources/big_icons/10/9291.png"

# Events =====================================================================
@client.event
async def on_ready():
    print("ALAN RISES")
    print(client.user.name, client.user.mention)
    print(client.user.id)
    print("--------")
    # Responses to try, in order. Each response returns True if it consumes the event,
    # Otherwise False is returned, and the next response is attempted.
    client.alan_responses = [
        WreckYourself(),
        NiceKirby(),
        Standing(),
        IgnoreMe(),
        FeelingsDotExe(),
        Counting(),
        Blizzard(),
        DontBeHasty(),
        Question(),
        LaughAtFools(),
        SaveFromChecks(),
        AlanPls(),
        HomophoneHelper(),
        Oof(),
        PleaseClap(),
        HangOut(),
    ]


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

    for response in client.alan_responses:
        print(type(response).__name__, end=" | ")
        if await response.command(message, lower):
            break
    print()


# These should be their own class
# @client.event
# async def on_reaction_add(reaction, user):
#     print("Reaction Added: " + reaction.emoji)
#     known_emoji.append(reaction.emoji)
#     if (user != client.user) and (kirby_url not in reaction.message.content) and (reaction.message.author.mention != "Wakter#9720"):
#         await reaction.message.remove_reaction(reaction.emoji, client.user)
#     print(f"{len(known_emoji)} emoji known!")


@client.event
async def on_reaction_remove(reaction, user):
    print("Reaction Removed: " + reaction.emoji)
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await reaction.message.add_reaction(reaction.emoji)


# General Utils ==============================================================
async def slow_talk(
    message, response, initial_message="hmmmmmmmmm...", delay=4, spacing=2
):
    msg = await message.channel.send(initial_message)
    await asyncio.sleep(delay)
    for i in range(1, len(response) + 1):
        await msg.edit(content=response[:i])
        await asyncio.sleep(spacing)


# Responses ==================================================================
class WreckYourself:
    lethal_burns = [
        "wreck yourself",
        "get pwned n00b",
        "bussy",
    ]

    death_sounds = [
        "<:oof:780645607990886421>",
        ":exploding_head:",
        "<a:deathclawdance:598347253630894080>",
        "<minecraft death sound>",
    ]

    async def command(self, message, lower):
        for burn in self.lethal_burns:
            if burn in lower:
                await message.channel.send(self.death_sounds[random.randrange(0, len(self.death_sounds))])
                exit()

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

    def __init__(self):
        restr = f"({client.user.id}|Alan).*(fuck off|let me live|go away)"
        self.regex = re.compile(restr, re.IGNORECASE)
        try:
            with open("ignored_users", "r") as ignore_file:
                ignored_lines = ignore_file.readlines()
            self.ignored_users = set([int(x.strip())for x in ignored_lines])
            pprint(self.ignored_users)
        except Exception as e:
            print(e)
            self.ignored_users = set()

    async def command(self, message, lower):
        if str(client.user.id) in lower and message.author.id in self.ignored_users:
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

    def __init__(self):
        self.anal = SentimentIntensityAnalyzer()
        self.sentimantcher = defaultdict(list)
        for e in EMOJI_UNICODE_ENGLISH:
            self.sentimantcher[
                round(
                    self.anal.polarity_scores(e[1:-1].replace("_", " "))["compound"], 2
                )
            ].append(e)
        del self.sentimantcher[0.0]  # Yachttsy

    async def command(self, message, lower):
        reactions_to_send = []
        words = lower.split()
        for word1, word2 in zip(words, words[1:]):
            words.append(f"{word1}_{word2}")
        words = [word for word in words if len(word) > 2]
        # Check single words
        for word in words:
            if f":{word}:" in EMOJI_UNICODE_ENGLISH:
                reactions_to_send.append(f":{word}:")

        # Add sentimental
        score = round(self.anal.polarity_scores(message.content)["compound"], 2)
        reaction = self.sentimantcher[score]
        if reaction:
            reactions_to_send.append(random.choice(reaction))

        for react in reactions_to_send:
            try:
                await message.add_reaction(EMOJI_UNICODE_ENGLISH[react])
            except:
                print(f"FAILED EMOJI: {react}, removing it from our list")
                # TODO: Save the emoji's discord doesn't support between restarts
                reaction.remove(react)
        return False  # Never consume the event

class Counting:

    async def command(self, message, lower):
        if random.randrange(1, 4) == 1 and "count" in message.channel.name:
            try:
                previous_number = int(lower)
                async with message.channel.typing():
                    await asyncio.sleep(random.randrange(1, 4))
                    await message.channel.send(f"{previous_number + 1}{'  xD' if previous_number == 68 or previous_number == 419 else ''}")
                return True
            except ValueError:
                return False
        return False

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
        if "now" in lower and random.randrange(1, 20) == 1:
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
        ("air", "heir"),
        ("aisle", "isle"),
        ("ante-"	,"anti-"),
        ("eye" ,"I"),
        ("bare", "bear"),
        ("be","bee"),
        ("brake", "break"),
        ("buy" ,"by"),
        ("cell", "sell"),
        ("cent", "scent"),
        ("cereal", "serial"),
        ("coarse", "course"),
        ("complement", "compliment"),
        ("dam", "damn"),
        ("dear", "deer"),
        ("die", "dye"),
        ("fair", "fare"),
        ("fir", "fur"),
        ("flour", "flower"),
        ("for", "four"),
        ("hair", "hare"),
        ("heal", "heel"),
        ("hear", "here"),
        ("him", "hymn"),
        ("hole", "whole"),
        ("hour", "our"),
        ("idle", "idol"),
        ("in", "inn"),
        ("knight", "night"),
        ("knot", "not"),
        ("know", "no"),
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


async def get_channel(channel_id):
    return discord.utils.get(client.get_all_channels(), **(dict(id = channel_id)))

@client.event
async def on_voice_state_update(member, before, after):
    print('ON_VOICE_STATE_UPDATE')
    # Never reply to yourself, that's gross.
    if member == client.user:
        print("Das me")
        return

    state_to_use = before and after
    if state_to_use is None or state_to_use.channel is None:
        return

    channel = await get_channel(state_to_use.channel.id)
    if random.randrange(1, 100) == 69 or str(channel) == "General":
        await client.connect_voice(channel)
        await asyncio.sleep(4)
        client.say_this("Oh. Shit. I'm sorry")
        await asyncio.sleep(20)
        await client.disconnect_voice()



class HangOut:

    async def command(self, message, lower):
        if "hang out" in lower and "alan" in lower and message.guild and message.guild.voice_channels:
            voice_channels = message.guild.voice_channels
            await message.channel.send("On my way! 8D")
            for channel in voice_channels:
                if message.author in channel.members:
                    await client.connect_voice(channel)
                    await asyncio.sleep(3)
                    client.say_this(f"Hewwo, {str(message.author).split('#')[0]}, nice to hear you.")
                    await asyncio.sleep(20)
                    await client.disconnect_voice()
                    return True
        return False

class NiceKirby:

    async def command(self, message, lower):
        if kirby_url in message.content or (str(message.author) == "Kirbot#0000"):
            await message.add_reaction("<:nice:774099859346292800>")
            return True
        return False

# Actually kicks things off ==================================================
client.run(token)
