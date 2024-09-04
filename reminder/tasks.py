import logging

from celery import shared_task, chain

from reminder.acs_requests.fetch_audio_data import get_audio_data
from reminder.acs_requests.fetch_status_data import get_status_data
from reminder.requests.patient_get_data import fetch_all_patients
from reminder.requests.reception_search import search_reception
from reminder.telegram.send_patient_info import send_message_from_tg_bot
from reminder.utils.clear_models import clear_models
from reminder.utils.clear_redis import clear_redis_db
from reminder.utils.process_receptions import process_receptions

# команды для запуска ->
# celery -A Kravcov_notif worker -l info -P gevent
# celery -A Kravcov_notif beat --loglevel=info
# celery -A Kravcov_notif flower --port=5555

logger = logging.getLogger(__name__)


@shared_task
def fetch_reception_information():
    logger.debug("Начало выполнения задачи fetch_reception_information")
    try:
        result = search_reception()
        logger.debug(f"Результат выполнения: {result}")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    logger.debug("Задача fetch_reception_information завершена")


@shared_task
def clear_models_data():
    logger.debug("Начало выполнения задачи clear_models_data")
    try:
        result = clear_models()
        logger.debug(f"Результат выполнения: {result}")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    logger.debug("Задача clear_models_data завершена")


@shared_task
def clear_redis_data():
    logger.debug("Начало выполнения задачи clear_redis_data")
    try:
        result = clear_redis_db()
        logger.debug(f"Результат выполнения: {result}")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    logger.debug("Задача clear_redis_data завершена")


@shared_task
def fetch_patient_information(*args, **kwargs):
    logger.debug("Начало выполнения задачи fetch_patient_information")
    try:
        result = fetch_all_patients()
        logger.debug(f"Результат выполнения: {result}")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    logger.debug("Задача fetch_patient_information завершена")


@shared_task
def fetch_reception_call(*args, **kwargs):
    logger.debug("Начало выполнения задачи fetch_reception_call")
    try:
        process_receptions()
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
    logger.debug("Задача fetch_reception_call завершена")


@shared_task
def fetch_status_updates(*args, **kwargs):
    try:
        logger.info("Fetching status updates...")
        status_data_list, error = get_status_data()
        if error:
            logger.error(f"Error fetching contact status data: {error}")
            raise Exception(error)
        logger.info("Successfully fetched contact status data.")
        return status_data_list
    except Exception as e:
        logger.error(f"Error fetching contact status data: {e}")
        raise


@shared_task
def get_contact_audio_data(*args, **kwargs):
    try:
        logger.info("Fetching contact audio data...")
        audio_data_list, error = get_audio_data()
        if error:
            logger.error(f"Error fetching contact audio data: {error}")
            raise Exception(error)
        logger.info("Successfully fetched contact audio data.")
        return audio_data_list
    except Exception as e:
        logger.error(f"Error fetching contact audio data: {e}")
        raise


@shared_task
def add_patient_info_for_tg_bot(*args, **kwargs):
    try:
        logger.info("Adding patient info for TG bot...")
        result = send_message_from_tg_bot()
        logger.info("Successfully added patient info for TG bot.")
        return result
    except Exception as e:
        logger.error(f"Error adding patient info for TG bot: {e}")
        raise


@shared_task
def telegram_bot_task_chain(*args, **kwargs):
    try:
        logger.info("Starting task chain execution...")

        first_step = fetch_status_updates.s()
        second_step = get_contact_audio_data.s()
        third_step = add_patient_info_for_tg_bot.s()

        task_chain = chain(first_step, second_step, third_step)

        result = task_chain.apply_async()

        logger.info("Task chain execution started.")

        chain_result = result.get()
        logger.info("Task chain executed successfully.")
        return chain_result

    except Exception as e:
        logger.error(f"Error executing task chain: {e}")
        raise


@shared_task
def patient_data_chain(*args, **kwargs):
    try:
        logger.info("Starting task chain execution...")

        first_step = fetch_reception_information.s()
        second_step = fetch_patient_information.s()

        task_chain = chain(first_step, second_step)

        result = task_chain.apply_async()

        logger.info("Task chain execution started.")

        chain_result = result.get()
        logger.info("Task chain executed successfully.")
        return chain_result

    except Exception as e:
        logger.error(f"Error executing task chain: {e}")
        raise
