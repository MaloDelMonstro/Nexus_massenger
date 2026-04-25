import requests


class NexusPluginClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json'
        })

    def execute(self, command: str, args: list = None) -> dict:
        url = f"{self.api_url}/api/v1/plugins/execute"
        payload = {
            'command': command,
            'args': args or []
        }

        response = self.session.post(url, json=payload)
        return response.json()

    def list_plugins(self) -> dict:
        url = f"{self.api_url}/api/v1/plugins/list"
        response = self.session.get(url)
        return response.json()

    def get_help(self, plugin_name: str) -> dict:
        url = f"{self.api_url}/api/v1/plugins/help"
        params = {'plugin': plugin_name}
        response = self.session.get(url, params=params)
        return response.json()

    def get_me(self) -> dict:
        url = f"{self.api_url}/api/v1/me"
        response = self.session.get(url)
        return response.json()


if __name__ == '__main__':
    API_URL = 'http://localhost:8080'
    API_KEY = 'API_KEY'

    client = NexusPluginClient(API_URL, API_KEY)

    print("Информация о пользователе:")
    me = client.get_me()
    if me.get('success'):
        user = me['user']
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Admin: {user['is_admin']}")
    else:
        print(f"Ошибка: {me.get('error')}")

    print("Доступные плагины:")
    plugins = client.list_plugins()
    if plugins.get('success'):
        print(f"Всего: {plugins['count']}")
        for p in plugins['plugins']:
            print(f"{p['name']} v{p['version']} — {p['description']}")
    else:
        print(f"Ошибка: {plugins.get('error')}")

    command = input('Введите команду (без слеша и лишних знаков): ')
    args = input('Введите аргументы через пробел: ')

    result = client.execute(f'{command}', [args.split(' ')])
    if result.get('success'):
        print(f"{result['message']}")
    else:
        print(f"{result.get('error')}")
