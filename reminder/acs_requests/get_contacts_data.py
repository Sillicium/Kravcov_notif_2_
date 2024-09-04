from datetime import timedelta, datetime
import pytz
from reminder.models import Reception


def get_order_data_for_reception(reception):
    order_list = []

    # Формируем полное имя пациента
    full_name = f"{reception.name} {reception.lastname}"

    # Преобразование времени приема в UTC+5
    tz_utc_plus_5 = pytz.timezone('Asia/Yekaterinburg')
    reception_start_time = reception.start_time.astimezone(tz_utc_plus_5)

    reception_date = reception_start_time.date()
    reception_time = reception_start_time.strftime("%H%M")

    # Определение значения time_value на основе даты приема
    if reception_date == datetime.today().astimezone(tz_utc_plus_5).date():
        time_value = f"s{reception_time}"
    elif reception_date == (datetime.today().astimezone(tz_utc_plus_5) + timedelta(days=1)).date():
        time_value = f"z{reception_time}"
    else:
        # Если префикс не подходит, пропускаем этот прием
        return []

    # Формирование данных для заказа
    order_list.append({
        "phone": reception.phone_number,
        "full_name": full_name,
        "info": {
            "time": time_value,
        }
    })

    return order_list, reception.reception_code
