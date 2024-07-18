import os
import discord
from discord.ui import Button, View, Modal, TextInput
from datetime import datetime, timedelta
import json

# Файлы для хранения данных
obshak_file = "obshak.json"
history_file = "FinanceLogs.txt"
state_file = "ObshakState.txt"

# Загрузка состояния общака из файла
def load_obshak():
    if os.path.exists(obshak_file):
        with open(obshak_file, 'r') as file:
            return json.load(file).get('obshak', 0)
    else:
        return 0

# Сохранение состояния общака в файл
def save_obshak(obshak):
    with open(obshak_file, 'w') as file:
        json.dump({'obshak': obshak}, file)

# Загрузка состояния общака из файла
def load_state():
    if os.path.exists(state_file):
        with open(state_file, 'r') as file:
            return file.read()
    else:
        return ""

# Сохранение состояния общака в файл
def save_state(state):
    with open(state_file, 'w') as file:
        file.write(state)

# Сохранение логов в файл
def save_log(message):
    timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    with open(history_file, 'a') as file:
        file.write(f"[{timestamp}] {message}\n")

obshak = load_obshak()

class FinanceModal(Modal):
    def __init__(self, action):
        super().__init__(title=action)
        self.action = action
        self.username = TextInput(label="Ник игрока", placeholder="Введите ник")
        self.amount = TextInput(label="Сумма", placeholder="Введите сумму")
        self.reason = TextInput(label="Причина", placeholder="Введите причину", style=discord.TextStyle.paragraph)
        self.add_item(self.username)
        self.add_item(self.amount)
        if self.action == "Снять":
            self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        global obshak
        username = self.username.value
        amount = int(self.amount.value.replace(' ', ''))
        reason = self.reason.value if self.action == "Снять" else None

        if self.action == "Пополнить":
            obshak += amount
            save_log(f"{username} пополнил общак на {amount:,} руб.".replace(',', ' '))
        elif self.action == "Снять":
            if obshak >= amount:
                obshak -= amount
                save_log(f"{username} снял из общака {amount:,} руб. Причина: {reason}".replace(',', ' '))
            else:
                await interaction.response.send_message("Недостаточно средств в общаке.", ephemeral=True)
                return

        save_obshak(obshak)
        save_state(f"{obshak:,}".replace(',', ' '))
        await interaction.response.send_message(f"Текущее состояние общака: {obshak:,} руб.".replace(',', ' '), ephemeral=True)
        await update_finance_message(interaction.channel)

async def update_finance_message(channel):
    global finance_message
    state = load_state()
    embed = discord.Embed(title="Состояние общака", description=f"{state} руб.")

    view = View()
    view.add_item(Button(label="Пополнить", style=discord.ButtonStyle.green, custom_id="replenish"))
    view.add_item(Button(label="Снять", style=discord.ButtonStyle.red, custom_id="withdraw"))

    if finance_message:
        await finance_message.edit(embed=embed, view=view)
    else:
        finance_message = await channel.send(embed=embed, view=view)

finance_message = None

def setup(bot):
    @bot.command(name='money')
    async def money_cmd(ctx):
        global finance_message
        if finance_message:
            await finance_message.delete()

        state = load_state()
        embed = discord.Embed(title="Состояние общака", description=f"{state} руб.")

        view = View()
        view.add_item(Button(label="Пополнить", style=discord.ButtonStyle.green, custom_id="replenish"))
        view.add_item(Button(label="Снять", style=discord.ButtonStyle.red, custom_id="withdraw"))

        finance_message = await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

async def handle_finance_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"] == "replenish":
        await interaction.response.send_modal(FinanceModal("Пополнить"))
    elif interaction.data["custom_id"] == "withdraw":
        await interaction.response.send_modal(FinanceModal("Снять"))
