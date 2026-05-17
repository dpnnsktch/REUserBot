# REUserBot

Telegram UserBot с использованием Pyrogram и Telethon для импорта модулей.

## 🚀 Быстрый старт

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Настройка
1. Отредактируйте `config.py` (опционально, основные настройки установятся автоматически)
2. Запустите юзербота:
```bash
python main.py
```

### Первый запуск
При первом запуске юзербот:
- Определит ваш Telegram ID и сохранит в config.py
- Создаст приватный чат для логов
- Отправит приветственное сообщение
- Загрузит все существующие модули

## 📁 Структура проекта

```
REUserBot/
├── modules/           # Все модули
│   └── Custom/        # Пользовательские модули
├── core/              # Основной функционал
│   ├── system.py      # Системные утилиты
│   ├── security.py    # Менеджер безопасности
│   ├── module_manager.py  # Управление модулями
│   ├── module_importer.py # Импорт модулей
│   └── commands.py    # Обработчик команд
├── logs/              # Логи
├── sessions/          # Сессии (защищено)
├── config.py          # Конфигурация
├── main.py            # Точка входа
└── help.py            # Полное руководство
```

## 📦 Команды

### Модули
- `.module import {link|local|tg|channel} [args]` - Импорт модуля
- `.module list` - Список модулей
- `.module del <name>` - Удалить модуль
- `.module perm <name>` - Показать права модуля
- `.module config <name> <key> <value>` - Изменить конфиг
- `.module info <name>` - Информация о модуле
- `.module root <name>` - Дать полный доступ (требует подтверждения)
- `.module block <name>` - Ограничить модуль
- `.module error <name>` - Показать ошибки
- `.module line <name> {show|replace} <line> [content]` - Редактировать код
- `.module restart <name> [debug]` - Перезагрузить модуль

### Безопасность
- `.security` - Помощь по безопасности
- `.security whitelist` - Белый список модулей
- `.security on/off` - Включить/выключить безопасность

### Системные
- `.reboot` - Перезапустить юзербота
- `.off` - Выключить юзербота
- `.welcome` - Приветственное сообщение
- `.update` - Проверить обновления

## 🔒 Безопасность

Модуль security защищает от:
- Опасных операций (os.remove, eval, exec)
- Доступа к папке sessions
- Вредоносного кода в модулях

Уровни доступа:
1. **Normal** - Стандартная защита
2. **Blocked** - Модуль ограничен папкой Custom
3. **Root** - Полный доступ (требует подтверждения кодом)

## 🔧 Создание модулей

Пример простого модуля:

```python
# My Module
from pyrogram import Client, filters

__doc__ = "Мой модуль"
commands = ["test"]

@Client.on_message(filters.command("test", prefixes=".") & filters.me)
async def test_cmd(client, message):
    await message.edit("Hello from my module!")
```

Сохраните в `modules/Custom/my_module.py`

## 📖 Документация

Полное руководство доступно через команду `.help` или в файле `help.py`.

## 📞 Поддержка

- GitHub: https://github.com/dpnnsktch/REUserBot
- Канал: @pitupiarbitrash

## ⚠️ Важно

- Никогда не передавайте session файлы
- Будьте осторожны с `.module root` - дает полный доступ
- Проверяйте код модулей перед импортом
