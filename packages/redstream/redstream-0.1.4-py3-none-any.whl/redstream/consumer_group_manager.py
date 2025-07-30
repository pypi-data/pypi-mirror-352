import asyncio
import logging
import traceback
from redis.exceptions import ResponseError

logger = logging.getLogger("redstream.redis_stream_router.consumer_group_manager")

async def initialize_consumer_groups(redis_conn, consumer_groups):
    """
    Создает группы потребителей для каждого потока, если они еще не существуют.
    """
    for stream, group in consumer_groups.items():
        try:
            await redis_conn.xgroup_create(stream, group, id="0", mkstream=True)
            logger.info(f"✅ Группа {group} создана для {stream}")
        except ResponseError as e:
            if "BUSYGROUP" in str(e):
                logger.info(f"⚠️ Группа {group} уже существует для {stream}")
            else:
                logger.error(f"❌ Ошибка создания группы {group} для {stream}: {e}")
                logger.debug(traceback.format_exc())
