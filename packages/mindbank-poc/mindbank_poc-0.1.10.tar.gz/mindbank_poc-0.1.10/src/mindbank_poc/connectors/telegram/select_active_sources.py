import aiohttp
import asyncio
import json
import os

API_URL = "http://localhost:8000"
STATE_FILE = os.path.join(os.path.dirname(__file__), "connector_state.json")


def load_state():
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

async def get_current_config(connector_id, access_token):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{API_URL}/connectors/{connector_id}/handshake",
            headers={"Authorization": f"Bearer {access_token}"}
        ) as resp:
            data = await resp.json()
            return data.get("current_config", {})

async def update_config(connector_id, access_token, config):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_URL}/connectors/{connector_id}/config",
            json=config,
            headers={"Authorization": f"Bearer {access_token}"}
        ) as resp:
            if resp.status == 200:
                print("Конфиг успешно обновлён!")
            else:
                print(f"Ошибка обновления: {await resp.text()}")

def choose_sources(available_sources):
    print("Доступные источники:")
    for idx, src in enumerate(available_sources):
        print(f"{idx+1}. {src['name']} (id: {src['id']})")
    selected = input("Введите номера активных источников через запятую (например: 1,3,5): ")
    selected_idxs = set(int(x.strip())-1 for x in selected.split(",") if x.strip().isdigit())
    for idx, src in enumerate(available_sources):
        src["monitoring_status"] = "monitored" if idx in selected_idxs else "inactive"
    return available_sources

async def main():
    if not os.path.exists(STATE_FILE):
        print(f"Файл состояния не найден: {STATE_FILE}")
        return
    state = load_state()
    connector_id = state.get("connector_id")
    access_token = state.get("access_token")
    if not connector_id or not access_token:
        print("connector_id или access_token не найдены в файле состояния.")
        return

    config = await get_current_config(connector_id, access_token)
    available_sources = config.get("available_sources", [])
    if not available_sources:
        print("Нет доступных источников в конфиге. Сначала выполните синхронизацию источников.")
        return

    updated_sources = choose_sources(available_sources)
    config["available_sources"] = updated_sources

    await update_config(connector_id, access_token, config)

if __name__ == "__main__":
    asyncio.run(main()) 