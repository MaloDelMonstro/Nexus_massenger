"""
from plugins import BasePlugin, PluginContext, PluginResponse


class BotApiCodePlugin(BasePlugin):
    name = "botapicode"
    description = "Показывает пример кода для API бота"
    version = "1.0.0"

    commands = {
        'botapicode': 'Пример кода API: /botapicode'
    }

    def execute(self, command: str, args: list[str], ctx: PluginContext) -> PluginResponse:
        python_code = ""import requests
import sys

BASE_URL = "ваш URL"

BOT_ID = BOT_ID
API_KEY = "YOUR_API_KEY"


def send_bot_message(text: str) -> bool:
    global response
    url = f"{BASE_URL}/bots/{BOT_ID}/send"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
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
        print(f"Не удалось подключиться к серверу {BASE_URL}")
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
    send_bot_message(message)""

        message = (
            "Примеры использования API бота:\n\n"
            "Python (requests):\n"
            f"{python_code}\n"
            "\n\n"
            "Важно: Замени BOT_ID, YOUR_API_KEY и домен на свои данные!"
        )

        return PluginResponse.ok(message)

"""