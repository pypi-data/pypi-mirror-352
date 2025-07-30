import asyncio
import redis.asyncio as redis
import logging
import traceback
from typing import Optional

from .utils.logging_helpers import LoggerWithCaller

logger = LoggerWithCaller("redstream.redis_cache")


class RedisCache:
    """
    RedisCache — простой клиент для кэширования данных в Redis.

    Поддерживает:
    - запись и чтение значений по ключу
    - TTL (время жизни)
    - префиксы (namespace)
    - атомарную установку (set if not exists)
    """

    def __init__(self, redis_url: str, prefix: str = "", default_ttl: int = 300):
        self.redis_url = redis_url
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.redis_conn: Optional[redis.Redis] = None

    async def connect(self):
        """Устанавливает соединение с Redis"""
        self.redis_conn = redis.from_url(self.redis_url, decode_responses=True)
        logger.info(f"🔌 Подключение к Redis установлено: {self.redis_url}")

    def make_key(self, key: str) -> str:
        """Добавляет префикс к ключу"""
        return f"{self.prefix}{key}"

    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Сохраняет значение с TTL"""
        if not self.redis_conn:
            logger.error("❌ RedisCache: соединение не установлено!")
            return

        try:
            full_key = self.make_key(key)
            await self.redis_conn.set(full_key, value, ex=ttl or self.default_ttl)
            logger.debug(f"📝 Установлен кеш: {full_key} (TTL={ttl or self.default_ttl})")
        except Exception as e:
            logger.error(f"❌ Ошибка установки ключа: {e}")
            logger.debug(traceback.format_exc())

    async def get(self, key: str) -> Optional[str]:
        """Получает значение по ключу"""
        if not self.redis_conn:
            logger.error("❌ RedisCache: соединение не установлено!")
            return None

        try:
            full_key = self.make_key(key)
            value = await self.redis_conn.get(full_key)
            logger.debug(f"📥 Получено из кеша: {full_key} → {value}")
            return value
        except Exception as e:
            logger.error(f"❌ Ошибка получения ключа: {e}")
            logger.debug(traceback.format_exc())
            return None

    async def exists(self, key: str) -> bool:
        """Проверяет наличие ключа"""
        if not self.redis_conn:
            return False
        return await self.redis_conn.exists(self.make_key(key)) == 1

    async def delete(self, key: str):
        """Удаляет ключ из Redis"""
        if not self.redis_conn:
            return
        try:
            await self.redis_conn.delete(self.make_key(key))
            logger.debug(f"❌ Ключ удалён: {self.make_key(key)}")
        except Exception as e:
            logger.error(f"❌ Ошибка удаления ключа: {e}")
            logger.debug(traceback.format_exc())

    async def set_if_not_exists(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Атомарно устанавливает значение, только если ключ не существует.
        Возвращает True, если значение было установлено.
        """
        if not self.redis_conn:
            return False

        try:
            full_key = self.make_key(key)
            success = await self.redis_conn.set(full_key, value, ex=ttl or self.default_ttl, nx=True)
            logger.debug(f"🔐 set_if_not_exists({full_key}) → {success}")
            return success
        except Exception as e:
            logger.error(f"❌ Ошибка set_if_not_exists: {e}")
            logger.debug(traceback.format_exc())
            return False
