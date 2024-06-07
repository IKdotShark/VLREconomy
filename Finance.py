import os
import discord
from discord.ext import commands
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

# Загрузка истории транзакций из файла
def load_history():
    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    else:
        return []

# Сохранение истории транзакций в файл
def save_history(history):
    with open(history_file, 'w', encoding='utf-8') as file:
        file.write("\n".join(history))

# Инициализация состояния общака и истории транзакций
obshak = load_obshak()
history = load_history()

money_message = None

def setup(bot):
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

    @bot.command(name='history_money')
    async def history_money(ctx):
        history_message = "\n".join(history[-100:]) if history else "История пуста."
        await ctx.author.send(f"Последние 100 операций:\n{history_message}")
        await ctx.message.delete()

    @bot.command(name='historyMe')
    async def history_me(ctx):
        await ctx.author.send(file=discord.File(history_file))
        await ctx.message.delete()

    @bot.command(name='clear')
    async def clear(ctx, key: str):
        CLEAR_KEY = os.getenv('CLEARKEY')
        if key == CLEAR_KEY:
            with open(history_file, 'w', encoding='utf-8') as file:
                file.write("")
            with open(obshak_file, 'w', encoding='utf-8') as file:
                file.write(json.dumps({'obshak': 0}))
            with open(state_file, 'w', encoding='utf-8') as file:
                file.write("")
            global obshak, history
            obshak = 0
            history = []
            await ctx.send("Файлы успешно очищены.", delete_after=10)
        else:
            await ctx.send("Неверный ключ.", delete_after=10)
        await ctx.message.delete()

async def handle_finance_interaction(interaction):
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
                save_obshak(obshak)
                timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
                history.append(f"[{timestamp}] {username} пополнил общак на {amount} рублей.")
                save_history(history)
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
                    save_obshak(obshak)
                    history.append(f"[{timestamp}] {username} снял {amount} рублей из общака. Причина: {reason}.")
                    save_history(history)
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
