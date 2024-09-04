from datetime import datetime

import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.models import Reception
from reminder.properties.properties import ACS_BASE_URL

from reminder.properties.utils import get_latest_api_key


def fetch_audio_data(keys_str):
    if not keys_str:
        return None, 'No keys found in the database.'

    api_key = get_latest_api_key()
    if api_key:

        url = f'{ACS_BASE_URL}/api/v2/orders/public/{api_key}/get_calls?keys={keys_str}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)


def process_audio_data(audio_data_list):
    if not audio_data_list:
        print("Список аудиоданных пуст.")
        return

    for audio_data in audio_data_list:
        order_key = audio_data.get('order_key')
        audio_link = audio_data.get('link')

        if order_key and audio_link:
            # Найдем прием по ключу ордера
            reception = Reception.objects.filter(
                first_order_key=order_key
            ).first() or Reception.objects.filter(
                second_order_key=order_key
            ).first()

            if reception:
                # Обновляем соответствующее поле для аудио
                if reception.first_order_key == order_key:
                    reception.first_audio_link = audio_link
                    print(f"Обновлен аудиоссылка для первого ордера с ключом: {order_key}")
                elif reception.second_order_key == order_key:
                    reception.second_audio_link = audio_link
                    print(f"Обновлен аудиоссылка для второго ордера с ключом: {order_key}")

                reception.save()
            else:
                print(f"Прием с ключом ордера {order_key} не найден.")


def get_audio_data():
    offset = 0
    all_audio_data = []

    while True:
        keys_array = get_keys_batch(batch_size=10, offset=offset)
        if not keys_array:
            break

        keys_str = ','.join(keys_array)
        if not keys_str:
            break

        audio_data_list, error = fetch_audio_data(keys_str)
        if error:
            return [], error

        process_audio_data(audio_data_list)
        all_audio_data.extend(audio_data_list)

        offset += 10

    return all_audio_data, None


"""Below code to get key to last 10 contacts"""


def get_keys_batch(batch_size=10, offset=0):
    keys = Reception.objects.order_by('-id')[offset:offset + batch_size].values_list('order_key', flat=True)
    return list(keys)


if __name__ == '__main__':
    get_audio_data()
