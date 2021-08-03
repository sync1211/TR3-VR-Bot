'''BOT EXTENSION'''
import asyncio
import itertools
import json
import logging
import operator
import os
import random
from shutil import copyfile

import discord
from discord.ext import commands
from concurrent.futures._base import CancelledError


#Logging
LOGGER = logging.getLogger("Bot")

#Sounds
DIR_BASE = "res/Sounds"

TR3VR_SOUNDS = {
    "kill": f"{DIR_BASE}/kill",
    "move": f"{DIR_BASE}/move",
}


async def send_error_embed(ctx, msg, usage=True, desc=""):
    '''Sends an error embed for the command invoked via ctx.
    (Used for consistency)

    Arguments:
        * msg: the error message to display ("Error: " will be prepended!)
        * usage: whether the commands usage text should be displayed in the error embed
        * desc: optional details/hints about the error
    '''
    error_embed = discord.Embed(title=f"**Error:** {msg}", description=desc, color=0x8b0000)
    if usage and ctx.command.usage is not None:
        error_embed.add_field(name="Usage", value=f"`{ctx.command.name} {ctx.command.usage}`")
    await ctx.send(embed=error_embed)



def load_config(config_file, config_name="config file", config_empty=None):
    '''load config file

    Arguments:
        * config_file: the configuration file to load (in JSON format)
        * config_name: the name of the configuration file (for logging purposes)
        * config_empty: the file to use if config_file does not exist. Will be copied to the path of config_file

        Raises:
            See https://docs.python.org/3/library/json.html#exceptions
    '''
    if not os.path.isfile(config_file) and config_empty is not None:
        copyfile(config_empty, config_file)

    LOGGER.info("Loading %s...\r", config_name)
    with open(config_file, 'r') as conf_file:
        return json.load(conf_file)



class TR3VR(commands.Cog, name="TR3-VR"):
    '''SPOOKY'''
    def __init__(self, bot):
        self.bot = bot

        #voice warning
        if len(bot.cogs) > 1:
            LOGGER.warning("Running this extension with other extensions is not recommended as it may interfere with other voice systems!")

        #init sounds
        self.sounds = {}
        for name, sound_dir in TR3VR_SOUNDS.items():
            self.sounds[name] = list(map(lambda sfile, sd=sound_dir: sd+"/"+sfile, os.listdir(sound_dir)))

        #start tasks
        self.walk_tasks = {}
        bot.loop.create_task(
            self.wait_for_ready()
        )


        if not os.path.isdir("config"):
            os.makedirs("config")
        self.server_settings = load_config("config/TR3-VR.json", "TR3-VR settings", "res/conf.empty")


    def cog_unload(self):
        '''stop all tasks'''
        list(
            map(
                operator.methodcaller("cancel"),
                self.walk_tasks.values()
            )
        )


    async def wait_for_ready(self):
        '''wait until ready and start walk tasks'''

        LOGGER.debug("Waiting until the bot is ready...")
        await self.bot.wait_until_ready()

        #create the walking loop for each server'''
        async for guild in self.bot.fetch_guilds():
            LOGGER.debug("Starting walking loop on %s", guild.name)
            self.walk_tasks[guild.id] = self.bot.loop.create_task(
                self.walk_loop(guild)
            )



    async def play_sound(self, voice_client, category):
        '''Plays a sound from the given category'''
        #choose sound
        chosen_sound = random.choice(self.sounds[category])

        LOGGER.debug("Playing %s-sound in %s\nSound path: %s", category, voice_client.channel.name, chosen_sound)

        wait_for_return = asyncio.Event()
        audio_source = discord.FFmpegPCMAudio(chosen_sound, options="-loglevel error")

        #Helper function
        def after_playing(error):
            LOGGER.debug("Done playing")
            if error is not None:
                LOGGER.error("Error playing audio!", exc_info=error)
            else:
                wait_for_return.set()

        #play the sound
        try:
            voice_client.play(
                audio_source,
                after=after_playing
            )
        except Exception as voice_err:
            LOGGER.error("Error playing sound!", exc_info=voice_err)
        else:
            #wait until sound is done playing
            await wait_for_return.wait()


    async def walk(self, channel, kill=False):
        '''
        Changes the channel, plays a sound and then leaves.
        May also hit players and kick them from the channel
        '''
        #connect to channel
        LOGGER.debug("Connecting to %s", channel.name)
        guild = await self.bot.fetch_guild(channel.guild.id)

        if not (guild.voice_client is not None
                and not guild.voice_client.channel is not None
                and channel is not None
                and guild.voice_client.channel.id == channel.id):
            try:
                if guild.voice_client is not None:
                    LOGGER.debug("Already connected; Disconnecting...")
                    await guild.voice_client.disconnect()
                voice_client = await channel.connect()
            except discord.ClientException as voice_err:
                LOGGER.error("Error connecting to channel, skipping!", exc_info=voice_err)
                return

        LOGGER.debug("Walking through %s...", channel.name)

        #hit layer
        channel = await self.bot.fetch_channel(channel.id)
        LOGGER.debug("Channel %s: %s", channel.name, channel.members)

        if len(channel.members) > 1:
            if kill and random.choice([True, False]):
                target_player = random.choice(
                    list(
                        itertools.filterfalse(
                            operator.attrgetter("bot"),
                            channel.members
                        )
                    )
                )

                if target_player:
                    if random.choice([True, False]):
                        #play walking sound
                        LOGGER.debug("Intending to kick %s", target_player)
                        await self.play_sound(voice_client, "move")

                    #kick player
                    LOGGER.debug("Hitting player %s", target_player)
                    self.bot.loop.create_task(target_player.move_to(None))

                    #play kill sound
                    await self.play_sound(voice_client, "kill")
            else:
                #play walking sound
                await self.play_sound(voice_client, "move")
        else:
            sleep_sec = random.randint(1, 4)
            LOGGER.debug("Sleeping for %s seconds...", sleep_sec)
            await asyncio.sleep(sleep_sec)


    async def walk_loop(self, guild):
        '''
        Walk through channels and perform actions!
        This is basically the main loop of this function!
        '''
        reverse = random.choice([True, False])
        LOGGER.debug("Started walking loop on %s!", guild.name)

        #get voice channels
        guild = await self.bot.fetch_guild(guild.id)
        voice_channels = list(
            sorted(
                filter(
                    lambda x: isinstance(x, discord.VoiceChannel) and x.id != getattr(guild.afk_channel, "id", 0),
                    await guild.fetch_channels()
                ),
                key=operator.attrgetter("position")
            )
        )
        LOGGER.debug("Voice channels: %s", voice_channels)

        if voice_channels == []:
            return

        kill_enabled = self.server_settings.get(
            str(guild.id),
            self.server_settings["global"]
        ).get("kill_enabled", False)

        #walking loop
        while True:
            #set direction
            direction = ((not reverse) * 2) - 1

            #walk through channels
            if reverse:
                i = len(voice_channels)
            else:
                i = 0
            LOGGER.debug("Direction: %s, i: %s", direction, i)

            while 0 <= i < len(voice_channels):
                try:
                    await self.walk(voice_channels[i], kill=kill_enabled)
                except CancelledError as e:
                    LOGGER.debug("Error while walking! server=%s; channel=%s", guild.name, voice_channels[i].name, exc_info=e)
                    return
                except RuntimeError as e:
                    LOGGER.error("Error while walking! server=%s; channel=%s", guild.name, voice_channels[i].name, exc_info=e)
                    return
                except Exception as e:
                    LOGGER.error("Error while walking! server=%s; channel=%s", guild.name, voice_channels[i].name, exc_info=e)

                i += direction

                if random.choice(([True, False])):
                    direction = direction * -1
                    LOGGER.debug("Changing direction...")

            #turn around
            reverse = not reverse


    #commands
    @commands.command(brief="stop walking")
    async def stopWalking(self, ctx):
        '''stops the walking loop for this server'''
        await self.on_guild_remove(ctx.guild)
        if ctx.guild.voice_client is not None:
            await ctx.guild.voice_client.disconnect()
        await ctx.send("stopped walking...")


    @commands.command(brief="stop walking")
    async def startWalking(self, ctx):
        '''starts the walking loop for this server'''
        try:
            if not self.walk_tasks[ctx.guild.id].is_canceled():
                await self.on_guild_join(ctx.guild)
            else:
                await send_error_embed(ctx, "already walking", usage=False)
                return
        except KeyError:
            await self.on_guild_join(ctx.guild)
        await ctx.send("started walking...")


    @commands.command(brief="stop walking")
    async def restartWalking(self, ctx):
        '''restarts the walking loop for this server'''
        try:
            self.walk_tasks[ctx.guild.id].cancel()
        except KeyError:
            pass
        await self.on_guild_join(ctx.guild)
        await ctx.send("started walking...")



    #events
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''invited to server -> start walking'''
        self.walk_tasks[guild.id] = self.bot.loop.create_task(
                self.walk_loop(guild)
            )


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''left server -> stop walking'''
        try:
            self.walk_tasks[guild.id].cancel()
        except (KeyError, asyncio.CancelledError):
            pass



def setup(bot):
    '''import and run extension'''
    bot.add_cog(TR3VR(bot))
