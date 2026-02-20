import aiohttp
import json
import io
import asyncio
from typing import Optional
import random

class ComfyUIClient:
    def __init__(self, server_address):
        self.server_address = server_address
        self.client_id = "discordClient"
    
    async def queue_prompt(self, prompt: dict) -> str:
        """queue a prompt and return the prompt_id"""
        data = {
            "prompt": prompt,
            "client_id": self.client_id
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://{self.server_address}/prompt",
                json=data
            ) as response:
                result = await response.json()
                return result['prompt_id']
    
    async def get_history(self, prompt_id: str) -> dict:
        """Get the history/results of a prompt"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.server_address}/history/{prompt_id}"
            ) as response:
                return await response.json()
    
    async def get_image_bytes(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        """Download image as bytes"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://{self.server_address}/view",
                params={
                    "filename": filename,
                    "subfolder": subfolder,
                    "type": folder_type
                }
            ) as response:
                return await response.read()
    
    async def wait_for_completion(self, prompt_id: str, timeout: int = 300) -> dict:
        """Poll until the prompt is completed"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Image generation timed out")
            
            history = await self.get_history(prompt_id)
            
            if prompt_id in history:
                return history[prompt_id]
            
            await asyncio.sleep(0.3)  # Poll every 0.3 sec
    
    async def generate_image(self, workflow: dict, positive_prompt: str, 
                            negative_prompt: Optional[str] = None) -> bytes:

        # Modify the workflow with new prompts
        workflow["6"]["inputs"]["text"] = positive_prompt
        workflow["22"]["inputs"]["noise_seed"] = random.randint(0, 18446744073709551615)
        
        if negative_prompt:
            workflow["7"]["inputs"]["text"] = negative_prompt
        
        # Queue the prompt
        prompt_id = await self.queue_prompt(workflow)
        
        # Wait for completion
        history = await self.wait_for_completion(prompt_id)
        
        # Extract image info
        outputs = history['outputs']
        
        # Find the image output (usually from VAE Decode or Preview nodes)
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                image_info = node_output['images'][0]
                
                # Download image bytes
                image_bytes = await self.get_image_bytes(
                    filename=image_info['filename'],
                    subfolder=image_info['subfolder'],
                    folder_type=image_info['type']
                )
                
                return image_bytes
        
        raise Exception("No image found in output")

    async def generate_text(self, model_path:str, workflow: dict, prompt: str) -> str:
        """Generate text and return as string"""
        
        # Modify workflow with prompt
        workflow["1"]["inputs"]["prompt"] = prompt
        workflow["1"]["inputs"]["model_name"] = model_path
        
        prompt_id = await self.queue_prompt(workflow)
        history = await self.wait_for_completion(prompt_id)
        
        # Extract text from outputs
        outputs = history['outputs']
        for node_id, node_output in outputs.items():
            if 'text' in node_output:
                full_text =  node_output['text'][0]
                clean_prompt = prompt.strip()
                clean_full_text = full_text.strip()
                return full_text[len(prompt):].lstrip()
        
        raise Exception("No text found in output")
