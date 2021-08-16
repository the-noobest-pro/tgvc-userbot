from os import environ
from pyrogram import Client, idle

API_ID = int(environ["API_ID"])
API_HASH = environ["API_HASH"]
SESSION_NAME = environ["SESSION_NAME"]

bot = Client(SESSION_NAME, API_ID, API_HASH)
bot.start()
