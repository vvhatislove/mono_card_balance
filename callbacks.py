from bson import ObjectId
from telebot import types, TeleBot

from models import MyMongoDB
from mono_requests import MonoRequest


def account_balance(bot: TeleBot, callback: types.CallbackQuery):
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text='Sending request...'
    )
    _id = ObjectId(callback.data.split('_')[1])
    with MyMongoDB() as db:
        account = db.get_card_info_by_id(_id=_id)
    mono = MonoRequest(account.get('token'),
                       account.get('card_type'))
    mono_response = mono.get_balance_from_mono()
    if mono_response.balance is None:
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.id,
            text=f'Something went wrong, couldn\'t get balance from Monobank!\n\n'
                 f'Error: {mono_response.error}\n'
                 f'Status code: {mono_response.status_code}\n\n'
                 f'Maybe it\'s because there is an air raid alert in your area.'
        )
        return
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=f"Name: {account.get('name')}\n"
             f"Card type: {account.get('card_type')}\n"
             f"Баланс: {mono_response.balance}₴"
    )


def delete_account(bot: TeleBot, callback: types.CallbackQuery):
    _id = ObjectId(callback.data.split('_')[1])
    with MyMongoDB() as db:
        name = db.get_card_info_by_id(_id=_id).get('name')
        db.remove_card_info_by_id(_id=_id)
    bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        text=f'"{name}" card removed'
    )
