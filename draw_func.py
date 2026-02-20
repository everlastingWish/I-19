import discord
import json
import io

async def draw_func(prompt, comfy_client):
    with open("rss/illu api no save.json", "r") as f:
        data = json.load(f)

    image_bytes = await comfy_client.generate_image(
        workflow = data.copy(),  # Use a copy to avoid modifying original
        positive_prompt=f"sfw, {prompt}"    
        )
    
    # Create Discord file from bytes
    file = discord.File(
        fp=io.BytesIO(image_bytes),
        filename="if image is bad it means your prompt is bad.png"
    )
    
    return file
