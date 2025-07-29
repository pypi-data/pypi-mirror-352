"""
Клиент коннектора для тестирования API с динамическим протоколом.

Запуск:
    python -m tests.test_connector_client 
"""

import os
import sys
import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
import httpx
import argparse

# URL API по умолчанию
DEFAULT_API_URL = "http://localhost:8000"

class ConnectorClient:
    """
    Клиент для демонстрации работы коннектора с API, использующим динамический протокол.
    Реализует регистрацию, рукопожатие /handshake и отправку данных.
    Поддерживает многоэтапную настройку и динамическую конфигурацию.
    """
    
    def __init__(
        self, 
        connector_type: str,
        api_url: str = DEFAULT_API_URL,
        polling_interval: int = 15,
        config: Optional[Dict[str, Any]] = None,
        integration_key: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        initial_config_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Инициализирует клиент динамического коннектора.
        
        Args:
            connector_type: Тип коннектора (например, "telegram")
            api_url: URL API сервера
            polling_interval: Интервал поллинга в секундах
            config: Начальная конфигурация (если None, будет использоваться пустой словарь)
            integration_key: Ключ интеграции для регистрации (если None, нужно запросить у пользователя)
            capabilities: Список возможностей коннектора (например, "oauth", "two-factor")
            initial_config_schema: Схема конфигурации для регистрации
        """
        self.connector_type = connector_type
        self.api_url = api_url
        self.polling_interval = polling_interval
        self.collector_id = f"{connector_type}-collector"
        self.connector_id: Optional[str] = None
        self.stage = "unregistered"
        self.enabled = False
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.running = False
        self.integration_key = integration_key
        self.access_token: Optional[str] = None
        self.capabilities = capabilities or []
        self.config_schema = initial_config_schema or { 
            "properties": {
                "polling_interval": {"type": "integer", "default": polling_interval}
            }
        }
        self.steps = []
        self.current_config = config or {}
        self.config_validation = {"valid": False, "errors": []}
        self.messages = []
        self.group_id_counter = 0
    
    async def register(self) -> bool:
        print(f"🔌 Регистрация коннектора типа '{self.connector_type}'...")
        if not self.integration_key:
            print("❌ Ключ интеграции не найден.")
            return False
            
        register_data = {
            "type": self.connector_type,
            "metadata": {
                "version": "1.0.0",
                "description": f"Динамический коннектор {self.connector_type}",
                "author": "Example Client Script"
            },
            "config_schema": self.config_schema,
            "integration_key": self.integration_key,
            "capabilities": self.capabilities
        }
        
        try:
            response = await self.http_client.post(
                f"{self.api_url}/connectors/register",
                json=register_data
            )
            if response.status_code == 200:
                data = response.json()
                self.connector_id = data["connector_id"]
                self.access_token = data["access_token"]
                print(f"✅ Коннектор зарегистрирован: ID={self.connector_id}, Token={self.access_token[:8]}...")
                # Сразу делаем handshake для получения начального состояния
                if await self.handshake():
                    return True
                else:
                    print("⚠️ Регистрация успешна, но первый handshake не удался.")
                    return False
            else:
                print(f"❌ Ошибка регистрации: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Исключение при регистрации: {e}")
            return False

    async def _update_state_from_handshake(self, data):
        # Обновляем основные поля состояния
        self.stage = data.get("stage", self.stage)
        self.enabled = data.get("enabled", self.enabled)
        self.steps = data.get("steps", self.steps)
        self.current_config = data.get("current_config", self.current_config)
        self.config_validation = data.get("config_validation", self.config_validation)
        self.messages = data.get("messages", self.messages)
        
        # Обновляем токен, если он пришел
        if data.get("auth_token"):
            # Только если токен действительно изменился
            if self.access_token != data["auth_token"]:
                 print(f"🔑 Токен доступа обновлен: {self.access_token[:8]}... -> {data['auth_token'][:8]}...")
                 self.access_token = data["auth_token"]
            else:
                # Можно добавить debug лог, что токен пришел, но не изменился
                pass

    async def handshake(self) -> bool: # Убрали V2 из названия метода
        if not self.connector_id or not self.access_token:
            print("❌ ID коннектора или токен доступа отсутствуют для handshake.")
            return False
            
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            print("🤝 Запрос Handshake...")
            # Используем единый эндпоинт /handshake
            response = await self.http_client.get(
                f"{self.api_url}/connectors/{self.connector_id}/handshake", headers=headers 
            )
            if response.status_code == 200:
                data = response.json()
                await self._update_state_from_handshake(data)
                print(f"  Ответ Handshake: Stage={self.stage}, Enabled={self.enabled}, ConfigValid={self.config_validation.get('valid')}")
                if self.steps:
                    print("  Шаги настройки:")
                    for step in self.steps:
                        # Используем get для безопасного доступа к ключам
                        print(f"    - {step.get('id')}: {step.get('status')} - {step.get('title', step.get('message', ''))}")
                if self.messages:
                    print("  Сообщения от сервера:")
                    for msg in self.messages: print(f"    - [{msg.get('level')}] {msg.get('text')}")
                return True
            else:
                print(f"❌ Ошибка Handshake: {response.status_code} - {response.text}")
                if response.status_code == 401:
                    print("  Токен недействителен. Возможно, требуется обработка ротации токена или остановка.")
                    # В зависимости от логики, можно попытаться использовать previous_token или остановить клиент
                    self.stage = "unregistered" # Пример: считаем коннектор невалидным
                return False
        except Exception as e:
            print(f"❌ Исключение при Handshake: {e}")
            return False

    async def process_setup_steps(self):
        if self.stage != "setup" or not self.enabled:
            return False 

        pending_steps = [step for step in self.steps if step.get("status") == "pending"]
        if not pending_steps:
            print("ℹ️ Нет ожидающих шагов настройки (pending).")
            return True # Считаем успешным, если шагов нет

        step_processed = False
        for step in pending_steps:
            step_id = step.get("id")
            print(f"⚙️ Обработка шага '{step_id}': {step.get('title', step.get('message', ''))}")
            
            # Имитация получения значения для шага
            value_for_step = None
            # Если это шаг initial_configuration, передадим тестовый конфиг
            if step_id == "initial_configuration":
                 # Пытаемся заполнить обязательные поля из схемы
                 required_fields = self.config_schema.get("required", [])
                 value_for_step = {}
                 for field in required_fields:
                     value_for_step[field] = f"auto_value_for_{field}"
                 # Добавляем опциональные с default значением, если есть
                 for field, props in self.config_schema.get("properties", {}).items():
                     if field not in value_for_step and "default" in props:
                          value_for_step[field] = props["default"]
            else:
                # Для других шагов просто генерируем тестовое значение
                value_for_step = f"auto_value_for_{step_id}"
            
            if value_for_step is not None:
                print(f"  Предоставлено значение: {json.dumps(value_for_step)}")
                if await self.submit_step_input(step_id, value_for_step):
                    step_processed = True
                    # После успешной отправки шага делаем handshake, чтобы обновить состояние
                    await self.handshake() 
                    return True # Возвращаем True после обработки одного шага
                else:
                    print(f"  Не удалось отправить данные для шага '{step_id}'.")
                    return False # Прерываем обработку, если шаг не удался
            else:
                 print(f"  Не удалось получить значение для шага '{step_id}'. Пропуск.")
        
        return step_processed # Возвращаем True, если хотя бы один шаг был успешно обработан

    async def submit_step_input(self, step_id, value):
        if not self.connector_id or not self.access_token:
            print("❌ Невозможно отправить ввод шага: нет ID или токена.")
            return False
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"step_id": step_id, "value": value}
        try:
            response = await self.http_client.post(
                f"{self.api_url}/connectors/{self.connector_id}/input", json=payload, headers=headers
            )
            if response.status_code == 200:
                print(f"✅ Данные для шага '{step_id}' успешно отправлены.")
                return True
            else:
                print(f"❌ Ошибка отправки данных для шага '{step_id}': {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Исключение при отправке данных для шага '{step_id}': {e}")
            return False
            
    async def ensure_configuration(self):
        if self.stage != "configuration" or not self.enabled:
            return False 

        if self.config_validation.get("valid"):
            print("ℹ️ Конфигурация валидна.")
            # Если конфиг валиден, но этап все еще CONFIGURATION, значит, нужно сделать handshake
            # чтобы сервер перевел нас в READY (если все шаги выполнены)
            await self.handshake() 
            return True # Возвращаем True, так как текущая конфигурация валидна

        print(f"🛠️ Конфигурация невалидна. Ошибки: {self.config_validation.get('errors')}")
        config_to_set = {}
        missing = self.config_validation.get("missing_fields", [])
        invalid = self.config_validation.get("invalid_fields", []) # Учитываем и невалидные поля
        required_from_schema = self.config_schema.get("required", [])
        properties_schema = self.config_schema.get("properties", {})

        fields_to_fix = {f['field'] for f in missing} | {f['field'] for f in invalid}
        
        for field_name in fields_to_fix:
            # Пытаемся получить default значение из схемы
            default_value = properties_schema.get(field_name, {}).get("default")
            if default_value is not None:
                 config_to_set[field_name] = default_value
            # Если default нет, генерируем простое значение в зависимости от типа
            elif field_name in properties_schema:
                field_type = properties_schema[field_name].get("type")
                if field_type == "string": config_to_set[field_name] = f"auto_value_for_{field_name}"
                elif field_type == "integer": config_to_set[field_name] = 0
                elif field_type == "number": config_to_set[field_name] = 0.0
                elif field_type == "boolean": config_to_set[field_name] = False
                elif field_type == "array": config_to_set[field_name] = []
                elif field_type == "object": config_to_set[field_name] = {}
                else: config_to_set[field_name] = "unknown_type_default"
            else:
                 config_to_set[field_name] = f"dummy_value_for_{field_name}" # Запасной вариант
            
        if config_to_set:
            print(f"  Попытка установить частичную конфигурацию: {json.dumps(config_to_set)}")
            if await self.update_partial_config(config_to_set):
                # После обновления конфига делаем handshake, чтобы узнать новое состояние
                await self.handshake()
                return False # Возвращаем False, т.к. мы только что пытались исправить конфиг
            else:
                print("  Не удалось обновить конфигурацию.")
                return False
        else:
            print("  Не удалось определить значения для невалидной конфигурации.")
            return False

    async def update_partial_config(self, partial_config):
        if not self.connector_id or not self.access_token:
            print("❌ Невозможно обновить конфиг: нет ID или токена.")
            return False
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {"partial_config": partial_config}
        try:
            response = await self.http_client.post(
                f"{self.api_url}/connectors/{self.connector_id}/config", json=payload, headers=headers
            )
            if response.status_code == 200:
                print(f"✅ Частичная конфигурация успешно обновлена.")
                return True
            else:
                print(f"❌ Ошибка обновления частичной конфигурации: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Исключение при обновлении частичной конфигурации: {e}")
            return False

    async def collect_data_from_source(self):
        # Имитация сбора данных
        print("🔎 Сбор данных из источника...")
        await asyncio.sleep(0.5) # Небольшая задержка для имитации
        self.group_id_counter += 1
        current_group_id = f"group_{self.collector_id}_{self.group_id_counter}"
        # Генерируем 1-3 сообщения
        num_messages = random.randint(1, 3)
        data_items = []
        for i in range(num_messages):
            data_items.append(
                 {"id": f"msg{i+1}", "text": f"Сообщение {i+1} для {current_group_id} в {datetime.now().isoformat()}"}
            )
        print(f"  Собрано {len(data_items)} элементов.")
        return data_items, current_group_id
        
    async def format_to_raw_entry(self, item, group_id, is_last=False):
        # Форматирование данных в RawEntry
        entry = {
            "collector_id": self.collector_id,
            "group_id": group_id,
            "entry_id": f"{item['id']}_{uuid.uuid4()}", 
            "type": "text", # Пример типа
            "payload": { "content": item["text"] },
            "metadata": {
                "source": self.connector_type,
                "is_last": is_last,
                "collected_at": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat() # Используем текущее время как timestamp записи
        }
        return entry
        
    async def send_data_entry(self, entry):
        # Отправка одной записи RawEntry
        if not self.connector_id or not self.access_token:
            print("❌ Невозможно отправить данные: нет ID или токена.")
            return False
        headers = {"Authorization": f"Bearer {self.access_token}"}
        try:
            response = await self.http_client.post(
                f"{self.api_url}/connectors/{self.connector_id}/data", json=entry, headers=headers
            )
            if response.status_code == 200: 
                print(f"📤 Запись {entry.get('entry_id', 'N/A')} успешно отправлена.")
                return True
            else:
                print(f"❌ Ошибка отправки записи {entry.get('entry_id', 'N/A')}: {response.status_code} - {response.text}")
                # Если ошибка связана с состоянием коннектора (например, 403 Forbidden), делаем handshake
                if response.status_code == 403:
                    await self.handshake()
                return False
        except Exception as e:
            print(f"❌ Исключение при отправке записи {entry.get('entry_id', 'N/A')}: {e}")
            return False
            
    async def run(self):
        # Основной цикл работы коннектора
        if not self.connector_id:
            if not await self.register():
                print("Фатальная ошибка: не удалось зарегистрировать коннектор. Выход.")
                await self.http_client.aclose()
                return
        
        print(f"🚀 Запуск основного цикла коннектора {self.connector_type} (ID: {self.connector_id})...")
        self.running = True
        try:
            while self.running and self.stage != "unregistered": 
                # 1. Handshake для синхронизации состояния
                if not await self.handshake():
                    if self.stage == "unregistered": break # Выходим, если токен невалиден
                    print("🔴 Ошибка рукопожатия, повторная попытка через интервал...")
                    # Используем интервал из конфига или дефолтный
                    polling_interval = self.current_config.get("polling_interval", self.polling_interval)
                    await asyncio.sleep(polling_interval)
                    continue

                # 2. Проверка статуса enabled
                if not self.enabled:
                    print(f"💤 Коннектор ID: {self.connector_id} отключен. Ожидание включения...")
                    polling_interval = self.current_config.get("polling_interval", self.polling_interval)
                    await asyncio.sleep(polling_interval)
                    continue
                
                # 3. Обработка этапов
                action_taken = False
                if self.stage == "setup":
                    print("-> Этап SETUP")
                    action_taken = await self.process_setup_steps()
                elif self.stage == "configuration":
                    print("-> Этап CONFIGURATION")
                    action_taken = await self.ensure_configuration()
                elif self.stage == "ready":
                    print("-> Этап READY")
                    if self.config_validation.get("valid"):
                        print("  ✅ Конфигурация валидна. Сбор и отправка данных...")
                        collected_items, group_id = await self.collect_data_from_source()
                        if collected_items:
                            all_sent_successfully = True
                            for i, item in enumerate(collected_items):
                                is_last = (i == len(collected_items) - 1)
                                raw_entry = await self.format_to_raw_entry(item, group_id, is_last)
                                if not await self.send_data_entry(raw_entry):
                                    print("  ⚠️ Ошибка отправки данных, прерывание текущего цикла сбора.")
                                    all_sent_successfully = False
                                    break # Прерываем отправку текущей группы
                            if all_sent_successfully:
                                print(f"🏁 Обработка группы {group_id} завершена успешно.")
                            action_taken = True # Считаем действием попытку сбора/отправки
                        else:
                            print("  Нет новых данных для отправки.")
                            action_taken = True # Считаем действием проверку данных
                    else:
                        print("  ⚠️ Коннектор в этапе READY, но конфигурация невалидна! Ожидание исправления...")
                        # Ничего не делаем, ждем следующего handshake
                        action_taken = True # Считаем действием проверку конфига
                else: 
                    print(f"-> Неизвестный или неподдерживаемый этап: {self.stage}")
                    action_taken = True # Чтобы цикл не завис
                
                # 4. Ожидание перед следующим циклом
                polling_interval = self.current_config.get("polling_interval", self.polling_interval)
                # Если на предыдущем шаге было активное действие (обработка шага, конфига, отправка данных),
                # можно сделать паузу короче или вообще пропустить для быстрой реакции.
                # Но для простоты всегда ждем polling_interval.
                print(f"⏳ Ожидание {polling_interval} секунд...")
                await asyncio.sleep(polling_interval)
                
        except KeyboardInterrupt:
            print("🛑 Прерывание пользователем. Завершение работы...")
            self.running = False
        except Exception as e:
            print(f"💥 Непредвиденная ошибка в основном цикле: {e}")
            self.running = False
        finally:
            await self.http_client.aclose()
            print(f"👋 Коннектор {self.connector_type} (ID: {self.connector_id}) остановлен.")

async def main():
    """Основная функция для тестирования клиента коннектора."""
    parser = argparse.ArgumentParser(description="Клиент коннектора для Mindbank")
    parser.add_argument("--api-url", default=os.environ.get("API_URL", DEFAULT_API_URL), help="URL API")
    parser.add_argument("--integration-key", default=os.environ.get("INTEGRATION_KEY"), help="Интеграционный ключ (можно через env INTEGRATION_KEY)")
    parser.add_argument("--connector-type", default="example-connector", help="Тип коннектора")
    parser.add_argument("--interval", type=int, default=15, help="Polling interval seconds")
                      
    args = parser.parse_args()
    
    if not args.integration_key:
        print("Ошибка: Интеграционный ключ не указан. Используйте --integration-key или переменную окружения INTEGRATION_KEY.")
        sys.exit(1)
        
    # Пример схемы и возможностей для тестового коннектора
    example_schema = {
        "properties": {
            "api_token": {"type": "string", "description": "API Token для внешнего сервиса"},
            "target_folder": {"type": "string", "description": "Целевая папка"},
            "polling_interval": {"type": "integer", "default": args.interval, "description": "Интервал опроса источника"}
        },
        "required": ["api_token"] # Указываем обязательное поле
    }
    example_capabilities = ["file_watch", "status_report"]
    
    # Создаем и запускаем клиент
    client = ConnectorClient(
        api_url=args.api_url,
        integration_key=args.integration_key,
        connector_type=args.connector_type,
        polling_interval=args.interval,
        capabilities=example_capabilities,
        initial_config_schema=example_schema
    )
    
    await client.run() 

# Импортируем random для collect_data_from_source
import random 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Программа завершена.") 