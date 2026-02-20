from transformers import AutoTokenizer
from util.text_mod import splitUserMsg, replace_emojis_pings_inverse, replace_emojis_pings, cut_trailing_sentence, anti_spam, phrase_swap
import re
import json

class second_chance:
    def __init__(self, max_mem_tokens, instruction, model_path, combined_pattern, bot):            
        self.max_mem_tokens = max_mem_tokens
        # memory is a stack of tuples: [("author: text", token_count), ...]
        self.model_path = model_path
        self.memory = []
        self.current_tokens = 0
        self.instruction = instruction
        self.combined_pattern = combined_pattern
        self.client = bot
        self.app_emojis = None
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        
    def get_token_count(self, text:str) -> int:
        """Tokenize input text and return the number of tokens and the token list length."""
        tokenization_output = self.tokenizer(text, truncation=False)
        input_ids = tokenization_output.input_ids
        # Get the length of the input_ids list
        token_count = len(input_ids)
        return token_count

    def update_memory(self, author: str, text: str):
        token_count = self.get_token_count(text)
        new_memory_entry = (f"{author}: {text}", token_count)
        self.memory.append(new_memory_entry)
        self.current_tokens += token_count

    def build_ctx(self, input_author, input_text):
        if input_text != '':
            self.update_memory(input_author, input_text)

        if len(self.memory) > 1:
            # We pass the memory list to the utility function
            filtered_memory, tokens_removed = anti_spam(self.memory)

            if tokens_removed > 0:
                self.memory = filtered_memory
                self.current_tokens -= tokens_removed

        while len(self.memory) > 40:
            removed_entry, removed_tokens = self.memory.pop(0)
            self.current_tokens -= removed_tokens

        while self.current_tokens > self.max_mem_tokens and len(self.memory) > 1:
            # Pop the oldest entry (index 0)
            removed_entry, removed_tokens = self.memory.pop(0)
            self.current_tokens -= removed_tokens

        # 3. Build context string
        context = self.instruction + "\n"

        for text, _ in self.memory:
            context += text + "\n"
        context += "Chen:"
        return context

    # --- Pre/Post Processors ---

    def preprocessor(self, message):
        """
        Applies Eliza function C&P and swaps 'ii9'/'i-19' with 'chen'.
        """
        # 1. Eliza C&P (Placeholder implementation)
        input_text = splitUserMsg("=um", message.content, "chen ")
        input_text = replace_emojis_pings_inverse(text=input_text, users=message.guild.members, emojis=self.client.emojis)
        input_text = re.sub(r'\<[^>]*\>', '', input_text.lstrip().rstrip()).lstrip().rstrip()

        # 2. Swap all ii9/i-19 thing with chen
        input_text = re.sub(self.combined_pattern, "chen", input_text)
        return input_text

    def postprocessor(self, output_text, message):
        """
        Updates memory, swaps 'garbage', and applies Eliza C&P.
        """
        # 1. Update memory
        output_text = output_text.strip()
        self.update_memory("Chen", output_text)
        
        # nvm, don't swap garbage, just use raw chen
        # garbage_map = {
        #     "bakeneko": "sotonaru kami", "Bakeneko": "Sotonaru kami", "BAKENEKO": "SOTONARU KAMI",
        #     "shikigami": "hizōbutsu", "Shikigami": "Hizōbutsu", "SHIKIGAMI": "HIZŌBUTSU",
        #     "ran sama":"ruri sama", "Ran": "Ruri", "RAN": "RURI",
        #     "yukari": "akari", "Yukari": "Akari", "YUKARI": "AKARI",
        #     "yakumo": "yuzuki", "Yakumo": "Yuzuki", "YAKUMO": "YUZUKI",
        # }        
        # output_text = phrase_swap(output_text, garbage_map)
            
        # 3. Eliza C&P (Placeholder implementation)
        output_text = cut_trailing_sentence(output_text)
        output_text = output_text.lstrip()
        output_text = replace_emojis_pings(text=output_text, users=message.guild.members, emojis=self.app_emojis)

        return output_text

    # --- Main Function ---
    def self_reset (self):
        print("chen memory reseted")
        self.memory = []
        self.current_tokens = 0

    async def text_func(self, message, comfy_client):
        if self.app_emojis is None:
            self.app_emojis = await self.client.fetch_application_emojis()
        with open("rss/sukima_generation.json", "r") as f:
            data = json.load(f)
        
        preprocessed_input = self.preprocessor(message)
        #print("preprocessed: " + preprocessed_input)
        context = self.build_ctx(message.author, preprocessed_input)
        #print("built ctx: " + context)
        output = await comfy_client.generate_text(self.model_path, workflow = data.copy(), prompt = context)
        output = self.postprocessor(output, message)
        return output