"""His most glourious incarnation yeT"""

from collections import defaultdict
import random
import re

import discord

class Alan(discord.Client):

    def activate(self):
        with open(".token", "r") as file:
            token = file.read().strip()
        with open("dads", "r") as dad_file:
            dads = dad_file.readlines()
        self.dads = [x.strip() for x in dads]
        self.run(token)

    async def on_ready(self):
        print("ooooOOOOOooooOOOOOooooo Gooooood Morningggggggggggggg!!!\nIt's", self.user)

    async def on_message(self, message):
        print("{}:{}{}:{}".format(
            message.author,
            message.guild.name+":" if message.guild else "",
            message.channel,
            message.content,
        ))
        if message.author == self.user:
            return
        
        if message.content == "o/":
            print(self.dads)
            print(message.author.mention)
            await message.channel.send("\\o" if message.author.mention in self.dads else "_o")
        elif message.content == "o7":
            await message.channel.send("o7")

intents = discord.Intents.default()
intents.message_content = True
client = Alan(intents=intents)
client.activate()