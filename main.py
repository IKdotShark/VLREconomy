import os
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Инициализация бота
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Команда /history_guns
@bot.command(name='history_guns')
async def history_guns_cmd(ctx):
    guns_log_file = "GunsLogs.txt"
    await ctx.author.send(file=discord.File(guns_log_file))
    await ctx.message.delete()

# Обработка взаимодействий с кнопками
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"].startswith("take_") or interaction.data["custom_id"].startswith("put_"):
        await handle_gun_interaction(interaction)
    elif interaction.data["custom_id"] in ["replenish", "withdraw"]:
        await handle_finance_interaction(interaction)

# Импортируем команды и обработчики взаимодействий из Finance.py
from Finance import setup as setup_finance, handle_finance_interaction

# Импортируем команды и обработчики взаимодействий из guns.py
from guns import setup as setup_guns, handle_gun_interaction

# Регистрация команд
setup_finance(bot)
setup_guns(bot)

# keep_alive()  # Раскомментируйте, если используете Flask сервер для keep-alive
bot.run(TOKEN)
