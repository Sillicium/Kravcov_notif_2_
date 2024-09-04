import os
import time
from datetime import datetime, timedelta
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.models import Reception
from reminder.properties.properties import BASE_URL
from reminder.properties.utils import send_post_request
from reminder.acs_requests.trash_orders import trash_orders

url = BASE_URL + "/v2/doctor/reception/search"


def search_reception():
    skip = 0

    while True:
        today = datetime.today()
        tomorrow = today + timedelta(days=2)

        date_time_data = {
            'begin_datetime': f"{today.strftime('%d.%m.%Y')}",
            'end_datetime': f"{tomorrow.strftime('%d.%m.%Y')}",
            'skip': skip,
        }

        response = send_post_request(url, date_time_data)

        print(f"Status code: {response.status_code}")
        print("Response text:")
        print(response.text)

        if response.status_code in [200, 201]:
            response_json = response.json()
            save_to_db_saved_patients_from_receptions_search(response_json)

            if len(response_json) == 0:
                print("No more data to process.")
                break

            skip += 50

        elif response.status_code == 404:
            print(f"No more data available. Server returned 404 for params {date_time_data}.")
            break

        elif response.status_code == 502:
            print(f"Error 502: Bad Gateway. Retrying...")
            time.sleep(5)
            continue

        else:
            print(f"Error: Received status code {response.status_code}")
            break

        time.sleep(1)

    print("All data processed. Exiting.")


def save_to_db_saved_patients_from_receptions_search(data):
    try:
        if not data or not isinstance(data, dict):
            print("Получены пустые данные или данные не в формате словаря.")
            return

        now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)

        for patient_data in data.get("receptions", []):
            patient_code = patient_data.get("PATIENT_CODE")
            reception_code = patient_data.get("RECEPTION_CODE")

            start_time_str = patient_data.get("STARTTIME")
            if not start_time_str:
                print(f"Пропущен прием, так как не указано STARTTIME: {patient_data}")
                continue

            start_time = timezone.make_aware(datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S"))

            # Проверка времени
            if not (9 <= start_time.hour < 17):
                print(f"Пропущен прием для patient_code {patient_code} из-за времени: {start_time}")
                continue

            removed = patient_data.get("REMOVED")
            notify = patient_data.get("NOTIFY")

            if not patient_code or not reception_code:
                print(f"Пропущен прием с недействительным patient_code или reception_code: {patient_data}")
                continue

            existing_reception = Reception.objects.filter(
                patient_code=int(patient_code),
                start_time__date=start_time.date()
            ).order_by('start_time').first()

            if existing_reception:
                print(f"Пропущен прием для patient_code {patient_code}, так как уже существует запись на этот день.")
                continue

            if notify in (1, None) and removed == 0:
                reception, created = Reception.objects.get_or_create(
                    reception_code=int(reception_code),
                    defaults={
                        'patient_code': int(patient_code),
                        'start_time': start_time,
                        'upload_time': now
                    }
                )

                if not created:
                    reception.start_time = start_time
                    reception.save()

            elif notify == 0 or removed == 1:
                try:
                    reception = Reception.objects.get(
                        reception_code=int(reception_code),
                    )

                    # Проверяем и удаляем ордеры, начиная со второго
                    if reception.second_order_key:
                        print(f"Удаление второго ордера: {reception.second_order_key}")
                        trash_orders(reception.second_order_key)
                    elif reception.first_order_key:
                        print(f"Удаление первого ордера: {reception.first_order_key}")
                        trash_orders(reception.first_order_key)
                    reception.delete()
                    print(f"Запись с patient_code {patient_code} и reception_code {reception_code} удалена.")
                except Reception.DoesNotExist:
                    print(f"Запись с patient_code {patient_code} и reception_code {reception_code} не найдена для удаления.")

    except ValueError as ve:
        print(f"Ошибка при сохранении записи: {ve}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    search_reception()
