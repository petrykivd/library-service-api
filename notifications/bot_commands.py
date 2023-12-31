import os
from dotenv import load_dotenv

from notifications.bot_utils import asyncio_run
from notifications.management.commands.start_bot import send_message

import pyshorteners

load_dotenv()

ADMIN_GROUP = int(os.getenv("ADMIN_GROUP", 0))

PAYMENT_IMAGE_URL = "https://i.imgur.com/VWH0a9i.jpg"
BORROWING_IMAGE_URL = "https://i.imgur.com/Yjf9ARQ.jpg"


async def _send_payment_notification(
        telegram_id,
        message_to_user,
        message_to_admin
):
    if telegram_id:
        await send_message(
            telegram_id=telegram_id,
            message=message_to_user,
            image=PAYMENT_IMAGE_URL

        )
    if ADMIN_GROUP:
        await send_message(
            telegram_id=ADMIN_GROUP,
            message=message_to_admin,
            image=PAYMENT_IMAGE_URL
        )


async def _send_overdue_notification(
        telegram_id,
        message
):
    await send_message(telegram_id, message=message)
    if ADMIN_GROUP:
        await send_message(
            telegram_id=ADMIN_GROUP,
            message="overdue"
        )


async def _send_borrowing_notification(
        telegram_id,
        message_to_user,
        message_to_admin,
):
    if telegram_id:
        await send_message(
            telegram_id=telegram_id,
            message=message_to_user,
            image=BORROWING_IMAGE_URL
        )
    if ADMIN_GROUP:
        await send_message(
            telegram_id=ADMIN_GROUP,
            message=message_to_admin,
            image=BORROWING_IMAGE_URL
        )


def send_borrowing_notification(user, borrowing):
    payment_info = borrowing.payments.filter(status="PENDING").first()
    long_session_url = payment_info.session_url

    type_tiny = pyshorteners.Shortener()
    short_session_url = type_tiny.tinyurl.short(long_session_url)

    money = payment_info.money_to_pay

    telegram_id = None
    if user.telegram_notifications_enabled and user.telegram_id:
        telegram_id = user.telegram_id

    message_to_user = (
        f"📕 You have new borrowing: {borrowing.book.title}! "
        f"💰You need to pay {money} $ "
        f"🔗You can do it here: {short_session_url}"
    )

    message_to_admin = (
        f"📕 New borrowing: {borrowing.book.title} from "
        f"✉️ user {borrowing.user.email}."
        f"💰 Price: {money} $ "
    )
    asyncio_run(
        _send_borrowing_notification(
            telegram_id,
            message_to_user,
            message_to_admin,
        )
    )


def send_overdue_notification(
        users: dict,
) -> None:
    for user in users:
        asyncio_run(
            _send_overdue_notification(user, users[user]["book"])
        )


def send_payment_notification(user, payment):
    telegram_id = None
    if user.telegram_notifications_enabled and user.telegram_id:
        telegram_id = user.telegram_id

    message_to_user = (
        f"💰 Payment for 📕 {payment.borrowing.book.title} successful! "
        f"Paid: {payment.money_to_pay} $"
    )
    message_to_admin = message_to_user + f" by user {payment.user.email}"

    asyncio_run(
        _send_payment_notification(
            telegram_id,
            message_to_user=message_to_user,
            message_to_admin=message_to_admin,
        )
    )
