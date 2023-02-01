import os

import dotenv

dotenv.load_dotenv('.env')

DB_NAME = 'db'
BOT_API_TOKEN = os.getenv('BOT_API_TOKEN')
ALLOWED_IDS = tuple(map(int, os.getenv('ALLOWED_IDS').split()))
DB_HOST = os.getenv('DB_HOST', default='localhost')
DEFAULT_COLLECTION_NAME = 'cards'
