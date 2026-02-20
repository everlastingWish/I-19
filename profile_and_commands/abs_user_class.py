from abc import ABC, abstractmethod
import requests
from datetime import datetime, time
from zoneinfo import ZoneInfo

from util import webhook_edit

class abs_user_class(ABC):
    guildMap = None

    name = ""
    pfp = ""        #this needs to be a local img path
    webhook_name = ""
    memory_obj = "" # ...placeholder for now
    time_start = None   #inclusive
    time_end = None     #exclusive
    zone = None     # ZoneInfo(...)
    #constructor
    def __init__(self, guildmap, name, pfp, webhook_name, zone, memory_obj=None, time_start=None, time_end=None):
        with open(pfp, 'rb') as image_file:
            avatar_bytes = image_file.read()
        self.guildMap = guildmap
        self.name = name
        self.pfp = avatar_bytes
        self.webhook_name = webhook_name
        self.memory_obj = memory_obj
        self.time_start = time_start
        self.time_end = time_end
        self.zone = zone

    #methods
    def isAsleep(self) -> bool:
        # return (datetime.now(self.zone).time() < self.time_start) or (datetime.now(self.zone).time() >= self.time_end) 
        current_time = datetime.now(self.zone).time()
    
        # If time_start < time_end, its a normal day range (e.g: 9am - 9pm)
        if self.time_start < self.time_end:
            return current_time < self.time_start or current_time >= self.time_end
        
        # If time_start > time_end, the range crosses midnight (e.g: 9pm - 9am)
        # the bot is AWAKE from time_start to midnight AND midnight to time_end

        # its ASLEEP when its between time_end and time_start
        else:
            return self.time_end <= current_time < self.time_start


        
    async def split_and_send_message(self, msg, ctx, chunk_size=2000):
        #if ratelimited
        if msg == "":
            return
        # If message is shorter than chunk_size, send it directly
        if len(msg) <= chunk_size:
            await webhook_edit.send_message_via_webhook(ctx,self.webhook_name,self.pfp,self.name,msg)
            return
    
        # split msg into chunks
        chunks = []
        for i in range(0, len(msg), chunk_size):
            # Get chunk of appropriate size
            chunk = msg[i:i + chunk_size]
        
            # if mid word and its not the last chunk,
            # try to split at the last space
            if i + chunk_size < len(msg) and msg[i + chunk_size].isalnum():
                last_space = chunk.rfind(' ')
                if last_space != -1:  #if found a space
                    # move the partial word to the next chunk
                    chunk = chunk[:last_space]
                    
                    # adjust the starting point of the next chunk
                    i = i + last_space - chunk_size
            chunks.append(chunk.strip())
    
    # send each chunk
        for index, chunk in enumerate(chunks):
            if len(chunks) > 1:
                chunk = f"[{index + 1}/{len(chunks)}]\n{chunk}"
    
            await webhook_edit.send_message_via_webhook(ctx,self.webhook_name,self.pfp,self.name,chunk)

    async def send_help(self,title,content,color,ctx):
        await webhook_edit.send_embed_webhook(ctx,title,content,color,self.webhook_name,self.pfp,self.name)

    async def send_text_image(self,ctx, text, file):
        await webhook_edit.send_message_via_webhook(ctx,self.webhook_name,self.pfp,self.name,text, file)