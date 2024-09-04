import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv('MEDELEMENT_BASE_URL')
ACS_BASE_URL = os.getenv('ACS_BASE_URL')

statuses = {
    2394: {'description': 'Пациент опаздывает', 'topic_id': '6'},
    2356: {'description': 'Пациент сомневается, что записывался на прием', 'topic_id': '6'},
    2357: {'description': 'Пациент не придет - выбрал другую клинику', 'topic_id': '6'},
    2359: {'description': 'Перезапись - не придет по причине болезни', 'topic_id': '6'},
    616: {'description': 'Недозвон', 'topic_id': '2'},
    2119: {'description': 'Перезапись', 'topic_id': '6'},
    2458: {'description': 'Пациент просит удалить его из базы', 'topic_id': '6'},
    2371: {'description': 'Подтвержденная запись', 'topic_id': '4'},
    2105: {'description': 'Пациент уведомлен о записи', 'topic_id': '4'},
    2106: {'description': 'Пациент уведомлен о записи', 'topic_id': '4'},
    2109: {'description': 'Пациент уведомлен о записи', 'topic_id': '4'},
    2117: {'description': 'Робот не понял пациента', 'topic_id': '6'}
}
