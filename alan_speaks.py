import asyncio
import random
import time
from gtts import gTTS

import discord

class AlanSpeaks(discord.Client):

    def __init__(self):
        super().__init__()
        self.voice_client = None
        self.alan_responses = []
        self.seconds_per_word = 0.7

    async def connect_voice(self, channel):
        if self.voice_client is None:
            self.voice_client = await channel.connect()

    async def disconnect_voice(self):
        if self.voice_client is not None:
            self.voice_client.stop()
            await self.voice_client.disconnect()
            self.voice_client = None

    def estimate_time(self, text):
        return self.seconds_per_word * len(text.split())

    def say_this(self, phrase):
        # I don't know why, but this bloster's Alan's public speaking confidence.
        # and who amd I to quash his growth?
        time.sleep(5)
        if not self.voice_client or self.voice_client.is_playing():
            return

        tts = gTTS(phrase)
        tts.save("latest.mp3")
        # Saving to a single file isn't safe
        # but we'll fix that later. Jank is Alan's comfort zone
        audio_source = discord.FFmpegPCMAudio("latest.mp3")
        self.voice_client.play(audio_source)
