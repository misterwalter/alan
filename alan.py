import discord
import asyncio
from collections import defaultdict
import random
import re
import requests

# Load account token from other file
token = open("token", "r").read().strip()
dads = [open("dads", "r").read().strip()]
eng_dict_file = 'eng_dict_lower.txt'
global eng_dict
eng_dict = set()


# Global Initializations
client = discord.Client()
known_emoji = []
save_from_checks_regex = re.compile("^[cs](\d{1,3})", re.IGNORECASE)
alan_pls_regex = re.compile("^r(\d{1,3})(.*(pls|please).*)", re.IGNORECASE)
words_regex = re.compile("([a-z]{2,})", re.IGNORECASE)

@client.event
async def on_ready():
    print('ALAN RISES')
    print(client.user.name, client.user.mention)
    print(client.user.id)
    load_eng_dict( eng_dict_file )
    print('--------')


@client.event
async def on_message(message):
    print("{}:{}{}:{}".format(
        message.author,
        message.server.name+":" if message.server else "",
        message.channel,
        message.content,
    ))
    if message.author == client.user:
        print("Das me")
        return

    lower = message.content.lower()

    responses = [
        dont_be_hasty,
        dont_be_pasty,
        save_from_checks,
        alan_pls,
    ]

    for response in responses:
        if (await response(message, lower)):
            break


@client.event
async def on_reaction_add(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await client.remove_reaction(reaction.message, reaction.emoji, client.user)

@client.event
async def on_reaction_remove(reaction, user):
    known_emoji.append(reaction.emoji)
    if user != client.user:
        await client.add_reaction(reaction.message, reaction.emoji)

# Take your time.
async def slow_talk(message, response, initial_message="hmmmmmmmmm..."):
    msg = await client.send_message(message.channel, initial_message)
    await asyncio.sleep(5)
    for i in range(len(response)+1):
        await client.edit_message(msg, response[:i])
        await asyncio.sleep(2)


# Reeponses
async def dont_be_hasty(message, lower):
    if "now" in lower and random.randrange(1, 10) is 1:
        await slow_talk(
            message,
            "Now, don't be hasty young {}.".format(message.author.mention),
        )
        return True
    return False

async def dont_be_pasty(message, lower):
    if "white" in lower and random.randrange(1, 20) is 1:
        await slow_talk(
            message,
            "Now, don't be pasty young {}.".format(message.author.mention),
        )
        return True
    return False

async def save_from_checks(message, lower):
    if save_from_checks_regex.match(lower):
        await slow_talk(
            message,
            f"hey {message.author.mention}, just so you know, we're switching over to a nice new simplified system for rolling. Now that we've simplified things and made them simpler, you don't have to roll checks or saves! 8) You just need to roll! You can roll by typing 'r' at the start of your message instead of typing 'c' or 's' at the start of your message like you used to. This was done to make the game more fun! We hope you have a nice day, and you enjoy your thrills and spills in the Imperial Dawn Dice Role Playing Game System! 'Don't just have a good game, have a great game!' -Our Board of Directors, to you.",
            initial_message=f"r{message.content[1:]} to lend a little helping hand to {message.author.mention} <3",
        )
        return True
    return False


def make_succ(count):
    result = "**"
    for i in range(count):
        result += f" [{random.randrange(3, 7)}]"
    return result + "**"

async def alan_pls(message, lower):
    match = alan_pls_regex.match(lower)
    if match and random.randrange(1, 3):
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

async def definition_looks(message, lower):
    match = re.findall( words_regex, lower )
    if match and random.randrange(1,10) is 1:
        for word in match:
            definition = check_word_exists( word )
            if definition:
                response_string = f"You said {word}, but that's not in the dictionary, does this help?\n{definition}"
                await client.send_message( 
                    message.channel,
                    response_string
                )
    return True

def load_eng_dict( dict_file ):
    global eng_dict
    with open( dict_file, 'r', encoding='latin-1') as f:
        words = f.readlines()
        eng_dict = set( [ w.strip() for w in words ]  )
        #[ print( w ) for w in eng_dict ]

def check_word_exists( word ):
    definition = ""
    print( len( eng_dict ) )
    if word not in eng_dict:
        params = ( ('term', word ), )
        response = requests.get( 'http://api.urbandictionary.com/v0/define', params=params ).json()
        if response:
           definition = response[ 'list' ][ random.randrange( 0, len( response) ) ][ 'definition' ]
    return definition


# Actually kicks things off
client.run(token)
