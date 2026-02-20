from abc import ABC, abstractmethod
import discord

# all methods :D
class abs_command_class(ABC):
    voice_instance = None
    comfy_client = None
    def __init__(self, voice_instance, comfy_client):
        self.voice_instance = voice_instance
        self.comfy_client = comfy_client

    @abstractmethod
    async def um(self, ctx):
        pass

    @abstractmethod
    async def draw(self, ctx):
        pass

    @abstractmethod
    async def help(self,ctx):
        pass

    @abstractmethod
    async def ping(self,ctx):
        pass

    @abstractmethod
    async def join(self,ctx):
        await self.voice_instance.join_voice_channel(ctx)

    @abstractmethod
    async def play(self,ctx):
        inputs = ctx.message.content.split("=play ")[1]
        await self.voice_instance.play(ctx, inputs)

    @abstractmethod
    async def leave(self,ctx):
        await self.voice_instance.leave_voice_channel(ctx)