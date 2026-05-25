import requests

BASE = 'http://localhost:8000'


def check(path):
    response = requests.get(f'{BASE}{path}')
    print(path, response.status_code)


if __name__ == '__main__':
    check('/health')
