from datetime import datetime, time
from zoneinfo import ZoneInfo 
from profile_and_commands.abs_user_class import abs_user_class
from profile_and_commands.abs_command_class import abs_command_class
from textFuncGemini import textFunctionGemini
from draw_func import draw_func
from util import text_mod
class no_chen (abs_user_class, abs_command_class):
    def __init__(self, guildmap, voice_instance, comfy_client, name="Chen", pfp="rss/no_rss/no_chen.webp", webhook_name="Chen", zone=ZoneInfo("America/New_York"), memory_obj=None, time_start=time(9, 0), time_end=time(21, 0)):
 
        abs_user_class.__init__(
            self,
            guildmap=guildmap,
            name=name, 
            pfp=pfp, 
            webhook_name=webhook_name, 
            zone=zone,
            time_start=time_start,
            time_end=time_end,
        )

        abs_command_class.__init__(
            self,
            voice_instance=voice_instance,
            comfy_client=comfy_client
        )
    
    async def um(self, ctx):
        async with ctx.channel.typing():
            response = await self.guildMap[str(ctx.guild.id)]["secondChanceOBJ"].text_func(ctx.message,self.comfy_client)
        await self.split_and_send_message(response,ctx)

    async def draw(self, ctx):
        await self.split_and_send_message("i can't draw yet!",ctx)

    async def help(self, ctx):
        with open("rss/no_chen_help.txt", "r") as file:
            content = file.read()
        color = 0xFF0000
        title = ""
        await self.send_help(title,content,color,ctx)

    async def ping(self, ctx):
        response = "yay"
        await self.split_and_send_message(response,ctx)

    async def join(self,ctx):
        await super().join(ctx)
    
    async def play(self,ctx):
        await super().play(ctx)

    async def leave(self,ctx):
        await super().leave(ctx)