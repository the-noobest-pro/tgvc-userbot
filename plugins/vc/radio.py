"""
https://github.com/MarshalX/tgcalls/blob/main/examples/radio_as_smart_plugin.py
154ef295a3fe3a2383bbd0275a1195c6fafd307d
"""
import signal
import re

# noinspection PyPackageRequirements
import asyncio
import ffmpeg  # pip install ffmpeg-python
from pyrogram import Client, filters
from pyrogram.types import Message

from pytgcalls import GroupCall  # pip install pytgcalls

# Example of pinned message in a chat:
'''
Radio stations:

1. https://hls-01-regions.emgsound.ru/11_msk/playlist.m3u8

To start replay to this message with command !start <ID>
To stop use !stop command
'''


# Commands available only for anonymous admins
self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

GROUP_CALLS = {}
FFMPEG_PROCESSES = {}
STREAM_LINK = re.compile(r"https?://[\S]+\.(?:m3u8?|audio|mp3|aac|[a-z]{1,4}:[0-9]+)")

@Client.on_message(self_or_contact_filter & filters.command('start', prefixes='!'))
async def start(client, message: Message):
    input_filename = f'radio-{message.chat.id}.raw'

    group_call = GROUP_CALLS.get(message.chat.id)
    if group_call is None:
        group_call = GroupCall(client, input_filename, path_to_log_file='')
        GROUP_CALLS[message.chat.id] = group_call

    if len(message.command) < 2:
        await message.reply_text('You forgot to replay list of stations or pass a station ID')
        return

    query = message.command[1]
    match = STREAM_LINK.search(query)
    station_stream_url = query
    
    if not station_stream_url:
        await message.reply_text(f'Can\'t find a station.')
        return
    
    ffmpeg_log = open("ffmpeg.log", "w+")
    command = [
       "ffmpeg", "-y", "-i", station_stream_url, "-f", "s16le", "-ac", "2",
       "-ar", "48000", "-acodec", "pcm_s16le", group_call.input_filename
       ]


    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=ffmpeg_log,
        stderr=asyncio.subprocess.STDOUT,
        )

    await group_call.start(message.chat.id)
    FFMPEG_PROCESSES[message.chat.id] = process
    await message.reply_text(f'Radio is playing...')


@Client.on_message(self_or_contact_filter & filters.command('stop', prefixes='!'))
async def stop(_, message: Message):
    group_call = GROUP_CALLS.get(message.chat.id)
    if group_call:
        await group_call.stop()

    process = FFMPEG_PROCESSES.get(message.chat.id)
    if process:
        process.send_signal(signal.SIGTERM)
