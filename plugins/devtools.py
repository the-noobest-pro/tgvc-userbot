# PORTED EVAL FROM TheCodents/DevelopersUserbot
# PORTED BASH FROM TeamUltroid/Ultroid

import traceback
import aiohttp
import json
import sys
import os
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
        
        

TMP_DOWNLOAD_DIRECTORY = "/app/pastebin/"        
        
@Client.on_message(self_or_contact_filter & filters.command('paste', prefixes='!'))
async def pastebin(client, message: Message):
    huehue = await message.reply_text("`...`")
    downloaded_file_name = None

    if message.reply_to_message and message.reply_to_message.media:
        downloaded_file_name_res = await message.reply_to_message.download(
            file_name=TMP_DOWNLOAD_DIRECTORY
        )
        m_list = None
        with open(downloaded_file_name_res, "rb") as fd:
            m_list = fd.readlines()
        downloaded_file_name = ""
        for m in m_list:
            downloaded_file_name += m.decode("UTF-8")
        os.remove(downloaded_file_name_res)
    elif message.reply_to_message:
        downloaded_file_name = message.reply_to_message.text.html
    # elif len(message.command) > 1:
    #     downloaded_file_name = " ".join(message.command[1:])
    else:
        await huehue.edit("`Reply to a File or Text`")
        return

    if downloaded_file_name is None:
        await huehue.edit("`Reply to a File or Text`")
        return

    json_paste_data = {
        "content": downloaded_file_name
    }

    # a dictionary to store different pastebin URIs
    paste_bin_store_s = {
        "deldog": "https://dogbin.up.railway.app",
        "nekobin": "https://nekobin.com/api/documents"
    }

    chosen_store = "nekobin"
    if len(message.command) == 2:
        chosen_store = message.command[1]

    # get the required pastebin URI
    paste_store_url = paste_bin_store_s.get(
        chosen_store,
        paste_bin_store_s["nekobin"]
    )
    paste_store_base_url_rp = urlparse(paste_store_url)

    # the pastebin sites, respond with only the "key"
    # we need to prepend the BASE_URL of the appropriate site
    paste_store_base_url = paste_store_base_url_rp.scheme + "://" + \
        paste_store_base_url_rp.netloc

    async with aiohttp.ClientSession() as session:
        response_d = await session.post(paste_store_url, json=json_paste_data)
        response_jn = await response_d.json()

    # we got the response from a specific site,
    # this dictionary needs to be scrapped
    # using bleck megick to find the "key"
    t_w_attempt = bleck_megick(response_jn)
    required_url = json.dumps(
        t_w_attempt, sort_keys=True, indent=4
    ) + "\n\n #ERROR"
    if t_w_attempt is not None:
        required_url = "**Patsted to Nekobin**\n" + paste_store_base_url + "/" + "Raw" + "/" + t_w_attempt

    await huehue.edit(required_url)


def bleck_megick(dict_rspns):
    # first, try getting "key", dirctly
    first_key_r = dict_rspns.get("key")
    # this is for the "del.dog" site
    if first_key_r is not None:
        return first_key_r
    check_if_result_ests = dict_rspns.get("result")
    if check_if_result_ests is not None:
        # this is for the "nekobin.com" site
        second_key_a = check_if_result_ests.get("key")
        if second_key_a is not None:
            return second_key_a
    # TODO: is there a better way?
    return None
