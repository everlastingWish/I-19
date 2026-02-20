#libs
from discord.ext import commands
from dotenv import load_dotenv
import discord
import asyncio
import json
import os
import re
import io

# custom func
from src.AI_model_classes.gemini_class.gemini_AI import gemini_ai
from econd_chance import second_chance

from util import text_mod
from util.no_useage_class import no_useage_class
from util import webhook_edit
from util.json_to_map import json_to_map
from util import voice_channel
from util.comfyClient import ComfyUIClient

load_dotenv("rss/no_rss/.env")                               # Load environment variables from .env file
with open('rss/no_rss/.json','r') as file:                               # fix?
    data = json.load(file)
ownerID = data['friend']

intents = discord.Intents.default()
intents.message_content = True                              #ut

client = commands.Bot(
    command_prefix = '=',
    owner_ids = ownerID,
    help_command = None,
    strip_after_prefix = True,
    intents = intents
)
guildMap = {}


GEMINI_API_KEY = os.getenv('gemToken')                                   #global gemini guide
REQUESTS_PER_MINUTE = int(os.getenv('REQUESTS_PER_MINUTE'))

lava_host = os.getenv('lava_host')
lava_port = int(os.getenv('lava_port'))
lava_pass = os.getenv('lava_pass')
comfy_address = os.getenv('server_address')
instruction = os.getenv('instruction')
model_path = os.getenv('model_path')
max_mem_token = int(os.getenv('max_mem_token'))

# update guildMap
#acceleration
@client.event
async def on_ready(): 
    activity = discord.CustomActivity(
            name='Custom Status',
            state="type `=help` for commands",
        )
    await client.change_presence(activity=activity)
    webhook_edit.setup_db()

    global combined_pattern 
    combined_pattern = text_mod.pattern_maker(data["nicknames"])
    tempMap = json_to_map("rss/no_rss/.json")
    print('started\n{0.user} is online and connected to '.format(client) + str(len(client.guilds)) + " servers: ")
    async for guild in client.fetch_guilds(limit=250):
        guildMap[str(guild.id)] = {
                                    "geminiOBJ": gemini_ai(tempMap, GEMINI_API_KEY, REQUESTS_PER_MINUTE),
                                    "secondChanceOBJ": second_chance(max_mem_token, instruction, model_path, combined_pattern, client),
                                    "first_ping": True
                                    }

        print(" - " + guild.name + " - " + str(guild.id))                #list every guild it is in
    
    global voice_instance
    global comfy_client

    voice_instance = voice_channel.VoiceCommands(client)
    await voice_instance.setup_node(lava_host, lava_port, lava_pass)
    await client.add_cog(voice_instance)

    comfy_client = ComfyUIClient(comfy_address)

    global useage_interface 
    useage_interface= no_useage_class(guildMap, voice_instance, comfy_client)



@client.event
async def on_message(message):
    if message.author.bot or isinstance(message.channel, discord.channel.DMChannel):
        return
    
    ctx = await client.get_context(message)
    if ctx.command:
        await client.process_commands(message)
        return
    message_lower = message.content.lower()
    if "@everyone" in message_lower or "@here" in message_lower:
        return
    message_content = text_mod.replace_emojis_pings_inverse(text=message.content, users=message.guild.members, emojis=message.guild.emojis) + ' '
    if client.user.mentioned_in(message) or re.search(combined_pattern, message_content):
        ctx = await client.get_context(message)
        await useage_interface.absolute_useage("um", ctx)
    elif " chen" in ' ' +message_lower:
        ctx = await client.get_context(message)
        await useage_interface.only_chen_useage("um", ctx)
    elif " chii " in ' ' + message_lower:
        ctx = await client.get_context(message)
        await useage_interface.only_aka_useage("um", ctx)

command_names = ["draw", "help", "ping", "join", "play","leave"]

@client.command(name="um", aliases=command_names)
async def command_func(ctx):
    # ctx.invoked_with is the actual command name used (e.g: 'um', 'draw', 'play', etc.)
    current_name = ctx.invoked_with
    await useage_interface.absolute_useage(current_name, ctx)

@client.command()
@commands.is_owner()
async def cleanup(ctx):
    await webhook_edit.cleanup_all_webhooks(ctx)
    return

@client.command()
@commands.is_owner()
async def sudocleanup(ctx):
    await webhook_edit.delete_all_webhook_entries(ctx)
    return

@client.command()
@commands.is_owner()
async def selfd(ctx):
    MESSAGE_ID = text_mod.splitUserMsg("=selfd", ctx.message.content).strip()
    await webhook_edit.delete_message(ctx, MESSAGE_ID)
    return

@client.command()
@commands.is_owner()
async def cl(ctx):
    file = open("rss/no_change_log.txt", "r")
    embed = discord.Embed(title = "change log", description = file.read(), color = 000000)
    file.close()
    image_file = discord.File("rss/cover.png", filename="cover.png")
    embed.set_image(url="attachment://cover.png")
    await ctx.send(embed=embed, file=image_file)

# sends a message for every pics in a folder using a webhook,
# @client.command()
# @commands.is_owner()
# async def avatarTEST(ctx):
#     folder_path = "rss/no_rss"
#     image_file = "rss/cover.png"
#     username = "I-19"
#     message_text = ("")
#     with open(image_file, "rb") as f:
#         picture_by = f.read()
#     for all files  
#     for filename in os.listdir(folder_path):
#         if filename.lower().endswith(".png") or filename.lower().endswith(".jpg"):
#             file_path = os.path.join(folder_path, filename)
#             # Read the JPG bytes to use as the profile picture
#             with open(file_path, "rb") as f:
#                 pfp_bytes = f.read()
            
#             # Send the message
#             await webhook_edit.send_message_via_webhook(
#                 ctx, 
#                 webhook_name="temp test", 
#                 pfp_bytes=pfp_bytes, 
#                 username=username, 
#                 message_content=message_text,
#                 file = discord.File(
#                         fp=io.BytesIO(picture_by),
#                         filename="if image is bad it means your prompt is bad.png"
#                     )
#             )
#             await webhook_edit.delete_all_webhook_entries(ctx)
#             print(f"Sent message for {filename}")
#     await webhook_edit.delete_all_webhook_entries(ctx)
#     print("Cleanup complete.")
client.run(os.getenv('token')) 