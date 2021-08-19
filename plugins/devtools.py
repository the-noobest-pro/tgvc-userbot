# PORTED EVAL FROM TheCodents/DevelopersUserbot
# PORTED BASH FROM TeamUltroid/Ultroid

import traceback
import aiohttp
import json
import sys
import os
import requests
import re
import subprocess
import io
import asyncio
from urllib.parse import urlparse
from io import StringIO
from pyrogram import Client, filters
from pyrogram.types import Message


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

p = print

@Client.on_message(self_or_contact_filter & filters.command('eval', prefixes='!'))
async def evaluate(client, m: Message):

    status_message = await m.reply_text("`Running ...`")
    try:
        cmd = m.text.split(" ", maxsplit=1)[1]
    except IndexError:
        await status_message.delete()
        return
    reply_to_id = m.message_id
    if m.reply_to_message:
        reply_to_id = m.reply_to_message.message_id
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
            reply_to_message_id=reply_to_id,
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
    
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    OUT = f"**☞ BASH\n\n• COMMAND:**\n`{cmd}` \n\n"
    e = stderr.decode()
    if e:
        OUT += f"**• ERROR:** \n`{e}`\n\n"
    t = stdout.decode()
    if t:
        _o = t.split("\n")
        o = "\n".join(_o)
        OUT += f"**• OUTPUT:**\n`{o}`"
    if not e and not t:
        OUT += f"**• OUTPUT:**\n`Success`"
    if len(OUT) > 4096:
        ultd = OUT.replace("`", "").replace("*", "").replace("_", "")
        with io.BytesIO(str.encode(ultd)) as out_file:
            out_file.name = "bash.txt"
            await m.reply_document(
                document=out_file,
                caption="`Output file`",
                reply_to_message_id=m.message_id
            )
            await shtxt.delete()
    else:
        await shtxt.edit(OUT)
        
        

# Thanks to Avish peru for making Dogbin clone!
dog_ = "https://dogbin.up.railway.app/"
spaceb = "https://spaceb.in/api/v1/documents/"

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
            "id": key,
            "link": f"https://spaceb.in/{key}",
            "raw": f"{spaceb}{key}/raw",
        }
    except Exception as ex:
        return f"#Error : {r.get('error')}"
    
async def kontent(file, ext="txt"):
    if not file.media:
        return "#Error : Not a File"
    try:
        dl_ = await file.download_media()
        try:
            ext = file.file.ext.replace('.', '')
        except Exception:
            ext = "txt"
        data = ''
        with open(dl_) as f:
            data = f.read()
            f.close()
    except Exception as ex:
        return "#Error : While Reading the file!"
    finally:
        from os import remove
        remove(dl_)

    return ext, data
        
@Client.on_message(self_or_contact_filter & filters.command('paste', prefixes='!'))
async def pastebin(client, message: Message):
    huehue = await message.reply_text("`...`")
    try:
        reply = message.reply_to_message
        if reply.media:
            data = await kontent(reply)
            if isinstance(data, tuple):
                text = data[1]
                ext = data[0]
            else:
                return
        else:
            text = reply.message
    except Exception as e:
        await huehue.edit("`Reply to a File or Message`")
    
    _paste = spacebin(text, ext)
    
    if isinstance(_paste, dict):
        c1m = f"<b>Pasted to <a href='{_paste['link']}'>{_paste['bin']}</a> "\
        f"| <a href='{_paste['raw']}'>Raw</a></b>"
        await huehue.edit(c1m, parse_mode="html")
    else:
        return
    
