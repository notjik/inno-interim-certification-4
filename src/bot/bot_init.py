from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Command, CommandStart, CommandHelp
from database import db_session
from utils.load_local_variables import BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PATH, DB_PATH
from utils.loggers import logger_status, logger_database_engine
from bot.callbacks import cb_payload


# initializing the bot
bot = Bot(token=BOT_TOKEN)
dispatcher = Dispatcher(bot)


async def startup(callback):
    """
    Logging the launch of the bot

    :param callback: dispatcher object
    :return: None
    """
    db_session.global_init(DB_PATH)
    await bot.set_webhook(WEBHOOK_HOST + WEBHOOK_PATH)
    me = await callback.bot.get_me()
    extra = {
        'bot': me.username,
        'bot_id': me.id,
    }
    logger_status.info('has been successfully launched.', extra=extra)


async def shutdown(callback):
    """
    Logging off the bot

    :param callback: dispatcher object
    :return: None
    """
    logger_database_engine.info('Closing the connection due to program shutdown.')
    await bot.delete_webhook()
    me = await callback.bot.get_me()
    extra = {
        'bot': me.username,
        'bot_id': me.id,
    }
    logger_status.info('is disabled.', extra=extra)


def add_handlers():
    from bot.handlers import start_message, help_message, goto_subscribe, payment, process_pre_checkout_query, \
        process_pay, check_sub, push_cancel
    dispatcher.register_message_handler(start_message, CommandStart())
    dispatcher.register_message_handler(help_message, CommandHelp())
    dispatcher.register_message_handler(goto_subscribe, Command('menu'))
    dispatcher.register_callback_query_handler(payment, cb_payload.filter())
    dispatcher.register_pre_checkout_query_handler(process_pre_checkout_query)
    dispatcher.register_message_handler(process_pay, content_types=types.ContentType.SUCCESSFUL_PAYMENT)
    dispatcher.register_callback_query_handler(check_sub, text='check')
    dispatcher.register_callback_query_handler(push_cancel, text='cancel')
