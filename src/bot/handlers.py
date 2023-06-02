from aiogram import types
from database import db_session, users
from bot.keyboards import get_goto_subscribe, get_pay, get_check_subscribe
from bot.menu import set_starting_commands
from bot.bot_init import bot
from utils.load_local_variables import YOOMONEY_TOKEN
from utils.loggers import logger_message

pricing = {
    'basic': 250,
    'premium': 500,
    'vip': 1000
}


async def start_message(message: types.Message):
    await set_starting_commands(bot, message.chat.id)
    db_sess = db_session.create_session()
    q = db_sess.query(users.Users).filter_by(user_id=message.from_user.id)
    if not q.all():
        user = users.Users(user_id=message.from_user.id)
        db_sess.add(user)
        db_sess.commit()
    elif q.first().subscribe_type in ['basic', 'premium', 'vip']:
        username = message.from_user.username
        await message.answer(f'Welcome, {username}!')
    else:
        await message.answer('To get started, you need to subscribe', reply_markup=get_goto_subscribe())
    extra = {
        'user': message.from_user.username,
        'user_id': message.from_user.id,
        'content_type': '/start'
    }
    logger_message.info(message, extra=extra)


async def help_message(message: types.Message):
    await message.answer('You are in an information bot\n'
                         'A subscription is required to interact with the bot\n'
                         'If you have subscribed and it is not active, write'
                         'please administrators', reply_markup=get_check_subscribe())
    extra = {
        'user': message.from_user.username,
        'user_id': message.from_user.id,
        'content_type': '/help'
    }
    logger_message.info(message, extra=extra)


async def goto_subscribe(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Select a subscription category',
                           reply_markup=get_pay())
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'goto subscribe'
    }
    logger_message.info(callback.message, extra=extra)


async def payment(callback: types.CallbackQuery, callback_data: dict):
    await callback.answer()
    await bot.send_invoice(chat_id=callback.from_user.id,
                           title='{} subscribe'.format(callback_data['type'].capitalize()),
                           description='{} bot subscription'.format(callback_data['type'].capitalize()),
                           payload=callback_data['type'],
                           provider_token=YOOMONEY_TOKEN,
                           currency='RUB',
                           start_parameter='test_bot',
                           prices=[{'label': 'Rub', 'amount': pricing[callback_data['type']] * 100}])
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'start payment'
    }
    logger_message.info(callback.message, extra=extra)


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload in pricing.keys():
        db_sess = db_session.create_session()
        q = db_sess.query(users.Users).filter_by(user_id=message.from_user.id)
        q.update({'subscribe_type': message.successful_payment.invoice_payload})
        db_sess.commit()
        await bot.send_message(message.from_user.id, 'You have subscribed')
        extra = {
            'user': message.from_user.username,
            'user_id': message.from_user.id,
            'content_type': 'subscribed'
        }
        logger_message.info(message, extra=extra)


async def check_sub(callback: types.CallbackQuery):
    await callback.answer()
    db_sess = db_session.create_session()
    q = db_sess.query(users.Users).filter_by(user_id=callback.from_user.id).first()
    if q.subscribe_type is None:
        await callback.message.answer('Subscription is not active', reply_markup=get_goto_subscribe())
    else:
        await callback.message.answer('Your subscription level: {}'.format(q.subscribe_type))
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'check subscribe'
    }
    logger_message.info(callback.message, extra=extra)


async def push_cancel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer('You have unsubscribed\nA subscription is required for further work with the bot')
    extra = {
        'user': callback.from_user.username,
        'user_id': callback.from_user.id,
        'content_type': 'cancel subscribe'
    }
    logger_message.info(callback.message, extra=extra)
