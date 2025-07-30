import logging
import json
import redis.asyncio as redis  # Современный асинхронный клиент Redis
import threading  # Для синхронизации кеша

logger = logging.getLogger("redstream.redis_config")


class RedisConfig:
    """Класс для работы с конфигурациями в Redis с поддержкой защиты от записи, кешированием и сериализацией данных."""

    READ_ONLY_KEY = "config_readonly"  # Специальный ключ для хранения статуса read-only

    def __init__(self, redis_client, config_name):
        self.redis = redis_client
        self.config_name = config_name
        self.lock = threading.Lock()  # Мьютекс для кеша
        self.config_cache = {}  # Кеш конфигурации

    async def is_read_only(self):
        """Проверяет, является ли конфигурация 'только для чтения'."""
        read_only = await self.redis.get(f"{self.config_name}:{self.READ_ONLY_KEY}")
        return read_only == "1"

    async def set_read_only(self, state: bool):
        """Устанавливает флаг 'только для чтения'."""
        await self.redis.set(f"{self.config_name}:{self.READ_ONLY_KEY}", "1" if state else "0")
        logger.info(f"🔒 [Redis] Конфигурация {self.config_name} теперь {'только для чтения' if state else 'изменяемая'}.")

    async def get(self, key, default=None):
        """Получает параметр из конфигурации, автоматически десериализуя данные."""
        try:
            # Проверяем кеш
            with self.lock:
                if key in self.config_cache:
                    logger.info(f"🔍 [Redis] {self.config_name}[{key}] (из кеша) -> {self.config_cache[key]}")
                    return self.config_cache[key]
            
            value = await self.redis.hget(self.config_name, key)
            if value is not None:
                value = json.loads(value)  # Десериализация JSON

            # Обновляем кеш
            with self.lock:
                if value is not None:
                    self.config_cache[key] = value

            logger.info(f"🔍 [Redis] {self.config_name}[{key}] -> {value}")
            return value if value is not None else default
        except Exception as e:
            logger.error(f"❌ Ошибка получения {key} из {self.config_name}: {e}")
            return default

    async def get_all(self):
        """Возвращает всю конфигурацию, автоматически десериализуя все данные."""
        try:
            # Проверяем кеш
            with self.lock:
                if self.config_cache:
                    logger.info(f"🔍 [Redis] Загружена конфигурация {self.config_name} (из кеша)")
                    return self.config_cache

            config = await self.redis.hgetall(self.config_name)
            deserialized_config = {k: json.loads(v) for k, v in config.items()}

            # Обновляем кеш
            with self.lock:
                self.config_cache = deserialized_config

            logger.info(f"🔍 [Redis] Загружена конфигурация {self.config_name} -> {deserialized_config}")
            return deserialized_config
        except Exception as e:
            logger.error(f"❌ Ошибка получения конфигурации {self.config_name}: {e}")
            return {}

    async def set(self, key, value):
        """Устанавливает параметр в конфигурации, если она не read-only."""
        if await self.is_read_only():
            logger.warning(f"⚠️ Попытка записи {key} в защищенную конфигурацию {self.config_name}. Запрос отклонен.")
            return False
        try:
            serialized_value = json.dumps(value)  # Сериализация JSON
            await self.redis.hset(self.config_name, key, serialized_value)

            # Обновляем кеш
            with self.lock:
                self.config_cache[key] = value  

            logger.info(f"✅ [Redis] {self.config_name}[{key}] = {value} (кеш обновлен)")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка установки {key} в {self.config_name}: {e}")
            return False

    async def set_many(self, data: dict):
        """Устанавливает сразу несколько параметров, если конфигурация не read-only."""
        if await self.is_read_only():
            logger.warning(f"⚠️ Попытка массовой записи в защищенную конфигурацию {self.config_name}. Запрос отклонен.")
            return False
        try:
            serialized_data = {k: json.dumps(v) for k, v in data.items()}  # Сериализация всех данных
            await self.redis.hset(self.config_name, mapping=serialized_data)

            # Обновляем кеш
            with self.lock:
                self.config_cache.update(data)

            logger.info(f"✅ [Redis] Обновлены параметры {self.config_name} -> {data} (кеш обновлен)")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка массовой установки в {self.config_name}: {e}")
            return False

    async def delete(self, key):
        """Удаляет параметр (если конфигурация не read-only)."""
        if await self.is_read_only():
            logger.warning(f"⚠️ Попытка удаления {key} в защищенной конфигурации {self.config_name}. Запрос отклонен.")
            return False
        try:
            await self.redis.hdel(self.config_name, key)

            # Очищаем кеш
            with self.lock:
                if key in self.config_cache:
                    del self.config_cache[key]

            logger.info(f"🗑️ [Redis] Удален {key} из {self.config_name} (кеш очищен)")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка удаления {key} в {self.config_name}: {e}")
            return False

    def refresh_cache(self):
        """Принудительно обновляет кеш конфигурации."""
        try:
            with self.lock:
                config = self.redis.hgetall(self.config_name)
                self.config_cache = {k: json.loads(v) for k, v in config.items()}

            logger.info(f"🔄 [Redis] Кеш конфигурации {self.config_name} обновлен")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления кеша для {self.config_name}: {e}")

    def clear_cache(self):
        """Очищает кеш конфигурации."""
        with self.lock:
            self.config_cache.clear()
        logger.info(f"🗑️ [Redis] Кеш конфигурации {self.config_name} очищен")


class RedisConfigManager:
    """Менеджер конфигураций в Redis с поддержкой read-only и публикации конфигураций мастер-сервисом."""

    def __init__(self, redis_url="redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def get_config(self, config_name):
        """Получает объект конфигурации."""
        return RedisConfig(self.redis, config_name)

    async def get(self, config_name, key, default=None):
        """Получает параметр из указанной конфигурации."""
        return await self.get_config(config_name).get(key, default)

    async def set(self, config_name, key, value):
        """Устанавливает параметр в указанной конфигурации, если она не read-only."""
        return await self.get_config(config_name).set(key, value)

    async def set_many(self, config_name, data: dict):
        """Устанавливает несколько параметров в указанной конфигурации, если она не read-only."""
        return await self.get_config(config_name).set_many(data)

    async def delete(self, config_name, key):
        """Удаляет параметр из указанной конфигурации, если она не read-only."""
        return await self.get_config(config_name).delete(key)

    async def get_all(self, config_name):
        """Получает всю конфигурацию."""
        return await self.get_config(config_name).get_all()

    async def set_read_only(self, config_name, state: bool):
        """Устанавливает режим read-only для конфигурации."""
        return await self.get_config(config_name).set_read_only(state)

    async def is_read_only(self, config_name):
        """Проверяет, является ли конфигурация read-only."""
        return await self.get_config(config_name).is_read_only()

    async def publish_config(self, config_name, data: dict, read_only: bool = False):
        """
        Публикует конфигурацию в Redis (только мастер-сервис).
        Устанавливает статус read-only при необходимости.
        """
        await self.get_config(config_name).set_many(data)
        if read_only:
            await self.set_read_only(config_name, True)
        logger.info(f"📤 [Redis] Конфигурация {config_name} опубликована. Read-only: {read_only}")


# Глобальный экземпляр
redis_config = RedisConfigManager()
