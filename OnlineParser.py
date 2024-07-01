import requests
from bs4 import BeautifulSoup
import time


# Функция для получения информации о количестве игроков онлайн
def get_players_online():
    while True:
        url = "https://wargm.ru/server/66523"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем элемент, содержащий информацию о количестве игроков онлайн
        online_element = soup.find('div', {'class': 'f-r ml-5 fw-b'})
        if online_element:
            players_online = online_element.text.strip()
            return players_online
        return "Не удалось получить информацию о количестве игроков онлайн."

        # Ждем 15 секунд перед следующим обновлением
        time.sleep(15)
