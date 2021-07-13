import time

import discord



class Voice(discord.Client):
    def __init__(self, *args, **kwargs):
        print("init bot")
        super().__init__(*args, **kwargs)
        # self.text_channel_id = 
        # self.text_channel_name = 
        # self.voice_channel_id = 
        # self.voice_channel_name = 
        self.voice_client = None
        self.player = None
        
    async def on_ready(self):
        print("on_ready bot")
        print("\n".join(map(repr, self.get_all_channels())))

        # self.text_channel = discord.utils.get(
        #     self.get_all_channels(),
        #     **(
        #         dict(id=self.text_channel_id)
        #         if self.text_channel_id is not None
        #         else dict(name=self.text_channel_name)
        #     ),
        # )
        # self.voice_channel = discord.utils.get(
        #     self.get_all_channels(),
        #     **(
        #         dict(id=self.voice_channel_id)
        #         if self.voice_channel_id is not None
        #         else dict(name=self.voice_channel_name)
        #     ),
        # )

        print("Logged in to Discord as {} - ID {}".format(self.user.name, self.user.id))
        print("Ready to recieve commands!")

    async def on_voice_state_update(self, *args, **kwargs):
        # super().on_voice_state_update(*args, **kwargs)
        print(f"on_voice_state_update data: {args}::\n::{type(args)}::\n::{kwargs}")

    async def on_message(self, message, timeout=1.0):
        if message.author == self.user:
            return
        messageText = message.content.lower().strip()

        if messageText == "!hi" and self.voice_channel is not None:
            self.voice_client = await self.voice_channel.connect()
            self.voice_client.listen(self.audioSink)
            print("Connected!")

        elif messageText == "!bye" and self.voice_client is not None:
            print("Attempting to hang up from voice channel")
            try:
                self.voice_client.stop()
                await self.voice_client.disconnect()
            except Exception as e:
                print(e)
                time.sleep(timeout)
                await self.voice_client.disconnect()
                self.voice_client = None
                print("Disconnected!")

        elif messageText == "!play":
            audio_source = discord.FFmpegPCMAudio("test.mp3")
            # audio_source = discord.FFmpegPCMAudio("me_talking.mp3")
            if not self.voice_client.is_playing():
                self.voice_client.play(audio_source, after=None)

        elif messageText == "!stop" and self.player is not None:
            self.player.stop()
