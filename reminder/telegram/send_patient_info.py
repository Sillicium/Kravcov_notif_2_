from io import BytesIO
import pytz
import requests
import os
import django
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.properties.properties import statuses
from reminder.models import Reception


load_dotenv()

CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
TOKEN = os.getenv('TELEGRAM_API_TOKEN')


def split_message(message, max_length=4096):
    parts = []
    while len(message) > max_length:
        split_index = message.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = max_length
        parts.append(message[:split_index])
        message = message[split_index:]
    parts.append(message)
    return parts


def download_audio(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.RequestException as e:
        print(f"Ошибка при загрузке аудиофайла: {e}")
        return None


def send_audio_with_caption(chat_id, file, file_name, phone_number, caption, topic_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
    files = {'audio': (f"{file_name}_{phone_number}", file, 'audio/mpeg')}
    data = {
        'chat_id': chat_id,
        'caption': caption,
        "message_thread_id": topic_id,
        'parse_mode': 'Markdown',
    }
    try:
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при отправке аудиофайла в Telegram: {e}")
        return {"ok": False}


def send_message_from_tg_bot():
    responses = Reception.objects.filter(is_added=False)
    tz_utc_plus_5 = pytz.timezone('Asia/Yekaterinburg')

    for response in responses:
        status_id = int(response.status_id)

        if status_id in [2122, 2101]:
            print(f"Статус {status_id} пропущен.")
            continue

        status_info = statuses.get(status_id, {'description': 'Неизвестный статус', 'topic_id': '6'})

        reception_start_time = response.start_time.astimezone(tz_utc_plus_5)

        appointment_date = reception_start_time.strftime("%d/%m/%Y")
        appointment_time = reception_start_time.strftime("%H:%M")

        caption = (
            f"*{status_info['description']}*\n\n"
            f"*ФИО:* {response.name} {response.lastname}\n"
            f"*Телефон:* {response.phone_number}\n"
            f"*Дата приема:* {appointment_date}\n"
            f"*Время приема:* {appointment_time}\n"
        )

        audio_link = response.audio_link
        audio_file = download_audio(audio_link)
        if audio_file:
            result = send_audio_with_caption(CHAT_ID, audio_file, response.name, response.phone_number, caption, status_info['topic_id'])
            print(result)

            if result.get("ok"):
                response.is_added = True
                response.save()
            else:
                print(f"Не удалось отправить сообщение для пациента {response.name}")
        else:
            print(f"Не удалось отправить аудиофайл для пациента {response.name}")


if __name__ == '__main__':
    send_message_from_tg_bot()
