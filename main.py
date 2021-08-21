"""
tgvc-userbot, Telegram Voice Chat Userbot
Copyright (C) 2021  Dash Eclipse

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from os import environ

import logging
from logging.handlers import RotatingFileHandler

from pyrogram import Client, idle

API_ID = int(environ["API_ID"])
API_HASH = environ["API_HASH"]
SESSION_NAME = environ["SESSION_NAME"]

PLUGINS = dict(
    root="plugins",
    include=[
        "vc." + environ["PLUGIN"],
        "ping",
        "sysinfo",
        "stream",
        "devtools"
    ]
)

app = Client(SESSION_NAME, API_ID, API_HASH, plugins=PLUGINS)

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.parser.html").setLevel(logging.WARNING)
logging.getLogger("pyrogram.connection.connection").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING,
                    format='[%(asctime)s - %(levelname)s] - %(name)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S',
                    handlers=[
                        RotatingFileHandler(
                            "/app/tgvcuserbot.txt", maxBytes=2048000, backupCount=10),
                        logging.StreamHandler()
                    ])

app.start()
print('>>> USERBOT STARTED')
idle()
app.stop()
print('\n>>> USERBOT STOPPED')
