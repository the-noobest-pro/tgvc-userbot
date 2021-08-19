# PORTED EVAL FROM TheCodents/DevelopersUserbot
# PORTED BASH FROM TeamUltroid/Ultroid

import traceback
import aiofiles
import json
import sys
import os
import requests
import re
import subprocess
import io
import asyncio
from io import StringIO
from pyrogram import Client, filters
from pyrogram.types import Message


spaceb = "https://spaceb.in/api/v1/documents/"
DOWNLOAD_DIR = "/app/pastebin/"


self_or_contact_filter = filters.create(
    lambda _, __, message:
    (message.from_user and message.from_user.is_contact) or message.outgoing
)


async def aexec(code, client, m):
    exec(
        f"async def __aexec(client, m): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](client, m)


def spacebin(text, ext="txt"):
    try:
        request = requests.post(
            spaceb, 
            data={
                "content": text.encode("UTF-8"),
                "extension": ext,
            },
        )
        r = request.json()
        key = r.get('payload').get('id')
        return {
            "bin": "SpaceBin",
            "link": f"https://spaceb.in/{key}",
            "raw": f"{spaceb}{key}/raw",
        }
    except Exception as e:
        return str(e)
    

p = print
@Client.on_message(self_or_contact_filter & filters.command('eval', prefixes='!'))
async def evaluate(client, m: Message):
    status_message = await m.reply_text("`Running ...`")
    try:
        cmd = m.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await status_message.delete()
        return
    if m.reply_to_message:
        reply_id = m.reply_to_message.message_id
    else:
        reply_id = None
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, m)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"<b>Command:</b>\n<code>{cmd}</code>\n\n<b>Output</b>:\n<code>{evaluation.strip()}</code>"
    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(final_output))
        await m.reply_document(
            document=filename,
            caption="Pyrogram Eval",
            disable_notification=True,
            reply_to_message_id=reply_id,
        )
        os.remove(filename)
        await status_message.delete()
    else:
        await status_message.edit(final_output)
        
        
p = print
@Client.on_message(self_or_contact_filter & filters.command('bash', prefixes='!'))
async def terminal(client, m: Message):
    shtxt = await m.reply_text("`Processing...`")
    try: 
        cmd = m.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await shtxt.edit("`No cmd given`")
    if m.reply_to_message:
        reply_id = m.reply_to_message.message_id
    else:
        reply_id = None
    
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    OUT = f"**â˜ž BASH\n\nâ€¢ COMMAND:**\n`{cmd}` \n\n"
    e = stderr.decode()
    if e:
        OUT += f"**â€¢ ERROR:** \n`{e}`\n\n"
    t = stdout.decode()
    if t:
        _o = t.split("\n")
        o = "\n".join(_o)
        OUT += f"**â€¢ OUTPUT:**\n`{o}`"
    if not e and not t:
        OUT += f"**â€¢ OUTPUT:**\n`Success`"
    if len(OUT) > 4096:
        ultd = OUT.replace("`", "").replace("*", "").replace("_", "")
        with open("bash.txt", "w") as out_file:
            out_file.write(ultd)
        await m.reply_document(
            document="bash.txt",
            caption="`Output file`",
            reply_to_message_id=reply_id,
        )
        await shtxt.delete()
        os.remove("bash.txt")
    else:
        await shtxt.edit(OUT)


@Client.on_message(filters.command('paste', prefixes='!'))
async def pastebin(client, message: Message):
    huehue = await message.reply_text("`...`")
    reply = message.reply_to_message
    type = "txt"
    if reply:
        if reply.document:
            if reply.file_size < 300000:
                await huehue.edit("Brah, Too big file")
                return
            try:
                type = os.path.splitext(reply.document.file_name)[1].lstrip('.')
            except Exception:
                type = "txt"
            try:
                dl_ = await client.download_media(reply, DOWNLOAD_DIR)
                with open(dl_, 'r') as f:
                    text = f.read()
            except Exception:
                await huehue.edit("Couldn't read this file.")
                return
            os.remove(dl_)
        elif reply and reply.text:
            text = reply.text
    elif len(message.text) > 7:
        text = message.text[7:]
    else:
        await huehue.edit("`Give me Something to Paste ðŸ™„`")
        return

    _paste = spacebin(text, type)  
    if isinstance(_paste, dict):
        c1m = f"<b>Pasted to <a href='{_paste['link']}'>{_paste['bin']}</a> "\
        f"| <a href='{_paste['raw']}'>Raw</a></b>"
        await huehue.edit(
            c1m,
            parse_mode="html",
            disable_web_page_preview=True,
        )
    else:
        await huehue.edit(str(_paste))
        return
