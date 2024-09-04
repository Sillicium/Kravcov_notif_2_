import json
import os
import re
import time
import django
import requests

from reminder.properties.properties import BASE_URL

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.models import Reception
from reminder.header import headers


def clean_phone_number(phone_str):
    phone_numbers = phone_str.split(';')
    first_phone_number = phone_numbers[0].strip()
    cleaned_number = re.sub(r'\D', '', first_phone_number)  # Удалить все нецифровые символы
    return cleaned_number


def save_patient_data(patient, reception_code):
    """Сохраняет данные пациента в Reception."""
    patient_code = patient.get("PROFILE_CODE")
    phones_str = patient.get("PHONES_STR", "").strip()

    if not patient_code or not phones_str:
        print(f"Пропущен пациент с недействительными данными: {patient.get('NAME')} {patient.get('LASTNAME')}")
        return

    phone_number = clean_phone_number(phones_str)

    if not phone_number:
        print(f"Пропущен пациент с некорректным телефоном: {patient.get('NAME')} {patient.get('LASTNAME')}")
        return

    Reception.objects.update_or_create(
        reception_code=int(reception_code),
        defaults={
            'phone_number': phone_number,
            'name': patient.get("NAME"),
            'lastname': patient.get("LASTNAME"),
            'middlename': patient.get("MIDDLENAME"),
        }
    )
    print(f"Сохранен пациент: {patient.get('NAME')} {patient.get('LASTNAME')}")


def save_to_database(data, reception_code):
    try:
        # Если data не является списком, обернем его в список
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            print("Ожидался список или словарь, но получен другой тип данных. Проверьте формат данных.")
            return

        for patient in data:
            if not isinstance(patient, dict):
                print("Пропущен элемент, так как он не является словарем.")
                continue

            # Сохранение данных пациента с использованием reception_code
            save_patient_data(patient, reception_code)

    except ValueError as ve:
        print(f"Ошибка при сохранении пациента: {ve}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


def save_to_json(data, file_name):
    try:
        with open(f'{file_name}.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"Данные успешно сохранены в файл '{file_name}.json'")
    except Exception as e:
        print(f"Ошибка при сохранении в файл JSON: {e}")


def fetch_data(url, reception_code=None, max_retries=5):
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers)
            status = response.status_code

            if status == 200 or status == 201:
                response_json = response.json()
                print("Response JSON:")
                print(response_json)
                print(len(response_json))

                # Передаем reception_code в функцию save_to_database
                save_to_database(response_json, reception_code)

                # Проверяем, пустой ли ответ или меньше ожидаемого
                if len(response_json) == 0:
                    return False
                return True

            elif status == 404:
                print(f"No more patients.")
                return False

            elif status == 502:
                print(f"Error 502: Bad Gateway. Attempt {retry_count + 1} of {max_retries}.")
                retry_count += 1
                time.sleep(5)  # Подождите 5 секунд перед следующей попыткой
                continue

            else:
                print(f"Error: Received status code {status}")
                print(response.text)
                return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return True

    print(f"Max retries reached for URL: {url}")
    return False


def fetch_all_patients():
    all_receptions = Reception.objects.all()

    for reception in all_receptions:
        # Запрашиваем данные о пациенте по patient_code
        url = f"{BASE_URL}/doctor/v1/patient/{reception.patient_code}"
        success = fetch_data(url, reception_code=reception.reception_code)
        if not success:
            print(f"Не удалось обновить данные для reception_code {reception.reception_code}")
        time.sleep(1)

    print("All patient status codes processed. Exiting.")


if __name__ == "__main__":
    fetch_all_patients()
