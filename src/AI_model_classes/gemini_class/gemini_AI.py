import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_class import ai
from util import text_mod
from datetime import datetime, timedelta
from google import genai
from google.genai import Client
from google.genai import types

import requests
from io import BytesIO
from PIL import Image


from util.mood_changer import MoodSystem

# global, so only create 1 instance
class gemini_ai(ai):
    def __init__(self, tempMap, api_key, REQUESTS_PER_MINUTE):

        self.minute_req_count = 0
        self.iniCycleTime = datetime.now()       #to know if a minute is passed
        self.history = ""                        # so it wouldn t add the instruction to history everytime

        self.prompt_map = tempMap
        self.mood_obj = MoodSystem()

        self.REQUESTS_PER_MINUTE = REQUESTS_PER_MINUTE
        self.iniTime = datetime.now()

        if self.instance !=0:
            return 
        self.client = Client(api_key=api_key)

        self.instance = self.client.models.get(
            model='gemini-2.5-flash'
        )

    #methods ==========================================
    def preprocessor(self, user_input) -> tuple[bool, bool, str]:  
        '''
        bool (ratelimit or not, do NOT process if true)
        bool (send to AI if true, send the exact str if false)
        str (the modified input)

        '''
        if self.maximumReqGuard() == True:
            return (True, False, "")
        
        HIGH_RISK_KEYWORDS = {
            "kill myself", "take my life", "suicide", 
            "die tonight", "don't want to live", "want to hurt myself", 
            "no reason to live", "no reason for me to live"
        }
        
        # check for direct phrase matches
        if text_mod.keyword_matcher(HIGH_RISK_KEYWORDS, user_input):         
            return (False, False, "https://988lifeline.org/")
        
        #print(self.mood_obj.get_mood())
        self.geminiReset(False)

        return (False, True, user_input)

    # no sane person would want to download files on their local machine
    def process_attachment(self, attachment = None):
        if attachment:
            # Check if the attachment is an image
            if not attachment.content_type.startswith('image/'):
                print("no sane person would upload audio file")
                return -1
            response = requests.get(attachment.url)
            if response.status_code != 200:
                return -1
            # Convert to PIL Image
            image = Image.open(BytesIO(response.content))
            return image
        return -1               # not image/ none automatically return -1



    async def processing (self, message, msg_content, attachment=None):
        # print(msg_content)
        msg_content = text_mod.splitUserMsg("=um", msg_content)
        tempImg = self.process_attachment(attachment)

        payload = []
        payload.append(f"{self.prompt_map[self.mood_obj.get_mood_level()]}\n\n========history========\n{self.history}\n{message.author.display_name}: {msg_content}")
        #print(payload)
        #print("\n\n if the output is weird, make sure to change processing prompt")
        if tempImg != -1:    #if it is a real image
            payload.append(tempImg)

        self.updateHistoryPrompt(message.author.display_name, msg_content, tempImg)

        return await self.post_processing(payload, message)

    async def post_processing (self, payload, message) -> str:
        self.mood_obj.pre_input_update(datetime.now(), message.author.id)
        async with message.channel.typing():
            for i in range(5):
                response_obj = await self.client.aio.models.generate_content(
                                    model='gemini-2.5-flash',contents=payload,     
                                    config=types.GenerateContentConfig(
                                        temperature=0.1)
                                        )
                response_text = response_obj.text

                if (response_text is not None) and ("google" not in response_text.lower()):
                    break
                
            # if its still there...
            if "google" in response_text.lower():
                response = "..."
            else:
                response = response_text
            
            #clearing trash
            dict = {"I-19: ": "", "i-19: ": "", "^": "\'"}
            response = text_mod.phrase_swap(response, dict)

            self.history += f"\nI-19: {response}\n"

            self.update_msgCount_and_time()
            self.mood_obj.post_output_update(response)

            # print(self.mood_obj.get_mood())

            return response

        
    # true = no response, false = can have response
    def maximumReqGuard(self) -> bool:
        timeDiff = datetime.now() - self.iniCycleTime
        if (timeDiff.seconds < 60):
            if (self.minute_req_count >= 30):
                return True
        else:
            self.iniCycleTime = datetime.now()  #reset cycle to 60 sec
            self.minute_req_count = 0        # reset req count
        self.minute_req_count += 1
        return False

    def geminiReset(self, condition):
        if (self.resetCond(timedelta(days=2), timedelta(days=1), 80, condition)):
            print("clearing gemini chat history (reset)")
            self.history = ""
            self.iniTime = datetime.now()
            self.mood_obj.reset_mood()

    
    def updateHistoryPrompt (self, authorName, messageContent, imageMaybe):
        self.history += f"{authorName}: {messageContent} "
        if imageMaybe != -1:                #if image exist
            self.history+= "[image]"        #yea, not getting a ai vision service for this
        pass
    
    # debug methods
    def printHistory(self):
        print(self.history)