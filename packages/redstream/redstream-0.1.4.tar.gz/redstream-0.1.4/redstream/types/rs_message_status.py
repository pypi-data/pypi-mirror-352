import json
import uuid
from typing import Optional, Dict, List, Union, Any


class RSMessageStatus:
    """
    Управляет статусом сообщения:
    - Хранит блоки по ключам
    - Поддерживает редактирование, удаление и финализацию
    - Отслеживает message_id (для редактирования сообщения)
    - Гарантирует порядок блоков (вставка по ключу с порядком)
    """

    def __init__(
        self,
        blocks: Optional[Dict[str, str]] = None,
        order: Optional[List[str]] = None,
        finalized: bool = False,
        uid: Optional[str] = None,
        message_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,    # Дополнительные данные
    ):
        self.blocks: Dict[str, str] = blocks or {}
        self.order: List[str] = order or list(self.blocks.keys())
        self.finalized: bool = finalized
        self.uid: str = uid or str(uuid.uuid4())
        self.message_id: Optional[str] = message_id
        self.extra_data: Optional[Dict[str, Any]] = extra_data or {}

    def add_block(self, key: str, content: str):
        """Добавить или перезаписать блок. Поддерживает порядок вставки."""
        if self.finalized:
            return
        is_new = key not in self.blocks
        self.blocks[key] = content
        if is_new:
            self.order.append(key)

    def edit_block(self, key: str, content: str):
        """Изменить содержимое существующего блока."""
        if not self.finalized and key in self.blocks:
            self.blocks[key] = content

    def delete_block(self, key: str):
        """Удалить блок и его ключ из порядка."""
        if not self.finalized and key in self.blocks:
            self.blocks.pop(key)
            self.order = [k for k in self.order if k != key]

    def edit_last_block(self, content: str):
        """Изменить последний добавленный блок."""
        if not self.finalized and self.order:
            last_key = self.order[-1]
            self.blocks[last_key] = content

    def finalize(self, final_block: Optional[str] = None, key: str = "final"):
        """Завершить статус. Опционально добавить финальный блок."""
        if final_block:
            self.add_block(key, final_block)
        self.finalized = True

    def clear(self):
        """Очистить все блоки."""
        self.blocks.clear()
        self.order.clear()
        self.finalized = False

    def new_status(self):
        """Очистить все блоки и сбросить состояние."""
        self.blocks.clear()
        self.order.clear()
        self.finalized = False
        self.message_id = None

    def set_message_id(self, msg_id: str):
        """Установить message_id для последующего редактирования."""
        if not self.message_id:
            self.message_id = msg_id

    def to_dict(self) -> Dict[str, Union[str, bool, Dict[str, str], List[str]]]:
        return {
            "uid": self.uid,
            "blocks": self.blocks,
            "order": self.order,
            "finalized": self.finalized,
            "message_id": self.message_id or ""
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Union[str, bool, Dict[str, str], List[str]]]) -> "RSMessageStatus":
        return cls(
            blocks=data.get("blocks", {}),
            order=data.get("order", list(data.get("blocks", {}).keys())),
            finalized=data.get("finalized", False),
            uid=data.get("uid"),
            message_id=data.get("message_id")
        )

    @classmethod
    def from_json(cls, json_str: str) -> "RSMessageStatus":
        return cls.from_dict(json.loads(json_str))

    def __str__(self) -> str:
        """Человеко-читаемый текст со всеми блоками по порядку."""
        lines = [self.blocks[key] for key in self.order if key in self.blocks]
        if self.finalized:
            lines.append("✅ Завершено")
        return "\n\n".join(lines).strip()

    def is_empty(self) -> bool:
        return not self.order
