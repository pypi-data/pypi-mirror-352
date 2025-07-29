import threading
import random
import asyncio
import aiohttp
import logging
import re
from bs4 import BeautifulSoup
from typing import Dict

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
logger = logging.getLogger("FunpayACE")


class FunpayAce:
    BASE_URL = "https://funpay.com"
    HEADERS = {"X-Requested-With": "XMLHttpRequest"}

    def __init__(self, golden_key: str):
        self.golden_key = golden_key
        self._loop = None

    def forever_online(self) -> None:
        """Запускает вечный онлайн в отдельном потоке с event loop."""

        def run():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._forever_online())

        threading.Thread(target=run, daemon=True).start()

    async def _forever_online(self) -> None:
        logger.info("Вечный онлайн запущен.")
        async with aiohttp.ClientSession(cookies={"golden_key": self.golden_key}) as session:
            while True:
                try:
                    async with session.post(f"{self.BASE_URL}/runner/") as resp:
                        if resp.status == 200:
                            logger.info("Ping-запрос для вечного онлайна успешно отправлен.")
                        else:
                            logger.warning(f"Не удалось отправить ping-запрос: HTTP {resp.status}")
                except Exception as e:
                    logger.exception(f"Ошибка при выполнении ping-запроса: {e}")
                await asyncio.sleep(random.randint(45, 100))

    def lot_auto_boost(self, game_id: int, node_id: int) -> None:
        """Запускает автоподнятие лотов в отдельном потоке с event loop."""

        def run():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._lot_auto_boost(game_id, node_id))

        threading.Thread(target=run, daemon=True).start()

    async def _lot_auto_boost(self, game_id: int, node_id: int) -> None:
        logger.info(f"Автоподнятие лотов запущено (Игра: {game_id}, Узел: {node_id}).")

        form = aiohttp.FormData()
        form.add_field('game_id', str(game_id))
        form.add_field('node_id', str(node_id))

        headers = self.HEADERS | {"Cookie": f"golden_key={self.golden_key};"}

        async with aiohttp.ClientSession(headers=headers) as session:
            while True:
                try:
                    async with session.post(f"{self.BASE_URL}/lots/raise", data=form) as resp:
                        if resp.status == 200:
                            json_data = await resp.json()
                            logger.info(f"Ответ сервера: {json_data.get('msg')}")
                        else:
                            logger.warning(f"Не удалось поднять лоты: HTTP {resp.status}")
                except Exception as e:
                    logger.exception(f"Ошибка при автоподнятии лотов: {e}")
                await asyncio.sleep(random.randint(60, 300))

    async def get_balance(self) -> Dict[str, float]:
        """
        Возвращает словарь с балансами аккаунта Funpay:
            {
                "RUB": 123.45,
                "USD": 12.34,
                "EUR": 5.67
            }
        """
        try:
            async with aiohttp.ClientSession(cookies={"golden_key": self.golden_key}) as session:
                async with session.get(f"{self.BASE_URL}/account/balance") as resp:
                    if resp.status != 200:
                        raise Exception(f"Не удалось получить баланс: HTTP {resp.status}")

                    html = await resp.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    balances_block = soup.find('span', class_='balances-list')

                    if not balances_block:
                        raise ValueError("Блок с балансами не найден на странице.")

                    values = balances_block.find_all('span', class_='balances-value')
                    if len(values) < 3:
                        raise ValueError("Не удалось найти все три валюты (RUB, USD, EUR).")

                    def parse(text: str) -> float:
                        match = re.search(r'([\d\s,.]+)', text)
                        if not match:
                            raise ValueError(f"Неверный формат баланса: {text}")
                        return float(match.group(1).replace(" ", "").replace(",", "."))

                    return {
                        "RUB": parse(values[0].get_text(strip=True)),
                        "USD": parse(values[1].get_text(strip=True)),
                        "EUR": parse(values[2].get_text(strip=True)),
                    }

        except Exception as e:
            raise RuntimeError(f"Ошибка при получении баланса: {e}")
