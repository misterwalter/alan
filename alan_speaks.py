import asyncio
import random
import time

import pyttsx3
import discord

# Global Initializations
engine = pyttsx3.init()


class AlanSpeaks(discord.Client):

    def __init__(self):
        super().__init__()
        self.voice_client = None
        self.alan_responses = []
        self.seconds_per_word = 0.7
        # For some reason Alan won't start with more than one phrase
        self.phrases = {
          "classic.mp3": "Oh. Shit. I'm sorry",
          # "personal.mp3": "Heewwo. name. redacted. It is nice to hear you.",
        }
        self.generate_phrases(self.phrases)

    def generate_phrases(self, phrases):
        for name, phrase in phrases.items():
            print(f"Generating phrase {name}: {phrase}")
            engine.save_to_file(phrase, name)
            engine.runAndWait()
            engine.stop()
            time.sleep(5)

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
        if self.voice_client.is_playing():
            return

        if phrase in self.phrases:
            audio_source = discord.FFmpegPCMAudio(phrase)
            self.voice_client.play(audio_source)
