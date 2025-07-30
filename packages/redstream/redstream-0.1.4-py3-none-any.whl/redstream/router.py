import asyncio
import logging
import redis.asyncio as redis
import traceback
from .types import RSMessage
from .consumer_group_manager import initialize_consumer_groups
from .request_handler import send_request_with_timeout, send_streaming_request, _sanitize_dict
import uuid

from .utils.logging_helpers import LoggerWithCaller
logger = LoggerWithCaller("redstream.redis_stream_router")

class RedisStreamRouter:
    """Маршрутизатор сообщений между потоками Redis Streams."""

    def __init__(self, max_concurrent_requests=100):
        self.redis_url = None
        self.redis_conn = None  # Подключение к Redis устанавливается позже
        self.source_streams = []
        self.consumer_groups = {}
        self.handlers = {}
        self.shutdown_event = asyncio.Event()
        self.queue = asyncio.Queue()
        self.tasks = []
        self.request_semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def set_config(self, redis_url, redis_handler, package_name, source_streams=None, consumer_groups=None, consumer_group=None, handlers=None):
        """Настройка RedisStreamRouter + подключение к Redis."""
        self.redis_url = redis_url
        self.redis_conn = redis.from_url(self.redis_url, decode_responses=True)

        # Автоматически загружаем все обработчики
        redis_handler.auto_register_handlers(package_name)
        handlers = redis_handler.get_handlers()
        registered_consumer_groups = redis_handler.get_consumer_groups()
        logger.info(f"🔄 Зарегистрированные хендлеры: {handlers}")

        # Определяем source_streams
        if source_streams is not None:
            self.source_streams = source_streams
        elif consumer_groups is not None:
            self.source_streams = list(consumer_groups.keys())
        elif handlers is not None:
            self.source_streams = list(handlers.keys())

        # Объединяем consumer_groups
        self.consumer_groups = {}
        for stream in self.source_streams:
            if stream in registered_consumer_groups:
                self.consumer_groups[stream] = registered_consumer_groups[stream]
            elif consumer_groups and stream in consumer_groups:
                self.consumer_groups[stream] = consumer_groups[stream]
            elif consumer_group:
                self.consumer_groups[stream] = consumer_group

        # Гарантируем, что у всех потоков есть группа
        missing_groups = [s for s in self.source_streams if s not in self.consumer_groups]
        if missing_groups:
            package_group = f"{package_name}_group" if package_name else "default_group"
            for stream in missing_groups:
                self.consumer_groups[stream] = package_group
            logger.warning(f"⚠️ Потоки {missing_groups} не имели групп. Используется `{package_group}`.")

        if handlers is not None:
            self.handlers = handlers

        await initialize_consumer_groups(self.redis_conn, self.consumer_groups)
        logger.info(f"🔄 Итоговый source_streams: {self.source_streams}")
        logger.info(f"🔄 Итоговый consumer_groups: {self.consumer_groups}")

    async def publish_message(self, target_stream, rs_message: RSMessage):
        """Отправляет сообщение в указанный поток Redis."""
        message = rs_message.to_dict()
        
        # Применяем санитизацию перед отправкой
        sanitized_message = _sanitize_dict(message)

        if not target_stream:
            logger.error(f"❌ Попытка отправить сообщение без указанного stream. RSMessage: {rs_message.to_json()}")
            return

        if not self.redis_conn:
            logger.error("🚨 Ошибка: Redis не подключен!")
            return

        try:
            await self.redis_conn.xadd(target_stream, sanitized_message)
            if not rs_message.response_stream and rs_message.event_type != "response":
                logger.warning(f"⚠️ Сообщение без response_stream отправлено в {target_stream}: {sanitized_message}")
            else:
                logger.info(f"📤 Сообщение отправлено в {target_stream}: {sanitized_message}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в {target_stream}: {e}")
            logger.debug(traceback.format_exc())

    async def read_messages(self, source_stream):
        """Читает сообщения из потока и помещает их в очередь."""
        if not self.redis_conn:
            logger.error("🚨 Ошибка: Redis не подключен!")
            return

        group = self.consumer_groups[source_stream]
        consumer = f"{source_stream}_consumer"

        while not self.shutdown_event.is_set():
            try:
                messages = await self.redis_conn.xreadgroup(
                    groupname=group,
                    consumername=consumer,
                    streams={source_stream: ">"},
                    count=10,
                    block=2000
                )
                if messages:
                    for stream, msg_list in messages:
                        for message_id, message_data in msg_list:
                            await self.queue.put((stream, message_id, message_data))
            except Exception as e:
                logger.error(f"❌ Ошибка чтения из {source_stream}: {e}")
                logger.debug(traceback.format_exc())

        logger.info(f"🛑 Чтение из {source_stream} остановлено.")



    async def process_messages(self):
        """Обрабатывает сообщения из очереди, вызывая обработчики асинхронно."""
        while not self.shutdown_event.is_set():
            try:
                stream, message_id, message_data = await self.queue.get()
                logger.info(f"📩 Получено сообщение из {stream}: {message_data}")

                if stream not in self.handlers or not self.handlers[stream]:
                    logger.warning(f"⚠ Нет зарегистрированных обработчиков для потока {stream}")
                    continue

                rs_message = RSMessage.from_dict(message_data)
                rs_message.system_data = {
                    "message_id": message_id,
                    "stream": stream
                }

                handled = False

                for handler_func, filter_func in self.handlers[stream]:
                    try:
                        if filter_func and not filter_func(rs_message):
                            logger.info(f"⏩ Фильтр '{handler_func.__name__}' отклонил сообщение ID: {message_data.get('message_id')}")
                            continue

                        logger.info(f"✅ Фильтр '{handler_func.__name__}' принял сообщение ID: {message_data.get('message_id')}")

                        # Запускаем хендлер в фоне
                        asyncio.create_task(self._run_handler(handler_func, rs_message, stream, message_id))
                        handled = True
                        break  # не дожидаемся — просто доверяем _run_handler
                    except Exception as e:
                        logger.error(f"❌ Ошибка в фильтрации/запуске хендлера {handler_func.__name__}: {e}")
                        logger.debug(traceback.format_exc())

                if not handled:
                    logger.debug(f"⏭ Сообщение из {stream} не было обработано ни одним хендлером")

            except Exception as e:
                logger.error(f"❌ Ошибка обработки сообщения из очереди: {e}")
                logger.debug(traceback.format_exc())



    async def _run_handler(self, handler_func, rs_message, stream, message_id):
        async with self.request_semaphore:
            try:
                result = await handler_func(rs_message)

                if result is True:
                    await self.redis_conn.xack(stream, self.consumer_groups[stream], message_id)
                    return

                correlation_id = rs_message.correlation_id

                if isinstance(result, RSMessage):
                    result = result.to_dict()

                if isinstance(result, dict):
                    for target_stream, result_data in result.items():
                        if correlation_id:
                            result_data.correlation_id = correlation_id

                        if isinstance(result_data, RSMessage):
                            msg_dict = result_data.to_dict()
                            sanitized_result = _sanitize_dict(msg_dict)
                            await self.redis_conn.xadd(target_stream, sanitized_result)
                        else:
                            sanitized_result = _sanitize_dict(result_data)
                            await self.redis_conn.xadd(target_stream, sanitized_result)

                    await self.redis_conn.xack(stream, self.consumer_groups[stream], message_id)
                else:
                    logger.debug(f"⏭ Хендлер {handler_func.__name__} не вернул результат")
            except Exception as e:
                logger.error(f"❌ Ошибка в асинхронном хендлере {handler_func.__name__}: {e}")
                logger.debug(traceback.format_exc())



    async def send_request_with_timeout(self, target_stream, rs_message: RSMessage, response_stream=None, timeout=5, max_retries=3):
        """
        Отправляет запрос с таймаутом.
        Обертка вокруг функции из request_handler для сохранения обратной совместимости.
        """
        async with self.request_semaphore:
            return await send_request_with_timeout(self.redis_conn, self.redis_url, target_stream, rs_message, response_stream, timeout, max_retries)

    async def send_streaming_request(
        self, target_stream, message, response_stream=None,
        initial_timeout=5, max_retries=3, track_own_responses=True
    ):
        """
        Потоковый запрос с промежуточными ответами.
        Обертка вокруг функции из request_handler с контролем завершения генератора.
        """
        async with self.request_semaphore:
            gen = send_streaming_request(
                self.redis_conn,
                self.redis_url,
                target_stream,
                message,
                response_stream,
                initial_timeout,
                max_retries,
                track_own_responses
            )
            try:
                async for response in gen:
                    yield response
            finally:
                await gen.aclose()

    async def set_if_not_exists(self, key: str, value: str, expire_seconds: int) -> bool:
        """
        Устанавливает ключ, если он не существует. Возвращает True, если ключ был установлен.
        Используется для защиты от повторной публикации задач.
        """
        if not self.redis_conn:
            logger.error("🚨 Попытка записи ключа в Redis до подключения!")
            return False

        try:
            return await self.redis_conn.set(key, value, ex=expire_seconds, nx=True)
        except Exception as e:
            logger.error(f"❌ Ошибка при установке ключа в Redis: {e}")
            logger.debug(traceback.format_exc())
            return False

    async def start(self):
        """Запускает чтение сообщений (группы уже созданы)."""
        self.shutdown_event.clear()

        for stream in self.source_streams:
            self.tasks.append(asyncio.create_task(self.read_messages(stream)))
        self.tasks.append(asyncio.create_task(self.process_messages()))

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            logger.info("🛑 RedisStreamRouter остановлен.")

    async def stop(self):
        """Останавливает роутер, дожидаясь обработки всех сообщений в очереди."""
        logger.info("🛑 Остановка RedisStreamRouter...")
        self.shutdown_event.set()

        while not self.queue.empty():
            await asyncio.sleep(0.1)

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, return_exceptions=True)
        logger.info("✅ Все процессы завершены.")

# Глобальный объект `redis_router` для использования в пакете
redis_router = RedisStreamRouter()
