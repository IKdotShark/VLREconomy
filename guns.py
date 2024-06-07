import os
import discord
from discord.ui import Button, View, Modal, TextInput
import json
from datetime import datetime, timedelta

guns_file = "guns.json"
guns_log_file = "GunsLogs.txt"
guns_list = [
    "СВ-98",
    "Орсис Т-5000",
    "DVL Урбана",
    "DVL Волкодав",
    "L96A1",
    "Barret Mrad",
    "CheyTac",
    "Mar 10",
    "СВЧ",
    "Mk 18 Mjolnir"
]

# Загрузка состояния оружия из файла
def load_guns():
    if os.path.exists(guns_file):
        with open(guns_file, 'r') as file:
            return json.load(file)
    else:
        return {gun: 0 for gun in guns_list}

# Сохранение состояния оружия в файл
def save_guns(guns):
    with open(guns_file, 'w') as file:
        json.dump(guns, file)

# Сохранение логов оружия в файл
def save_gun_log(message):
    timestamp = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    with open(guns_log_file, 'a') as file:
        file.write(f"[{timestamp}] {message}\n")

guns = load_guns()

class GunActionModal(Modal):
    def __init__(self, gun, action):
        super().__init__(title=f"{action} {gun}")
        self.gun = gun
        self.action = action
        self.username = TextInput(label="Ник игрока", placeholder="Введите ник")
        self.add_item(self.username)

    async def on_submit(self, interaction: discord.Interaction):
        global guns
        username = self.username.value
        if self.action == "Взять":
            if guns[self.gun] > 0:
                guns[self.gun] -= 1
                save_guns(guns)
                save_gun_log(f"{username} взял {self.gun}")
                await interaction.response.send_message(f"{username} взял {self.gun}", ephemeral=True)
            else:
                await interaction.response.send_message(f"{self.gun} нет в наличии.", ephemeral=True)
        elif self.action == "Положить":
            guns[self.gun] += 1
            save_guns(guns)
            save_gun_log(f"{username} положил {self.gun}")
            await interaction.response.send_message(f"{username} положил {self.gun}", ephemeral=True)
        await update_guns_message(interaction.channel)

async def update_guns_message(channel):
    global guns_message
    embed = discord.Embed(title="Наличие оружия")
    for gun in guns_list:
        embed.add_field(name=gun, value=f"{guns[gun]} шт.", inline=False)

    view = View()
    for gun in guns_list:
        view.add_item(Button(label=f"Положить {gun}", style=discord.ButtonStyle.green, custom_id=f"put_{gun}"))
        view.add_item(Button(label=f"Взять {gun}", style=discord.ButtonStyle.red, custom_id=f"take_{gun}"))

    if guns_message:
        await guns_message.edit(embed=embed, view=view)
    else:
        guns_message = await channel.send(embed=embed, view=view)

guns_message = None

def setup(bot):
    @bot.command(name='guns')
    async def guns_cmd(ctx):
        global guns_message
        if guns_message:
            await guns_message.delete()

        embed = discord.Embed(title="Наличие оружия")
        for gun in guns_list:
            embed.add_field(name=gun, value=f"{guns[gun]} шт.", inline=False)

        view = View()
        for gun in guns_list:
            view.add_item(Button(label=f"Положить {gun}", style=discord.ButtonStyle.green, custom_id=f"put_{gun}"))
            view.add_item(Button(label=f"Взять {gun}", style=discord.ButtonStyle.red, custom_id=f"take_{gun}"))

        guns_message = await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

async def handle_gun_interaction(interaction: discord.Interaction):
    if interaction.data["custom_id"].startswith("take_"):
        gun = interaction.data["custom_id"].replace("take_", "")
        await interaction.response.send_modal(GunActionModal(gun, "Взять"))
    elif interaction.data["custom_id"].startswith("put_"):
        gun = interaction.data["custom_id"].replace("put_", "")
        await interaction.response.send_modal(GunActionModal(gun, "Положить"))

