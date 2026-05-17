"""
Пример модуля для REUserBot
Демонстрация основных возможностей
"""

from pyrogram import Client, filters

# Метаданные модуля
__doc__ = "Пример модуля для демонстрации возможностей REUserBot"
commands = ["hello", "ping", "info"]
permissions = []
requirements = []

# Конфигурация модуля
config = {
    "greeting": "Hello",
    "author": "User"
}


@Client.on_message(filters.command("hello", prefixes=".") & filters.me)
async def hello_command(client, message):
    """Приветственная команда"""
    greeting = config.get("greeting", "Hello")
    await message.edit(f"{greeting}! Это пример модуля REUserBot 🤖")


@Client.on_message(filters.command("ping", prefixes=".") & filters.me)
async def ping_command(client, message):
    """Проверка работоспособности"""
    await message.edit("🏓 Pong!")


@Client.on_message(filters.command("info", prefixes=".") & filters.me)
async def info_command(client, message):
    """Показать информацию о модуле"""
    info_text = f"""📋 Пример модуля

Автор: {config.get('author', 'Unknown')}
Версия: 1.0.0

Команды:
• .hello - Приветствие
• .ping - Проверка
• .info - Эта информация

Используйте .module config example <key> <value> для настройки
"""
    await message.edit(info_text)
