import logging

import requests
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.acs_requests.get_contacts_data import get_order_data_for_reception
from reminder.acs_requests.send_contacts import send_order
from reminder.models import Reception

logger = logging.getLogger(__name__)

from django.utils import timezone
from datetime import timedelta


def process_receptions():
    print("Начало выполнения задачи process_receptions")

    # Получаем текущее время в локальной временной зоне (UTC+5)
    now = timezone.localtime(timezone.now()).replace(second=0, microsecond=0)

    # Получаем все приемы, которые еще не были обработаны на сегодня
    receptions = Reception.objects.exclude(processed_for_today=True).filter(start_time__gte=now)

    for reception in receptions:
        # Убедимся, что start_time и upload_time также в локальной временной зоне (UTC+5)
        start_time = timezone.localtime(reception.start_time).replace(second=0, microsecond=0)
        upload_time = timezone.localtime(reception.upload_time).replace(second=0, microsecond=0)

        print(f"Обработка приема {reception.reception_code} для пациента {reception.patient_code}")

        # Логика для звонка за 24 часа до приема или более
        if start_time >= upload_time + timedelta(days=1):
            if start_time.hour <= 11:
                expected_call_time_today = start_time - timedelta(days=1)
                expected_call_time_today = expected_call_time_today.replace(hour=10, minute=50)
            else:
                expected_call_time_today = start_time - timedelta(hours=24)

            reception.calltime_for_today = expected_call_time_today
            reception.calltime_for_tomorrow = start_time - timedelta(hours=2, minutes=10)
            reception.save()
            print(
                f"Прием назначен через 24 часа и более, звонок будет запланирован на сегодня: {expected_call_time_today} и на завтра: {reception.calltime_for_tomorrow}")

        elif start_time.date() == upload_time.date() + timedelta(days=1):
            if upload_time.hour > 16:
                if start_time.hour >= 9 and start_time.hour <= 10:
                    expected_call_time_today = start_time - timedelta(hours=1, minutes=10)
                elif start_time.hour > 10:
                    expected_call_time_today = start_time - timedelta(hours=2, minutes=10)
                else:
                    expected_call_time_today = start_time - timedelta(minutes=70)

                reception.calltime_for_today = expected_call_time_today
                reception.calltime_for_tomorrow = start_time - timedelta(hours=1, minutes=10)
                reception.save()
                print(
                    f"Звонок запланирован на сегодня: {expected_call_time_today} и на завтра: {reception.calltime_for_tomorrow}")

            else:
                expected_call_time = upload_time + timedelta(hours=5)
                reception.calltime_for_tomorrow = expected_call_time
                reception.save()
                print(f"Звонок накануне запланирован на: {expected_call_time}")

        # Проверка и выполнение звонков накануне
        if not reception.processed_for_tomorrow and reception.calltime_for_tomorrow and now >= reception.calltime_for_tomorrow and now < start_time:
            print(f"Звонок накануне для приема {reception.reception_code}")

            order_data, reception_code = get_order_data_for_reception(reception)
            try:
                response = send_order(order_data, reception_code)
                if response:
                    print(f"Звонок для приема {reception.reception_code} инициирован через API")
                    reception.processed_for_tomorrow = True  # Помечаем звонок накануне как обработанный
                    reception.save()
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP ошибка при обработке приема {reception.reception_code}: {http_err}")
            except Exception as err:
                print(f"Произошла непредвиденная ошибка при обработке приема {reception.reception_code}: {err}")

        # Логика звонка в день приема
        if start_time.date() == upload_time.date() and not reception.processed_for_today:
            if reception.calltime_for_today is None:
                if start_time.hour >= 9 and start_time.hour <= 10:

                    expected_call_time_today = start_time - timedelta(hours=1, minutes=10)
                elif start_time.hour > 10:
                    expected_call_time_today = start_time - timedelta(hours=2, minutes=10)
                else:
                    expected_call_time_today = start_time - timedelta(minutes=70)
                reception.calltime_for_today = expected_call_time_today
                reception.save()
                print(f"Звонок в день приема запланирован на: {expected_call_time_today}")

        # Проверка и выполнение звонков в день приема
        if not reception.processed_for_today and reception.calltime_for_today and now >= reception.calltime_for_today and now < start_time:
            print(f"Звонок в день приема для приема {reception.reception_code}")

            order_data, reception_code = get_order_data_for_reception(reception)
            try:
                response = send_order(order_data, reception_code)
                if response:
                    print(f"Звонок для приема {reception.reception_code} инициирован через API")
                    reception.processed_for_today = True  # Помечаем прием как обработанный в день приема
                    reception.save()
            except requests.exceptions.HTTPError as http_err:
                print(f"HTTP ошибка при обработке приема {reception.reception_code}: {http_err}")
            except Exception as err:
                print(f"Произошла непредвиденная ошибка при обработке приема {reception.reception_code}: {err}")

    print("Задача process_receptions завершена")


if __name__ == '__main__':
    process_receptions()
