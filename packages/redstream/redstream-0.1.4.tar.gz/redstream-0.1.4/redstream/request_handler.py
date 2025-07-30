import asyncio
import logging
import uuid
import redis.asyncio as redis
from redis.exceptions import ConnectionError, ResponseError
from .types.rs_message import RSMessage
import copy
import traceback

from .utils.logging_helpers import LoggerWithCaller
logger = LoggerWithCaller("redstream.redis_stream_router.request_handler")

def _sanitize_dict(data):
    """Санитизация ключей и значений для Redis: всё должно быть str"""
    if not isinstance(data, dict):
        return {}

    sanitized = {}
    for k, v in data.items():
        # Обработка ключей
        if k is None:
            continue  # пропускаем, т.к. Redis не принимает ключ None
        key = str(k)

        # Обработка значений
        if v is None:
            sanitized[key] = ""
        elif isinstance(v, bool):
            sanitized[key] = "1" if v else "0"
        elif isinstance(v, (int, float, str, bytes)):
            sanitized[key] = v
        else:
            try:
                sanitized[key] = str(v)
            except Exception as e:
                logger.warning(f"⚠️ Невозможно сериализовать значение {v} ({type(v)}): {e}")
                sanitized[key] = ""

    return sanitized

async def send_request_with_timeout(
    redis_conn, redis_url, target_stream, rs_message: RSMessage,
    response_stream=None, timeout=10, max_retries=3
):
    # Создаем глубокую копию сообщения, чтобы не модифицировать оригинальный объект.
    msg = copy.deepcopy(rs_message)
    
    # Устанавливаем correlation_id, если его нет в копии
    correlation_id = msg.correlation_id or str(uuid.uuid4())
    msg.correlation_id = correlation_id
    request_id = str(uuid.uuid4())
    
    # Формирование response_stream, если не передано явно
    if response_stream is None:
        response_stream = f"response_stream_{request_id}"
    
    response_group = f"{response_stream}_group"
    consumer_name = f"consumer_{request_id}"
    
    # Задаем response_stream только для копии сообщения, чтобы оригинал оставался неизменным
    msg.response_stream = response_stream
    
    # Удаляем дублирующий ключ в extra_data, если он присутствует, чтобы избежать конфликтов
    if "response_stream" in msg.extra_data:
        logger.warning("⚠️ 'response_stream' найден в extra_data — будет удалён, чтобы избежать конфликта.")
        msg.extra_data.pop("response_stream")
    
    response_redis_conn = None
    try:
        # Создаем соединение для получения ответа
        response_redis_conn = redis.from_url(redis_url, decode_responses=True)
        
        try:
            await response_redis_conn.xgroup_create(response_stream, response_group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.error(f"❌ Ошибка создания consumer group: {e}")
        
        # Отправляем сообщение с повторными попытками в указанный target_stream
        for attempt in range(max_retries):
            try:
                # Получаем словарь и санитизируем его перед отправкой
                message_dict = msg.to_dict()
                sanitized_dict = _sanitize_dict(message_dict)
                
                logger.debug(f"sanitized_dict: {sanitized_dict}")

                for k, v in sanitized_dict.items():
                    if k is None:
                        logger.error("❌ Обнаружен ключ None перед отправкой в Redis!")
                    elif v is None:
                        logger.error(f"❌ Обнаружено значение None: ключ='{k}'")
                    elif not isinstance(k, (str, bytes)):
                        logger.error(f"❌ Ключ имеет недопустимый тип: {type(k)} — {k}")
                    elif not isinstance(v, (str, bytes, int, float)):
                        logger.error(f"❌ Значение имеет недопустимый тип: {type(v)} — {k}={v}")

                if target_stream is None:
                    raise ValueError("❌ target_stream не задан! Невозможно отправить сообщение в Redis.")

                await redis_conn.xadd(target_stream, sanitized_dict)
                logger.info(f"📤 Сообщение с таймаутом {timeout} секунд! Отправлено в {target_stream} → ответ ожидается в {response_stream}, correlation_id={correlation_id}")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка отправки (попытка {attempt + 1}): {e}")
                logger.debug(traceback.format_exc())
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        
        # Ожидаем ответа с заданным таймаутом
        try:
            response = await asyncio.wait_for(
                _read_response(response_redis_conn, response_stream, response_group, consumer_name, correlation_id),
                timeout=timeout
            )
            logger.info(f"📥 Получен ответ в {response_stream}, correlation_id={correlation_id}")
            return response
        except asyncio.TimeoutError:
            logger.warning(f"⏳ Таймаут ожидания ответа в {response_stream}, correlation_id={correlation_id}")
            return None
    
    except Exception as e:
        logger.exception(f"❌ Неожиданная ошибка: {e}")
        return None
    
    finally:
        # Корректное закрытие соединения
        if response_redis_conn:
            try:
                await response_redis_conn.xgroup_delconsumer(response_stream, response_group, consumer_name)
                await response_redis_conn.aclose()
            except Exception as e:
                logger.warning(f"⚠️ Ошибка закрытия соединения: {e}")


async def _read_response(redis_conn, stream, group, consumer, correlation_id):
    """Вспомогательная функция для чтения ответа из Redis Stream"""
    while True:
        try:
            messages = await redis_conn.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream: ">"},
                count=1,
                block=1000  # Ожидаем новые сообщения с таймаутом в 1 секунду
            )
            
            if not messages:
                # Используем короткий asyncio.sleep вместо активного опроса
                await asyncio.sleep(0.1)
                continue
                
            for stream_name, msg_list in messages:
                for msg_id, data in msg_list:
                    if (
                        str(data.get("correlation_id", "")) == correlation_id
                        and data.get("event_type") == "response"
                        #and data.get("message_id")
                    ):
                        await redis_conn.xack(stream_name, group, msg_id)
                        return RSMessage.from_dict(data)
                    else:
                        # Подтверждаем получение сообщения, даже если оно не то, что мы ищем
                        await redis_conn.xack(stream_name, group, msg_id)
                        
        except ConnectionError as e:
            logger.warning(f"⚠️ Соединение потеряно: {e}")
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.exception(f"❌ Ошибка получения ответа: {e}")
            await asyncio.sleep(0.5)

async def send_streaming_request(
    redis_conn, redis_url, target_stream, rs_message: RSMessage,
    response_stream=None, initial_timeout=5, max_retries=3, track_own_responses=True
):
    correlation_id = rs_message.correlation_id or str(uuid.uuid4())
    rs_message.correlation_id = correlation_id

    if response_stream is None:
        response_stream = f"response_stream_{correlation_id}"

    response_group = f"{response_stream}_group"
    consumer_name = f"consumer_{correlation_id}"

    # ✅ Устанавливаем правильно
    rs_message.response_stream = response_stream

    # 🛡️ Удалим дублирующий ключ в extra_data
    if "response_stream" in rs_message.extra_data:
        logger.warning("⚠️ 'response_stream' найден в extra_data — будет удалён, чтобы избежать конфликта.")
        rs_message.extra_data.pop("response_stream")

    response_redis_conn = None
    try:
        # Получаем словарь и санитизируем его перед отправкой
        message_dict = rs_message.to_dict()
        sanitized_dict = _sanitize_dict(message_dict)
        
        # Отправляем сообщение
        await redis_conn.xadd(target_stream, sanitized_dict)
        logger.info(f"📤 Потоковый запрос: {target_stream} → {response_stream}, correlation_id={correlation_id}")

        # Создаем соединение для получения ответов
        response_redis_conn = redis.from_url(redis_url, decode_responses=True)
        
        try:
            await response_redis_conn.xgroup_create(response_stream, response_group, id="0", mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.error(f"❌ Ошибка создания группы: {e}")

        # Начинаем прослушивание потока
        final_received = False
        while not final_received:
            try:
                messages = await response_redis_conn.xreadgroup(
                    groupname=response_group,
                    consumername=consumer_name,
                    streams={response_stream: ">"},
                    count=10,
                    block=2000  # Увеличиваем timeout для более эффективного ожидания
                )
                
                if not messages:
                    continue
                    
                for stream, msg_list in messages:
                    for msg_id, data in msg_list:
                        # Проверяем, принадлежит ли сообщение нашему потоку
                        if (
                            not track_own_responses
                            or str(data.get("correlation_id", "")) == correlation_id
                        ):
                            await response_redis_conn.xack(stream, response_group, msg_id)
                            message = RSMessage.from_dict(data)
                            yield message
                            
                            # Проверяем, является ли это финальным сообщением
                            if data.get("final_chunk") == "1":
                                final_received = True
                                return
                        else:
                            # Подтверждаем даже не наши сообщения
                            await response_redis_conn.xack(stream, response_group, msg_id)
                            
            except ConnectionError as e:
                logger.warning(f"⚠️ Временная потеря соединения: {e}")
                await asyncio.sleep(0.5)  # Небольшая пауза перед повторной попыткой
            except Exception as e:
                logger.exception(f"❌ Ошибка при чтении сообщений: {e}")
                await asyncio.sleep(0.2)

    except GeneratorExit:
        logger.warning("🧹 Поток прерван — остановка генератора.")
        raise

    except Exception as e:
        logger.exception(f"❌ Ошибка в send_streaming_request: {e}")

    finally:
        # Корректно закрываем ресурсы
        if response_redis_conn:
            try:
                await response_redis_conn.xgroup_delconsumer(response_stream, response_group, consumer_name)
                await response_redis_conn.aclose()
                logger.debug("🔒 Redis соединение закрыто.")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка при завершении соединения: {e}")
