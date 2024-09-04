import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.properties.properties import ACS_BASE_URL
from reminder.properties.utils import get_latest_api_key
from reminder.models import Reception


def send_order(order_data, reception_code):
    api_key = get_latest_api_key()
    if api_key:
        url = f"{ACS_BASE_URL}/api/v2/bpm/public/bp/{api_key}/add_orders"
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.post(url, json=order_data, headers=headers)

        if response.status_code == 200:
            try:
                data = response.json().get('data', {})
                if isinstance(data, dict) and data:
                    for phone_number, item in data.items():
                        try:
                            order_key = item.get('order', '')
                            if order_key:
                                reception = Reception.objects.filter(reception_code=reception_code).first()

                                if reception:
                                    if not reception.first_order_key:
                                        reception.first_order_key = order_key
                                    elif not reception.second_order_key:
                                        reception.second_order_key = order_key
                                    else:
                                        print(f"Both order keys are already filled for reception code: {reception_code}")

                                    reception.save()
                                    reception.refresh_from_db()
                                    print(f"After save: first_order_key = {reception.first_order_key}, second_order_key = {reception.second_order_key}")
                                else:
                                    print(f"Reception with code {reception_code} not found.")
                        except Exception as e:
                            print(f"Error updating order: {e}")
            except ValueError as ve:
                print(f"Error decoding JSON: {ve}")
        else:
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP error occurred: {http_err}")
    else:
        print("Failed to retrieve or decode API key.")
    return None
