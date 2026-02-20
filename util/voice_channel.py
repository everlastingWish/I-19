import discord
from discord.ext import commands
import asyncio
import wavelink
from typing import Optional, cast
import re 

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.disconnect_timers = {}  # guild_id -> timer task
        self.node_connected = False

    async def setup_node(self, host: str, port: int, password: str):
        """
        Sets up the Wavelink node connection to your Lavalink server.
        Call this method when your bot is ready (e.g., in on_ready event).
        
        Args:
            host: The host address of your Lavalink server
            port: The port number (default: 2333)
            password: The password for your Lavalink server
        """
        try:
            node = wavelink.Node(
                uri=f"http://{host}:{port}",
                password=password
            )
            
            await wavelink.Pool.connect(client=self.bot, nodes=[node])
            
            self.node_connected = True
            print(f"✅ Successfully connected to Lavalink node at {host}:{port}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Lavalink node: {e}")
            self.node_connected = False


    def _cancel_disconnect_timer(self, guild_id: int):
        """
        Safely cancel and remove a disconnect timer for a guild.
        """
        if guild_id in self.disconnect_timers:
            timer_task = self.disconnect_timers[guild_id]
            if not timer_task.done():
                timer_task.cancel()
            del self.disconnect_timers[guild_id]


    async def join_voice_channel(self, ctx) -> Optional[wavelink.Player]:
        """
        Connects the bot to the voice channel of the command invoker (ctx.author) 
        using the wavelink.Player class.
        """
        if not self.node_connected:
            await ctx.send("where is lavalink.")
            return None
        
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel first.")
            return None
        
        channel = ctx.author.voice.channel
        guild_id = ctx.guild.id
        voice_client = cast(Optional[wavelink.Player], ctx.voice_client)
        try:
            if voice_client and voice_client.channel:
                # Bot is already connected, move it to the new channel
                await voice_client.move_to(channel)
                await ctx.message.add_reaction('✅')
                
            else:
                # Bot is not connected, connect it using the wavelink Player class
                voice_client = await channel.connect(cls=wavelink.Player, self_deaf=True)
                await ctx.message.add_reaction('✅')                

            # Cancel any pending disconnect timer since a user is now present
            self._cancel_disconnect_timer(guild_id)

            return voice_client

        except Exception as e:
            await ctx.send(f"I don't have permission to join that voice channel: {e}")
            return None

    def _is_alone(self, voice_client: discord.VoiceClient) -> bool:
        """
        Helper method to check if the bot is the only human/non-self user
        in the voice channel.
        """
        if not voice_client or not voice_client.channel:
            return True
        
        human_users = [
            member for member in voice_client.channel.members
            if not member.bot
        ]
        
        return len(human_users) == 0

    def _is_player_valid(self, voice_client: wavelink.Player, guild) -> bool:
        """
        Check if the player is still valid and connected.
        """
        try:
            return (
                voice_client is not None and
                voice_client.channel is not None and
                voice_client.guild is not None and
                guild.voice_client is not None
            )
        except Exception:
            return False

    async def _auto_disconnect_timer(self, voice_client: wavelink.Player, guild, timeout_seconds: int = 60):
        """
        A dedicated task to wait for the timeout and disconnect.
        """
        guild_id = voice_client.guild.id
        
        try:
            await asyncio.sleep(timeout_seconds)
            print("it should be gone?")
            # Re-check the condition after the timer expires
            if self._is_player_valid(voice_client, guild) and self._is_alone(voice_client):
                try:
                    print(f"Guild {guild_id}: Auto-disconnecting due to inactivity")
                    await voice_client.stop()
                    await voice_client.disconnect()
                except Exception as e:
                    print(f"Error during auto-disconnect for guild {guild_id}: {e}")
        
        except asyncio.CancelledError:
            # Timer was cancelled (user joined back)
            print(f"Guild {guild_id}: Disconnect timer cancelled")
        
        finally:
            # Clean up the timer reference
            if guild_id in self.disconnect_timers:
                del self.disconnect_timers[guild_id]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handles auto-disconnect/reconnect logic based on user activity."""

        # 1. Ignore if the update is for the bot itself or a change that doesn't involve the channel
        if member.id == self.bot.user.id or before.channel == after.channel:
            return

        guild = member.guild
        # Get the wavelink player for this guild
        player = cast(Optional[wavelink.Player], guild.voice_client)

        if not player:
            return
            
        guild_id = guild.id
        
        # 2. Check if a human user left the bot's channel
        if before.channel == player.channel and member.id != self.bot.user.id and not member.bot:
            # Check if the bot is now alone after the member left
            if self._is_alone(player):
                # Start timer if one is not already running
                if guild_id not in self.disconnect_timers:
                    print(f"Guild {guild_id}: Bot is alone (via event). Starting 60s disconnect timer.")
                    timer_task = self.bot.loop.create_task(
                        self._auto_disconnect_timer(player, guild, timeout_seconds=60) # Note: ctx is now None
                    )
                    self.disconnect_timers[guild_id] = timer_task
            
        # 3. Check if a human user joined the bot's channel
        elif after.channel == player.channel and member.id != self.bot.user.id and not member.bot:
            # Cancel timer if one is running
            if guild_id in self.disconnect_timers:
                print(f"Guild {guild_id}: Human user joined (via event). Cancelling disconnect timer.")
                self._cancel_disconnect_timer(guild_id)
                
        # 4. Critical: If the bot itself disconnected (e.g., manually kicked/Lavalink issue)
        if member.id == self.bot.user.id and before.channel and not after.channel:
            # The bot left the channel. Ensure all related tasks are cleaned up.
            print(f"Guild {guild_id}: Bot disconnected (via event). Cleaning up tasks.")
            self._cancel_disconnect_timer(guild_id)

    async def play(self, ctx, search: str):
        """
        Searches for a track and streams it to the voice channel.
        Usage: !play <song title or URL>
        """
        if not self.node_connected:
            await ctx.send("Lavalink node not connected.")
            return
        
        # 1. Ensure the bot is connected
        if not ctx.voice_client:
            vc = await self.join_voice_channel(ctx)
            if not vc:
                return
        else:
            vc = cast(wavelink.Player, ctx.voice_client)
            
            # Verify the player is still valid
            if not self._is_player_valid(vc, ctx.guild):
                await ctx.send("Voice connection is invalid.")
                return
        
        if not search.startswith("http"):
            if re.match(r"^[a-zA-Z0-9_-]{11}$", search):
                search = f"https://www.youtube.com/watch?v={search}"
        
        # 2. Search for the track

        try:
            tracks = await wavelink.Playable.search(search)
        except Exception as e:
            await ctx.send(f"a {e}")
            return

        if not tracks:
            return await ctx.send(f"Could not find any tracks for `{search}`.")

        # 3. Play the track
        track = tracks[0]
                
        await vc.play(track)
        

    async def leave_voice_channel(self, ctx):
        """
        Manually disconnect the bot from voice channel.
        """
        voice_client = cast(Optional[wavelink.Player], ctx.voice_client)
        
        if not voice_client or not voice_client.channel:
            await ctx.send("I'm not in a voice channel.")
            return
        
        guild_id = ctx.guild.id
        
        try:
            # Cancel any pending timers 
            self._cancel_disconnect_timer(guild_id)
            
            # Stop the player and disconnect
            await voice_client.stop()
            await voice_client.disconnect()
            await ctx.message.add_reaction('👋')

        except Exception as e:
            await ctx.send(f"Error while leaving: {e}")