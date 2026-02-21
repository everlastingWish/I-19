# I-19
A specialized, self hosted Discord bot designed for self hosting high performance AI media generation and roleplaying. 

Unlike standard bots, I-19 features a time based core switch, **alternating between two distinct personalities and command behaviors depending on the time of day**.

https://github.com/user-attachments/assets/6f494b56-9cf2-42d2-82c8-c23e5127154e

# Features
## Self hosting AI Generations
- **ComfyUI Backend Wrapper:** self hosting a chatbot/stable diffusion server with comfyUI backend integration.
- **Optimized Workflow:** uses optimized pre-configured workflows for tasks.

## Infrastructure & Audio
- **"2 bots":** 2 bots in one, each have its own core with different command behaviours; core A is active from 09:00 to 21:00 EST, and core B takes over from 21:00 to 09:00 EST.
- **Lavalink Integration:** music player with lavalink + lavalink youtube plugin support.
- **OOP Design:** mostly rewritten in v1.0.0 for maintainability and modularity.
- **Edge Cases:** some easter egg interaction will appear during "edge cases" to keep the experience fresh.

## AI & Roleplay
- **Dual Core Personality:** features a hardware inspired switching system; core A is active from 09:00 to 21:00 EST, and core B takes over from 21:00 to 09:00 EST.
- **Gemini Mood System:** gemini api wrapper with a integrated "mood system" based of input and output; prompt changes according to the mood system for enhanced roleplaying experience
- **Prompt Engineering:** includes multiple over 5k characters of default instructions for highly nuanced interactions.
- **Webhook Integration:** automatically swaps usernames and profile pictures per core to maintain immersion
- **Easy Triggers:** responds to `@mention`, core name and contextual cues like `i-19`, `l-19`, `ll9`... etc

# Prerequisites
## Hardware/Software
- **OS:** Debian Linux (Linux is highly recommended; Windows is currently untested).
- **Java Runtime:** required for the Lavalink server.
- **Backend:** A running ComfyUI instance listening on port `8188`

## ComfyUI Setup
First, download [illustriousXL20_stable.safetensors](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0), the weight must have a name of "illustriousXL20_stable.safetensors"

Then, place `illustriousXL20_stable.safetensors` in "models/checkpoints/Stable-diffusion" (create a "Stable-diffusion" subdirectory in "models/checkpoints" first)

Ensure the following custom nodes are installed:
- [Sukima Custom Nodes](https://github.com/everlastingWish/Sukima-but-its-a-custom-comfy-UI-node)
- [ComfyUI-Bleh](https://github.com/blepping/ComfyUI-bleh)
- [ComfyUI-PPM](https://github.com/pamparamm/ComfyUI-ppm)
- [ComfyUI-Show-Text](https://github.com/fairy-root/ComfyUI-Show-Text)

Refer to ComfyUI documentation for detailed installation instructions for ComfyUI and custom nodes

Refer to java runtime documentation for detailed installation instructions of it

# Installation
1. Clone and setup I-19 by running these commands:

`git clone https://github.com/everlastingWish/I-19`

`cd I-19`

`pip install -r requirements.txt`

2. Setup lavalink by doing these below:

In the subdirectory "lavalink", download the latest Lavalink.jar in [here](https://github.com/lavalink-devs/Lavalink)

In the subdirectory "lavalink/plugins", download [youtube-plugin-1.17.0.jar](https://github.com/lavalink-devs/youtube-source/releases/tag/1.17.0)

3. In the subdirectory "rss/no_rss", you have to set some values for `.env` and `.json`:

`.json`: add your discord ID to the `friend` field to enable administrative commands
<img width="519" height="102" alt=".json circled" src="https://github.com/user-attachments/assets/06eb6816-ff01-4e37-a763-aa9e02f54a39" />

`.env`: fill in your bot token, google AI studio API key, comfyUI server address and text generation weights' path.
<img width="850" height="422" alt=".env circled" src="https://github.com/user-attachments/assets/bc7f35c4-034c-4350-991f-7e9aa2e5f1a6" />

4. If you don't have netcat or tmux, run these commands to install them:

`sudo apt install netcat-openbsd`

`sudo apt install tmux`

## Run
Run this command in your terminal (within this repo) to start the bot:

`source start_all.sh`

# Usage:
As of early 2026, this bot does not use slash commands to enhance roleplaying; thus you have to type it out on discord for command usage

E.g:
- `=um` or `character name` to trigger one of the text generation function based on core
- `=draw` to trigger one of the image generation function based on core
- `=help` to send a help file with the influence of the active core's personality
...etc

You can type `=help` to see the most of the usable commands for normal users on discord

# Project History

Originally written to have fun. Influenced by [Pandora](https://github.com/Cubie87/Pandora) and [Eliza](https://github.com/harubaru/eliza).

## vd1.0.0 (8/17/2024): 
Inital commit with a simple [meta api backend](https://github.com/Strvm/meta-ai-api) for chatbot and hugging face api for [music](https://huggingface.co/facebook/musicgen-small) and [image](https://huggingface.co/black-forest-labs/FLUX.1-dev) generation with basic logging

Showcase:

https://github.com/user-attachments/assets/98f66328-3cd2-4cd5-b749-61e2f6f1b618

## vd1.0.2 (12/21/2024): 

Added a command `=uh` with different personality prompts for gemini, overall optimisation and various bug fixes, attempted to add OOP design on some functions

## v1.0.0 (2/21/2026): 

Major structural change to OOP design as it seems that the old structure is too hard to work with, implemented the time based dual core system, and shift to local comfyUI hosting to bypass API rate limits

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or features.

# License
This project contains code from Eliza and is licensed under [GPL-2.0](LICENSE).
