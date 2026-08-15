import logging
import os

from celery import shared_task
from .models import TelegramChat
import requests

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

@shared_task
def send_habit_reminder(habit_id):
    from habits.models import Habit
    try:
        habit = Habit.objects.get(pk=habit_id)
    except Habit.DoesNotExist:
        logger.warning(f'Habit {habit_id} not found')
        return

    chats = TelegramChat.objects.filter(user=habit.user, is_active=True)
    if not chats.exists():
        return

    text = (
        f"⏰ Напоминание о привычке:\n\n"
        f"{habit.action}\n"
        f"Место: {habit.place or 'не указано'}\n"
        f"Время: {habit.time_of_day or 'любое'}\n"
        f"Длительность: {habit.duration_seconds} сек"
    )

    token = 'YOUR_TELEGRAM_BOT_TOKEN'
    for chat in chats:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send message to chat {chat.chat_id}: {e}")