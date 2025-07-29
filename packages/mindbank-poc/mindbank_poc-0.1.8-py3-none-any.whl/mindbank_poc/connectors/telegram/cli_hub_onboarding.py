import json
import time
import requests
import os
import traceback

STATE_FILE = os.path.join(os.path.dirname(__file__), "connector_state.json")
API_URL = "http://localhost:8000"
POLL_INTERVAL = 2

def wait_for_connector_registration(state_file=STATE_FILE, poll_interval=POLL_INTERVAL):
    while True:
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
            access_token = state.get("access_token")
            connector_id = state.get("connector_id")
            if access_token and connector_id:
                print("Коннектор зарегистрирован!")
                return access_token, connector_id
        except Exception:
            traceback.print_exc()
            pass
        print("Ожидание регистрации коннектора...")
        time.sleep(poll_interval)


def init_onboarding():
    access_token, connector_id = wait_for_connector_registration()
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        requests.post(f"{API_URL}/api/onboard/{connector_id}/initiate", headers=headers)
    except Exception as e:
        print(f"Ошибка при инициации онбординга: {e}")
        return
    return access_token, connector_id

def cli_onboarding():
    access_token, connector_id = init_onboarding()
    headers = {"Authorization": f"Bearer {access_token}"}
    last_step_id = None
    while True:
        try:
            resp = requests.get(f"{API_URL}/api/onboard/{connector_id}/status", headers=headers)
            if resp.status_code == 404:
                print(resp.text)
                print("Онбординг ещё не инициирован. Ждём...")
                time.sleep(POLL_INTERVAL)
                continue
            status = resp.json()
            # if last_step_id == status.get("step_id"):
            #     continue
            last_step_id = status.get("step_id")
            if last_step_id == "AWAITING_ONBOARD_START":
                init_onboarding()
                time.sleep(2)
                continue
            print(f"\nТекущий шаг: {status.get('description')}")
            for msg in status.get("messages", []):
                print(msg)
            if status.get("is_final_step"):
                print("Онбординг завершён!")
                break
            input_schema = status.get("input_schema")
            if input_schema:
                data = {}
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])
                for field, field_info in properties.items():
                    prompt = field_info.get("description") or field
                    value = input(f"Введите {prompt}: ")
                    if value == "" and field in required:
                        print(f"Поле {field} обязательно для заполнения!")
                        value = input(f"Введите {prompt}: ")
                    data[field] = value
                payload = {"step_id": status["step_id"], "data": data}
                print(payload)
                resp2 = requests.post(
                    f"{API_URL}/api/onboard/{connector_id}/submit_step",
                    json=payload,
                    headers=headers
                )
                if resp2.status_code != 200:
                    print(f"Ошибка отправки шага: {resp2.text}")
            else:
                print("Ожидание следующего шага...")
                time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\nПрервано пользователем.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    cli_onboarding() 