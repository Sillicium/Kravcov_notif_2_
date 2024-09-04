import redis


def clear_redis_db():
    # Подключение к Redis
    r = redis.Redis(host='localhost', port=6379, db=0)  # Замените на ваш хост, порт и индекс базы данных

    # Очистка базы данных
    r.flushdb()

    print("База данных Redis очищена.")
