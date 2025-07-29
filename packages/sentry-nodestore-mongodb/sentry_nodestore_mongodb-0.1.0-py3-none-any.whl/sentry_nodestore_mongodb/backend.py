from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pymongo import MongoClient, ASCENDING
from sentry.nodestore.base import NodeStorage


class MongoDBNodeStorage(NodeStorage):
    __client = None
    __collection = None

    def __init__(
        self,
        connection,
        database='sentry',
        collection='nodestore',
    ):
        self.connection = connection
        self.database = database
        self.collection = collection

        super(MongoDBNodeStorage, self).__init__()

    def delete(self, id):
        self.__col.delete_one({'_id': id})

    def _get_bytes(self, id):
        response = self.__col.find_one({'_id': id})

        if response is None:
            return None

        return response['data']

    def _set_bytes(self, id, data, ttl=None):
        data = {
            '_id': id,
            'data': data,
            'timestamp': datetime.now(),
            'ttl': ttl
        }

        response = self.__col.find_one({'_id': id})

        if response is None:
            self.__col.insert_one(data)
        else:
            self.__col.replace_one({'_id': id}, data)

    def _decode(self, value: None | dict, subkey: str | None) -> Any | None:
        if value is None:
            return None

        if subkey is not None:
            return value.get('subkeys', {}).get(subkey, None)

        return value.get('data', None)

    def _encode(self, data: dict[str | None, Mapping[str, Any]]) -> dict:
        return {
            'data': data.pop(None),
            'subkeys': data
        }

    def cleanup(self, cutoff: datetime):
        self.__col.delete_many({'timestamp': {'$lt': cutoff}})

    def bootstrap(self):
        pass

    @property
    def __col(self):
        if self.__collection is None:
            if self.__client is None:
                self.__client = MongoClient(self.connection)
            self.__collection = self.__client[self.database][self.collection]
            self.__collection.create_index([("timestamp", ASCENDING)])

        return self.__collection
