import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.acs_requests.fetch_audio_data import get_keys_batch
from reminder.models import Reception
from reminder.properties.properties import ACS_BASE_URL
from reminder.properties.utils import get_latest_api_key


def fetch_status_data(keys_str):
    if not keys_str:
        return None, 'No keys found in the database.'

    api_key = get_latest_api_key()
    if api_key:
        url = f'{ACS_BASE_URL}/api/v2/orders/public/{api_key}/get_status?keys={keys_str}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json(), None
        except requests.exceptions.RequestException as e:
            return None, str(e)


def process_status_data(status_data_list):
    if isinstance(status_data_list, dict):
        for order_key, details in status_data_list.items():
            if isinstance(details, dict):
                for status_group, status_info in details.items():
                    if isinstance(status_info, dict) and 'status_id' in status_info:
                        status_id = status_info['status_id']
                        reception = Reception.objects.filter(
                            first_order_key=order_key
                        ).first() or Reception.objects.filter(
                            second_order_key=order_key
                        ).first()

                        if reception:
                            if reception.first_order_key == order_key:
                                reception.first_status_id = status_id
                                print(f"Updated first status for order_key: {order_key} to status_id: {status_id}")
                            elif reception.second_order_key == order_key:
                                reception.second_status_id = status_id
                                print(f"Updated second status for order_key: {order_key} to status_id: {status_id}")
                            reception.save()
                        else:
                            print(f"Reception with order_key {order_key} not found.")
            else:
                print(f"Unexpected format for details: {details}")
    elif isinstance(status_data_list, list):
        for item in status_data_list:
            if isinstance(item, dict) and 'order' in item and 'status_id' in item:
                order_key = item['order']
                status_id = item['status_id']
                reception = Reception.objects.filter(
                    first_order_key=order_key
                ).first() or Reception.objects.filter(
                    second_order_key=order_key
                ).first()

                if reception:
                    if reception.first_order_key == order_key:
                        reception.first_status_id = status_id
                        print(f"Updated first status for order_key: {order_key} to status_id: {status_id}")
                    elif reception.second_order_key == order_key:
                        reception.second_status_id = status_id
                        print(f"Updated second status for order_key: {order_key} to status_id: {status_id}")
                    reception.save()
                else:
                    print(f"Reception with order_key {order_key} not found.")
            else:
                print(f"Unexpected format for item: {item}")
    else:
        raise ValueError("Unexpected format for status_data_list")


def get_status_data():
    offset = 0
    all_status_data = []

    while True:
        keys_array = get_keys_batch(batch_size=10, offset=offset)
        if not keys_array:
            break

        keys_str = ','.join(keys_array)
        if not keys_str:
            break

        status_data_list, error = fetch_status_data(keys_str)
        if error:
            return [], error

        # Ensure status_data_list is in an expected format before processing
        if status_data_list:
            print(f"Fetched status data: {status_data_list}")
            process_status_data(status_data_list)
            if isinstance(status_data_list, list):
                all_status_data.extend(status_data_list)
            elif isinstance(status_data_list, dict):
                all_status_data.append(status_data_list)
            else:
                return [], "Invalid data format received"
        else:
            return [], "Invalid data format received"

        offset += 10

    return all_status_data, None


if __name__ == '__main__':
    get_status_data()
