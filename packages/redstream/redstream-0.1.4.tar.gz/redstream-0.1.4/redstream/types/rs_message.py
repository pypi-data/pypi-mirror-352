from copy import deepcopy
import json
import pytz
import uuid
from typing import Optional, Dict, Any, Union
import logging
from .rs_message_status import RSMessageStatus
logger = logging.getLogger("redstream.types.rs_message")


class RSMessage:
    """Универсальная структура сообщения для микросервисной архитектуры (Redis Streams)."""
    
    """
    Поддерживает:
    - Текстовые, мультимедийные, голосовые сообщения
    - Ответы (`reply_to_message_id`)
    - Correlation ID для трекинга запросов
    - Совместимость с aiogram Message (если aiogram доступен)
    - Готов для работы с RedisStreamRouter
    """

    extra_data: Dict[str, Any]  # 💡 IDE теперь будет подсвечивать

    def __init__(
        self,
        event_type: str,                                # Тип события ("message", "edit_message", "response"...)
        initial_response_stream: Optional[str] = None,  # Исходный трим отправителя для ответа
        message_type: Optional[str] = "text",           # Тип сообщения
        action: Optional[str] = "",                     # Требуемое действие
        status: Optional[RSMessageStatus] = None,       # Статусное сообщение
        chat_id: Optional[str] = None,                  # ID чата (группы)
        user_id: Optional[str] = None,                  # ID пользователя
        message_id: Optional[str] = None,               # ID сообщения в чате
        text: Optional[str] = "",                       # Текст события
        is_command: Optional[bool] = False,             # Является ли событие командой
        date: Optional[str] = None,                     # Дата/время сообщения
        reply_to_message_id: Optional[Union[str, int]] = None,  # ID сообщения, на которое отвечает текущее
        file_path: Optional[str] = None,                # Путь к файлу
        correlation_id: Optional[str] = None,           # ID корреляции
        response_stream: Optional[str] = None,          # Стрим для ответа
        extra_data: Optional[Dict[str, Any]] = None,    # Дополнительные данные
    ):
        self.event_type = event_type
        self.initial_response_stream = initial_response_stream
        self.message_type = message_type
        self.action = action
        self.status = status
        self.chat_id = chat_id
        self.user_id = user_id
        self.message_id = message_id
        self.text = text or ""
        self.is_command = is_command
        self.date = date or self._current_time()
        self.reply_to_message_id = str(reply_to_message_id) if reply_to_message_id else None
        self.file_path = file_path
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.response_stream = response_stream
        self._extra_data = extra_data or {}

        # Систеные данные потока. Не сериализуется специально
        self.system_data = {
            "message_id": None,
            "stream": None
        }

    @property
    def extra_data(self) -> Dict[str, Any]:
        """Безопасный доступ к extra_data (без возможности перезаписи словаря целиком)."""
        return self._extra_data

    @extra_data.setter
    def extra_data(self, value):
        raise AttributeError("❌ Прямое присваивание extra_data запрещено.")

    @staticmethod
    def _current_time() -> str:
        """Возвращает текущее время в формате UTC."""
        return pytz.utc.localize(pytz.datetime.datetime.utcnow()).isoformat()

    @staticmethod
    def to_bool(value):
        if value in (1, "1"):
            return True
        elif value in (0, "0", None):
            return False
        raise logger.error(f"❌ Недопустимое значение для преобразования в bool: {value}")

    @staticmethod
    def parse_user_id(value) -> Optional[int]:
        """Безопасное преобразование user_id в int"""
        try:
            if value is None:
                return None
            str_value = str(value).strip()
            return int(str_value) if str_value.isdigit() else None
        except Exception as e:
            logger.warning(f"⚠️ Невалидный user_id: {value} ({e})")
            return None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RSMessage":
        """Создает объект RSMessage из словаря."""

        def safe_json_loads(value: Any) -> Any:
            """Попытка распарсить JSON-строку, иначе вернуть как есть."""
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ Ошибка разбора JSON: {value}")
                    return value  # Если JSON некорректен, оставляем строку (но лучше избегать такого)
            return value

        # Внутри from_dict
        status_raw = data.get("status", None)
        status_obj = None

        if isinstance(status_raw, str) and status_raw.strip().startswith("{"):
            try:
                status_obj = RSMessageStatus.from_json(status_raw)
            except Exception as e:
                logger.warning(f"⚠️ Невалидный JSON в status: {e}")
        elif isinstance(status_raw, dict):
            status_obj = RSMessageStatus.from_dict(status_raw)

        #logger.debug(f"📩 from_dict() входные данные: {data}")

        instance = cls(
            event_type=data.get("event_type", "message"),
            initial_response_stream=data.get("initial_response_stream"),
            message_type=data.get("message_type", "text"),
            action=data.get("action", ""),
            status=status_obj,
            chat_id=data.get("chat_id"),
            user_id=cls.parse_user_id(data.get("user_id")),
            message_id=str(data["message_id"]) if data.get("message_id") is not None else None,
            text=data.get("text", ""),
            is_command=cls.to_bool(data.get("is_command", False)),
            date=data.get("date"),
            reply_to_message_id=str(data["reply_to_message_id"]) if data.get("reply_to_message_id") else None,
            file_path=data.get("file_path"),
            correlation_id=data.get("correlation_id") or str(uuid.uuid4()),
            response_stream=data.get("response_stream"),
            extra_data=safe_json_loads(data.get("extra_data", "{}")),
        )

        #logger.debug(f"📩 from_dict() создал RSMessage с message_id={instance.message_id}, correlation_id={instance.correlation_id}")

        return instance

    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует объект в словарь для передачи через Redis."""
        result = {}
        
        # Перебираем все атрибуты кроме system_data
        for k, v in self.__dict__.items():
            if k in ["system_data", "_extra_data"]:
                continue

            # Обработка значений перед вставкой
            if v is None:
                if k in ["text", "action", "correlation_id"]:
                    result[k] = ""  # Преобразуем None в пустую строку для текстовых полей
                continue  # Пропускаем None для других полей
            elif isinstance(v, bool):
                result[k] = "1" if v else "0"
            elif isinstance(v, (uuid.UUID, int)):
                result[k] = str(v)
            else:
                result[k] = v

        # Обеспечиваем наличие обязательных полей, даже если они None
        mandatory_fields = ["event_type", "message_type", "action", "chat_id", "user_id", "correlation_id"]
        for field in mandatory_fields:
            if field not in result:
                result[field] = ""

        # Сериализация status как JSON
        if isinstance(self.status, RSMessageStatus):
            result["status"] = self.status.to_json()

        # Сериализуем extra_data
        if isinstance(self.extra_data, dict):
            safe_extra_data = self._extra_data.copy()
            if isinstance(safe_extra_data.get("callback_data"), dict):
                safe_extra_data["callback_data"] = json.dumps(safe_extra_data["callback_data"], ensure_ascii=False)
            result["extra_data"] = json.dumps(safe_extra_data, ensure_ascii=False)
        else:
            result["extra_data"] = "{}"

        # Приводим correlation_id к строке
        result["correlation_id"] = str(result.get("correlation_id", "")) or str(uuid.uuid4())

        # user_id в строку
        if "user_id" in result and result["user_id"] is not None:
            result["user_id"] = str(result["user_id"])

        # Убеждаемся, что action не None
        if "action" not in result or result["action"] is None:
            result["action"] = ""

        return result

    def to_json(self) -> str:
        """Сериализация в JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "RSMessage":
        """Создает RSMessage из JSON-строки."""
        return cls.from_dict(json.loads(json_str))


    async def update_status(self, redis_router, timeout: int = 15) -> Optional["RSMessage"]:
        """
        Отправляет статусное сообщение без изменения оригинального текста.
        """
        if not self.status or not isinstance(self.status, RSMessageStatus):
            logger.warning("⚠️ Попытка обновить статус при отсутствии RSMessageStatus")
            return None

        # Готовим копию только для статуса
        msg = deepcopy(self)
        msg.event_type = "edit_message" if self.status.message_id else "message"
        msg.message_type = "text"
        msg.message_id = self.status.message_id
        msg.action = "status_update"
        msg.text = str(self.status)  # ТОЛЬКО В КОПИИ
        msg.correlation_id = str(uuid.uuid4())
        #msg.reply_to_message_id = self.message_id
        msg._extra_data["status_uid"] = self.status.uid

        logger.debug(f"📩 update_status() отправляем статус: {msg.to_dict()}")
        try:
            response: Optional[RSMessage] = await redis_router.send_request_with_timeout(
                target_stream=self.initial_response_stream,
                rs_message=msg,
                timeout=timeout,
                max_retries=2
            )

            if response and isinstance(response, RSMessage) and not self.status.message_id:
                self.status.set_message_id(response.message_id)

            return response

        except Exception as e:
            logger.exception(f"❌ Ошибка при update_status: {e}")
            return None



    def delete_status(self):
        self.status = None
        #self.text = ""

    def ensure_status(self, override: bool = False):
        """Гарантирует наличие status-объекта"""
        if self.status is None or override:
            self.status = RSMessageStatus()
        return self.status


    # === Методы для работы с aiogram (если доступен) ===
    @classmethod
    def from_aiogram_message(cls, message: Any, initial_response_stream) -> "RSMessage":
        """Создает RSMessage из aiogram.types.Message."""
        if not hasattr(message, "chat") or not hasattr(message, "from_user"):
            raise ValueError("Переданный объект не является aiogram Message.")

        return cls(
            event_type="message",
            initial_response_stream=initial_response_stream,
            message_type=message.content_type.value,
            chat_id=str(message.chat.id),
            user_id=str(message.from_user.id),
            message_id=str(message.message_id),
            text=message.text or message.caption or "",
            is_command=bool(message.text and message.text.startswith("/")),
            date=str(message.date),
            reply_to_message_id=str(message.reply_to_message.message_id) if message.reply_to_message else None,
            file_path=None,
            extra_data={},  # <-- добавлено
        )

    def to_aiogram_message(self) -> Dict[str, Any]:
        """Конвертирует RSMessage в JSON-структуру, схожую с aiogram Message."""
        return {
            "chat": {"id": int(self.chat_id) if self.chat_id else None},
            "from_user": {
                "id": int(self.user_id) if self.user_id else None,
            },
            "message_id": int(self.message_id) if self.message_id else None,
            "date": self.date,
            "text": self.text,
            "content_type": self.message_type,
            "reply_to_message_id": int(self.reply_to_message_id) if self.reply_to_message_id else None,
            "correlation_id": self.correlation_id,
        }

    @staticmethod
    def extract_media_data(message: Any) -> Optional[Dict[str, Any]]:
        """Извлекает информацию о мультимедиа (фото, видео, документы) из aiogram Message."""
        media_data = None
        if hasattr(message, "photo") and message.photo:
            media_data = {"type": "photo", "file_id": message.photo[-1].file_id}
        elif hasattr(message, "video") and message.video:
            media_data = {"type": "video", "file_id": message.video.file_id}
        elif hasattr(message, "document") and message.document:
            media_data = {
                "type": "document",
                "file_id": message.document.file_id,
                "file_name": message.document.file_name,
            }
        elif hasattr(message, "voice") and message.voice:
            media_data = {"type": "voice", "file_id": message.voice.file_id}
        elif hasattr(message, "audio") and message.audio:
            media_data = {"type": "audio", "file_id": message.audio.file_id}
        return media_data


