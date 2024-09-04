import django
import os
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Kravcov_notif.settings')
django.setup()

from reminder.models import Reception


def clear_models():
    """
    Функция для удаления записей из модели Reception, где start_time уже прошел более чем на 24 часа.
    """
    # Получаем текущее время
    now = timezone.now()

    # Определяем время 24 часа назад
    cutoff_time = now - timedelta(hours=24)

    # Удаляем записи, где start_time прошел более чем на 24 часа назад
    deleted_count, _ = Reception.objects.filter(start_time__lte=cutoff_time).delete()

    print(f"Удалено {deleted_count} записей из модели Reception.")


if __name__ == "__main__":
    clear_models()
