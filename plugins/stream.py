import signal
import re
import subprocess

import asyncio
import ffmpeg 
from pyrogram import Client, filters
from pyrogram.types import Message

from youtube_dl import YoutubeDL
from pytgcalls import GroupCall 


# Special Thanks to AsmSafone for the YTDL filter.

# Commands available only for owner and contacts

self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)

GROUP_CALLS = {}
FFMPEG_PROCESSES = {}

ydl_opts = {
    "geo-bypass": True,
    "nocheckcertificate": True
    }
ydl = YoutubeDL(ydl_opts)


@Client.on_message(self_or_contact_filter & filters.command('radio', prefixes='!'))
async def radio(client, message: Message):
    input_filename = f'radio-{message.chat.id}.raw'

    group_call = GROUP_CALLS.get(message.chat.id)
    if group_call is None:
        group_call = GroupCall(client, input_filename, path_to_log_file='')
        GROUP_CALLS[message.chat.id] = group_call

    if len(message.command) < 2:
        await message.reply_text('You forgot to enter a Stream URL')
        return   

    query = message.command[1]

    regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
    match = re.match(regex,query)
    if match:
        meta = ydl.extract_info(query, download=False)
        formats = meta.get('formats', [meta])
        for f in formats:
            station_stream_url = f['url']
    else:
        station_stream_url = query

    process = (
        ffmpeg.input(station_stream_url)
        .output(input_filename, format='s16le', acodec='pcm_s16le', ac=2, ar='48k')
        .overwrite_output()
        .run_async()
    )

    FFMPEG_PROCESSES[message.chat.id] = process
    await message.reply_text(f'📻 Radio is Starting...')
    await asyncio.sleep(2)
    await group_call.start(message.chat.id)


@Client.on_message(self_or_contact_filter & filters.command('stopradio', prefixes='!'))
async def stopradio(_, message: Message):
    process = FFMPEG_PROCESSES.get(message.chat.id)
    if process:
        process.send_signal(signal.SIGTERM)
        await asyncio.sleep(2)

    group_call = GROUP_CALLS.get(message.chat.id)
    if group_call:
        await group_call.stop()
        await message.reply_text(f'✋ Stopped Streaming')
