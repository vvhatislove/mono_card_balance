import telebot
from telebot import types

import settings
from callbacks import account_balance, delete_account
from models import MyMongoDB
from mono_requests import MonoRequest
from utils import get_existing_accounts, no_accounts_message

bot = telebot.TeleBot(settings.BOT_API_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message: types.Message):
    if message.chat.id not in settings.ALLOWED_IDS:
        return
    bot.send_message(
        chat_id=message.chat.id,
        text='Hello, the bot for checking '
             'the balance of monobank '
             'cards is ready to go!')


@bot.message_handler(commands=['accounts'])
def accounts_command(message: types.Message):
    if message.chat.id not in settings.ALLOWED_IDS:
        return
    accounts = get_existing_accounts()
    if accounts is None:
        no_accounts_message(bot, message)
        return
    markup = types.InlineKeyboardMarkup()
    for account in accounts:
        markup.add(types.InlineKeyboardButton(
            text=account.get('name'),
            callback_data='check_' + str(account.get('_id'))
        ))
    bot.send_message(
        chat_id=message.chat.id,
        text='📖Choose an account',
        reply_markup=markup
    )


@bot.message_handler(commands=['add_account'])
def add_account_command(message: types.Message):
    if message.chat.id not in settings.ALLOWED_IDS:
        return
    send = bot.send_message(
        chat_id=message.chat.id,
        text='🆕Send the name that you want to see on the button, like "Vasya Pupkin"\n\n'
             'PS. Without quotes, and make names unique!\n'
             'Write "cancel" to cancel the addition')
    bot.register_next_step_handler(send, get_name_step)


def get_name_step(message: types.Message):
    if message.text == 'cancel':
        bot.send_message(
            chat_id=message.chat.id,
            text='Canceled'
        )
        return
    name = message.text
    if '"' in name or "'" in name:
        send = bot.send_message(
            chat_id=message.chat.id,
            text='Please enter a name without quotes'
        )
        bot.register_next_step_handler(send, get_name_step)
    else:
        with MyMongoDB() as db:
            is_name_uniqueness = db.is_name_uniqueness(name)
        if not is_name_uniqueness:
            send = bot.send_message(
                chat_id=message.chat.id,
                text='Please send a unique name'
            )
            bot.register_next_step_handler(send, get_name_step)
        else:
            send = bot.send_message(
                chat_id=message.chat.id,
                text='Great, now send me the token\nWrite "cancel" to cancel the addition'
            )
            bot.register_next_step_handler(send, get_token_step, name=name)
            bot.send_message(
                chat_id=message.chat.id,
                text='MESSAGES CONTAINING THE TOKEN WILL BE DELETED AFTER PROCESSING!')


def get_token_step(message: types.Message, name: str):
    if message.text == 'cancel':
        bot.send_message(message.chat.id, 'Canceled')
        return
    token = message.text
    try:
        is_status_code_200 = MonoRequest(token).is_status_cod_200()
    except UnicodeEncodeError:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
        send = bot.send_message(
            chat_id=message.chat.id,
            text='The token must contain only English characters.\n'
                 'Write the correct token or write "cancel" to cancel the addition')
        bot.register_next_step_handler(send, get_token_step, name=name)
    else:
        if not is_status_code_200:
            send = bot.send_message(
                chat_id=message.chat.id,
                text='Invalid token. Please send a valid token or write "cancel" to cancel the addition'
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            bot.register_next_step_handler(send, get_token_step, name=name)
        else:
            send = bot.send_message(
                chat_id=message.chat.id,
                text='Great, now send me the card type: "black" or "white"'
            )
            bot.delete_message(chat_id=message.chat.id, message_id=message.id)
            bot.register_next_step_handler(send, get_card_type_step, name=name, token=token)


def get_card_type_step(message: types.Message, name: str, token: str):
    if message.text == 'cancel':
        bot.send_message(message.chat.id, 'Canceled')
        return
    card_type = message.text
    if card_type not in ('black', 'white'):
        send = bot.send_message(chat_id=message.chat.id,
                                text='Card type must be "black" or "white".\n'
                                     'Submit the correct card type or write "cancel" to cancel the addition'
                                )
        bot.register_next_step_handler(send, get_card_type_step, name=name, token=token)
    else:
        with MyMongoDB() as db:
            db.save_card_info({
                'name': name,
                'token': token,
                'card_type': card_type
            })
        bot.send_message(message.chat.id, 'Saved, see /accounts')


@bot.message_handler(commands=['delete_account'])
def delete_account_command(message: types.Message):
    if message.chat.id not in settings.ALLOWED_IDS:
        return
    accounts = get_existing_accounts()
    if accounts is None:
        no_accounts_message(bot, message)
        return
    markup = types.InlineKeyboardMarkup()
    for account in accounts:
        markup.add(types.InlineKeyboardButton(
            text=account.get('name'),
            callback_data='delete_' + str(account.get('_id')))
        )
    bot.send_message(
        chat_id=message.chat.id,
        text='🗑️Select an account to delete',
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda callback: callback.data)
def callbacks(callback: types.CallbackQuery):
    if 'check' in callback.data:
        account_balance(bot, callback)
    elif 'delete' in callback.data:
        delete_account(bot, callback)
