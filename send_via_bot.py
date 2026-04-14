import requests
import sys

from admin_utils._const import API_KEY1, BASE_URL1, BOT_ID1

BASE_URL = BASE_URL1

BOT_ID = BOT_ID1
API_KEY = API_KEY1


def send_bot_message(text: str) -> bool:
    global response
    url = f"{BASE_URL1}/bots/{BOT_ID}/send"

    headers = {
        "Authorization": f"Bearer {API_KEY1}",
        "Content-Type": "application/json"
    }

    payload = {"message": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        response.raise_for_status()

        data = response.json()

        if data.get("success"):
            print(f"Успешно отправлено! ID сообщения: {data.get('message_id')}")
            return True
        else:
            print(f"Сервер вернул ответ без success: {data}")
            return False

    except requests.exceptions.HTTPError:
        print(f"Ошибка HTTP {response.status_code}:")
        try:
            print(f"Детали: {response.json().get('error', 'Нет описания')}")
        except Exception:
            print(f"Детали: {response.text}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"Не удалось подключиться к серверу {BASE_URL1}")
        print("Проверь, запущен ли сервер и правильный ли порт.")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input(f"Ваше сообщение:\n")

    print(f"Отправляю: \"{message}\"")
    send_bot_message(message)