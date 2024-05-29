import os
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime, timedelta
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


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Состояние общака и история транзакций
obshak = 0
history = []
money_message = None

# Команда /money
@bot.command(name='money')
async def money(ctx):
    global money_message
    if money_message:
        await money_message.delete()

    embed = discord.Embed(title="Информация")
    embed.add_field(name="Состояние общака", value=f"{obshak} рублей")

    view = View()
    view.add_item(Button(label="Пополнить", style=discord.ButtonStyle.green, custom_id="replenish"))
    view.add_item(Button(label="Снять", style=discord.ButtonStyle.red, custom_id="withdraw"))

    money_message = await ctx.send(embed=embed, view=view)
    await ctx.message.delete()

# Команда /history
@bot.command(name='history')
async def history_cmd(ctx):
    history_message = "\n".join(history) if history else "История пуста."
    await ctx.author.send(f"История транзакций:\n{history_message}")
    await ctx.message.delete()

# Обработка нажатий на кнопки
@bot.event
async def on_interaction(interaction: discord.Interaction):
    global obshak, history, money_message

    if interaction.data["custom_id"] == "replenish":
        class ReplenishModal(Modal):
            def __init__(self):
                super().__init__(title="Пополнить общак")
                self.username = TextInput(label="Ник игрока", placeholder="Введите ник")
                self.amount = TextInput(label="Сумма", placeholder="Введите сумму", style=discord.TextStyle.short)
                self.add_item(self.username)
                self.add_item(self.amount)

            async def on_submit(self, interaction: discord.Interaction):
                global obshak, money_message
                username = self.username.value
                amount = int(self.amount.value)
                obshak += amount
                timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
                history.append(f"[{timestamp}] {username} пополнил общак на {amount} рублей.")
                await interaction.response.send_message(f"{username} пополнил общак на {amount} рублей. Текущий баланс: {obshak} рублей.", ephemeral=True)
                await update_money_message(interaction.channel)

        await interaction.response.send_modal(ReplenishModal())

    elif interaction.data["custom_id"] == "withdraw":
        class WithdrawModal(Modal):
            def __init__(self):
                super().__init__(title="Снять из общака")
                self.username = TextInput(label="Ник игрока", placeholder="Введите ник")
                self.amount = TextInput(label="Сумма", placeholder="Введите сумму", style=discord.TextStyle.short)
                self.reason = TextInput(label="Причина", placeholder="Введите причину", style=discord.TextStyle.paragraph)
                self.add_item(self.username)
                self.add_item(self.amount)
                self.add_item(self.reason)

            async def on_submit(self, interaction: discord.Interaction):
                global obshak, money_message  
                username = self.username.value
                amount = int(self.amount.value)
                reason = self.reason.value
                timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
                if amount > obshak:
                    await interaction.response.send_message(f"Недостаточно средств в общаке для снятия {amount} рублей.", ephemeral=True)
                else:
                    obshak -= amount
                    history.append(f"[{timestamp}] {username} снял {amount} рублей из общака. Причина: {reason}.")
                    await interaction.response.send_message(f"{username} снял {amount} рублей из общака. Причина: {reason}. Текущий баланс: {obshak} рублей.", ephemeral=True)
                    await update_money_message(interaction.channel)

        await interaction.response.send_modal(WithdrawModal())

async def update_money_message(channel):
    global money_message
    if money_message:
        embed = discord.Embed(title="Информация")
        embed.add_field(name="Состояние общака", value=f"{obshak} рублей")

        view = View()
        view.add_item(Button(label="Пополнить", style=discord.ButtonStyle.green, custom_id="replenish"))
        view.add_item(Button(label="Снять", style=discord.ButtonStyle.red, custom_id="withdraw"))

        await money_message.edit(embed=embed, view=view)

keep_alive()
bot.run(os.getenv('DISCORD_BOT_TOKEN'))