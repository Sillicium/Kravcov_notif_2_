import requests

from reminder.header import headers
from reminder.properties.utils import get_latest_api_key


def trash_orders(order):
    api_key = get_latest_api_key()
    if api_key:
        url = f"https://api.example.com/api/v2/orders/public/{api_key}/trash_order"

        payload = {
            'keys': [order]
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            print("Response data:", data)

            return data

        except requests.exceptions.RequestException as e:
            print(f"Произошла ошибка при выполнении запроса: {e}")
            return None
