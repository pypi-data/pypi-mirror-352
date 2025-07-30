# RedStream

Асинхронный инструментарий для работы с Redis Streams и конфигурациями.

## Описание

RedStream - это Python библиотека, которая предоставляет удобный интерфейс для работы с Redis Streams. Она разработана для создания масштабируемых микросервисных архитектур с использованием Redis в качестве шины обмена сообщениями.

## Особенности

- Асинхронный API для работы с Redis Streams
- Система роутинга сообщений
- Работа с группами потребителей (Consumer Groups)
- Структуры сообщений с поддержкой типизации
- Отслеживание статусов сообщений в процессе обработки
- Интеграция с aiogram

## Установка

```bash
pip install redstream
```

## Простой пример использования

```python
import asyncio
from redstream import RSMessage, RSMessageStatus, RedisStreamRouter

async def main():
    # Инициализация роутера
    router = RedisStreamRouter(
        redis_url="redis://localhost:6379/0",
        stream_name="my_stream"
    )
    
    # Создание сообщения
    message = RSMessage(
        event_type="message",
        message_type="text",
        action="process",
        chat_id="123456",
        user_id="user123",
        text="Привет, RedStream!"
    )
    
    # Отправка сообщения
    await router.publish_message("my_stream", message)
    
    # Обработка сообщений
    async def message_handler(msg):
        print(f"Получено сообщение: {msg.text}")
        return True
    
    # Регистрация обработчика
    router.register_handler("message", message_handler)
    
    # Запуск обработки сообщений
    await router.start_consuming()

if __name__ == "__main__":
    asyncio.run(main())
```

## Лицензия

MIT

## Автор

Albert Toma (cornil@mail.ru) 