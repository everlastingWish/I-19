from datetime import datetime, time
from zoneinfo import ZoneInfo 
from profile_and_commands.abs_user_class import abs_user_class
from profile_and_commands.abs_command_class import abs_command_class
from textFuncGemini import textFunctionGemini
from draw_func import draw_func
from util import text_mod
class no_akashi (abs_user_class, abs_command_class):
    def __init__(self, guildmap, voice_instance, comfy_client, name="Chii", pfp="rss/no_rss/no_akashi.png", webhook_name="Chii", zone=ZoneInfo("America/New_York"), memory_obj=None, time_start=time(21, 0), time_end=time(9, 0)):
 
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
        response = await textFunctionGemini(ctx.message,self.guildMap)
        await self.split_and_send_message(response,ctx)

    async def draw(self, ctx):
        async with ctx.channel.typing():
            prompt = ctx.message.content.split("=draw ")[1]

            # blacklist words
            keywords = {
                'nsfw', 'nude', 'naked', 'pussy', 
                'vagina', 'dick', 'cock', 'penis', 
                'loli', 'shota', 'child', 'children'
            }
            if text_mod.keyword_matcher(keywords, prompt):
                await self.split_and_send_message(f"{ctx.author.mention} Watch your language.", ctx)
                return
            response = "there..."
            temp_prompt = prompt.split(',')
            if len(temp_prompt) < 6:
                response = "i don't know, what do you want from me nya?? your instructions suck so bad."
            await self.send_text_image(ctx, response, await draw_func(prompt,self.comfy_client))

    async def help(self, ctx):
        title = "commands nya"
        with open("rss/no_aka_help.txt", "r") as file:
            content = file.read()
        color = 0x155835
        await self.send_help(title,content,color,ctx)

    async def ping(self, ctx):
        if self.guildMap[str(ctx.guild.id)]["first_ping"]:
            self.guildMap[str(ctx.guild.id)]["first_ping"] = False
            response = "..."
        else: 
            response = "...?"
        await self.split_and_send_message(response,ctx)

    async def join(self,ctx):
        await super().join(ctx)
    
    async def play(self,ctx):
        await super().play(ctx)

    async def leave(self,ctx):
        await super().leave(ctx)