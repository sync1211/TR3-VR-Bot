import logging
import sys
import signal

import discord
from discord.ext import commands

#Put your token here:
#==============================
TOKEN = "<PASTE YOUR TOKEN HERE!>"
#==============================


#Logging
LOGGER = logging.getLogger('Bot')
LOGGER.setLevel(logging.INFO)
print_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
print_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.addHandler(file_handler)
LOGGER.addHandler(print_handler)


EXT_PERMS = discord.Permissions(
    kick_members=True,
    move_members=True,
    connect=True,
    speak=True,
    administrator=True
)


BOT = commands.Bot(
    command_prefix="+",
    case_insensitive=True,
    description="TR3-VR Bot",
    intents=discord.Intents.all(),
    member_cache_flags=discord.MemberCacheFlags.all()
)



@BOT.event
async def on_ready():
    LOGGER.info("Bot is ready")
    LOGGER.info("Invite link: %s", discord.utils.oauth_url(BOT.user.id, permissions=EXT_PERMS))


@BOT.event
async def on_command_error(ctx, err):
    LOGGER.error("Error while processing command %s", ctx.message.content, exc_info=err)





#catch CTRL+C (linux only!)
def shutdown():
    BOT.loop.create_task(BOT.close())

if sys.platform != "win32":
    BOT.loop.add_signal_handler(signal.SIGINT, shutdown)
    BOT.loop.add_signal_handler(signal.SIGTERM, shutdown)


BOT.load_extension("tr3vr")
BOT.run(TOKEN)

