from profile_and_commands.no_akashi import no_akashi
from profile_and_commands.no_chen import no_chen

class no_useage_class():
    current_user_ptr = None

    def __init__(self, guildmap, voice_instance, comfy_client):
        self.akashi = no_akashi(guildmap, voice_instance, comfy_client) 
        self.chen = no_chen(guildmap, voice_instance, comfy_client)

        self.current_user_ptr = self.chen                

    def switch_check(self,ctx):
        # pass
        if self.current_user_ptr.isAsleep():
            # switch to the other bot and clear memory

            guildID = str(ctx.guild.id)

            if self.current_user_ptr is self.akashi:
                self.current_user_ptr = self.chen
                self.current_user_ptr.guildMap[guildID]["secondChanceOBJ"].self_reset()
            else:
                self.current_user_ptr = self.akashi
                self.current_user_ptr.guildMap[guildID]["geminiOBJ"].geminiReset(True)
            
            bot_name = "Chen" if self.current_user_ptr is self.chen else "Akashi"
            print(f"Switched current user to {bot_name}.")
    
    async def absolute_useage(self,command, ctx):
        self.switch_check(ctx)
        method = getattr(self.current_user_ptr, command)
        await method(ctx)
    
    async def only_chen_useage(self,command, ctx):
        self.switch_check(ctx)
        if self.current_user_ptr is not self.chen:
            return  # Do nothing if the current user is not chen
        method = getattr(self.chen, command)
        await method(ctx)

    async def only_aka_useage(self,command, ctx):
        self.switch_check(ctx)
        if self.current_user_ptr is not self.akashi:
            return  # Do nothing if the current user is not akashi
        method = getattr(self.akashi, command)
        await method(ctx)
