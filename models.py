import pymongo

import settings


class MyMongoDB:
    def __init__(
            self,
            db_name: str = settings.DB_NAME,
            collection_name: str = settings.DEFAULT_COLLECTION_NAME,
            host: str = settings.DB_HOST,
            port: int = 27017
    ):
        self.connect = pymongo.MongoClient(f'mongodb://{host}:{port}/', )
        self.db = self.connect[db_name]
        self.collection = self.db[collection_name]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connect.close()

    def save_card_info(self, document: dict):
        return self.collection.insert_one(document=document)

    def get_card_info_by_id(self, _id):
        return self.collection.find_one({'_id': _id})

    def get_all_names_and_ids(self):
        return list(map(
            lambda x:
            {
                'name': x.get('name'),
                '_id': x.get('_id')
            }, self.collection.find()))

    def remove_card_info_by_id(self, _id):
        return self.collection.delete_one({'_id': _id})

    def is_name_uniqueness(self, name: str):
        return True if self.collection.count_documents({'name': name}) == 0 else False
