from telebot import TeleBot

from models import MyMongoDB


def get_existing_accounts():
    with MyMongoDB() as db:
        accounts = db.get_all_names_and_ids()
    if not len(accounts):
        return None
    return accounts


def no_accounts_message(bot: TeleBot, message):
    bot.send_message(
        chat_id=message.chat.id,
        text='No accounts. Create one via "/add_account"'
    )
