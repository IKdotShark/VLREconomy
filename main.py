import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from asyncio import sleep
from OnlineParser import get_players_online
import asyncio
import subprocess

load_dotenv()

TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Инициализация бота
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)


@bot.command(name='restart')
#@has_permissions(administrator=True)
async def restart_cmd(ctx):
    message = await ctx.send("Бот перезапускается. Пожалуйста, не используйте его в течение следующих 2 минут.")
    await asyncio.sleep(60)

    subprocess.call(['systemctl', 'restart', 'discordbot'])

    await asyncio.sleep(120)
    await message.delete()

# Команда /history_guns
@bot.command(name='history_guns')
async def history_guns_cmd(ctx):
    guns_log_file = "GunsLogs.txt"
    await ctx.author.send(file=discord.File(guns_log_file))
    await ctx.message.delete()

# Команда /historyMe
@bot.command(name='historyMe')
async def history_me_cmd(ctx):
    finance_log_file = "FinanceLogs.txt"
    await ctx.author.send(file=discord.File(finance_log_file))
    await ctx.message.delete()

# Команда /rules
@bot.command(name='rules')
async def rules_cmd(ctx):
    rules_file = "rules.txt"
    if os.path.exists(rules_file):
        with open(rules_file, 'r', encoding='utf-8') as file:
            rules_content = file.read()
        await ctx.send(rules_content)
    else:
        await ctx.send("Файл с правилами не найден.")
    await ctx.message.delete()

# Команда /commands (вместо /help)
@bot.command(name='commands')
async def commands_cmd(ctx):
    embed = discord.Embed(title="Доступные команды", description="Список доступных команд", color=0x00ff00)
    embed.add_field(name="/money", value="Показать состояние общака", inline=False)
    embed.add_field(name="/guns", value="Показать наличие оружия", inline=False)
    embed.add_field(name="/history_guns", value="Отправить файл с историей оружия", inline=False)
    embed.add_field(name="/historyMe", value="Отправить файл с историей финансов", inline=False)
    embed.add_field(name="/rules", value="Показать правила", inline=False)
    await ctx.send(embed=embed)
    await ctx.message.delete()

# Обработка взаимодействий с кнопками
@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"].startswith("take_") or interaction.data["custom_id"].startswith("put_"):
        await handle_gun_interaction(interaction)
    elif interaction.data["custom_id"] in ["replenish", "withdraw"]:
        await handle_finance_interaction(interaction)

@bot.event
async def on_ready():
    while True:
        players_online = get_players_online()
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(players_online))
        await sleep(15)

# Импортируем команды и обработчики взаимодействий из Finance.py
from Finance import setup as setup_finance, handle_finance_interaction

# Импортируем команды и обработчики взаимодействий из guns.py
from guns import setup as setup_guns, handle_gun_interaction

# Регистрация команд
setup_finance(bot)
setup_guns(bot)

# Запуск бота
bot.run((TOKEN))

