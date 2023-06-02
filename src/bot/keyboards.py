from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.callbacks import cb_payload


def get_pay():
    keyboard = InlineKeyboardMarkup()
    btn_basic = InlineKeyboardButton('Basic subscribe', callback_data=cb_payload.new('basic'))
    btn_premium = InlineKeyboardButton('Premium subscribe', callback_data=cb_payload.new('premium'))
    btn_vip = InlineKeyboardButton('Vip subscribe', callback_data=cb_payload.new('vip'))
    btn_cancel = InlineKeyboardButton('Отмена', callback_data='cancel')
    keyboard.add(btn_basic, btn_premium, btn_vip, btn_cancel)
    return keyboard


def get_check_subscribe():
    keyboard = InlineKeyboardMarkup()
    btn_check = InlineKeyboardButton('Check your subscription', callback_data='check')
    keyboard.add(btn_check)
    return keyboard
