import logging
import os
from enum import Enum

from onepasswordconnectsdk.models import Item
from pymongo import MongoClient

from .secretmanagerbase import SecretManagerBase, SecretMetadata
from ..mongo.mongoparameters import MongoParameters


class MongoPrivilege(Enum):
    read = 0
    readWrite = 1
    root = 2


class MongoSecretItem(SecretMetadata):
    def __init__(self, server: str, port, username: str, password: str, Environment: str, database: str = None,
                 **kwargs):
        self.server = server
        self.port = int(port)
        self.username = username
        self.password = password
        self.environment = Environment
        self.database = database
        self.privilege = MongoPrivilege[kwargs['database permission']]

    def metadata(self):
        md = dict(self.__dict__)
        del md['password']
        return md


class MongoFactory(SecretManagerBase[MongoSecretItem]):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)

    def tag_filter(self):
        return 'DB/Mongo'

    def process_item(self, item: Item):
        metadata = {}
        for field in item.fields:
            if field.value is not None:
                metadata[field.label] = field.value
        return MongoSecretItem(**metadata)

    def find_item(self, database, privilege: MongoPrivilege) -> MongoSecretItem | None:
        items = self.find(database=database)
        items.sort(key=lambda i: i.privilege.value, reverse=False)
        for item in items:
            if item.privilege.value >= privilege.value:
                return item
        return None

    def create_mongo_db(self, database, privilege: MongoPrivilege = MongoPrivilege.read):
        mongo_host = os.environ.get('MONGO_HOST')
        if mongo_host is not None:
            self.logger.info(f'Creating MongoClient for database={database} from environment variables...')
            mongo_port = int(os.environ.get('MONGO_PORT', 27017))
            mongo_username = os.environ.get('MONGO_USERNAME')
            mongo_password = os.environ.get('MONGO_PASSWORD')
            client = MongoClient(host=mongo_host,
                                 port=mongo_port,
                                 username=mongo_username,
                                 password=mongo_password)
            return client[database]

        item = self.find_item(database, privilege)
        if item:
            self.logger.info(f'Creating MongoClient for database={database} from secret manager...')
            client = MongoClient(host=item.server,
                                 port=item.port,
                                 username=item.username,
                                 password=item.password)
            return client[item.database]
        else:
            raise KeyError(f'Unable to find database={database}')

    def create_mongo_parameters(self, database, collection_name, privilege: MongoPrivilege = MongoPrivilege.readWrite):
        mongo_db = self.create_mongo_db(database=database, privilege=privilege)
        return MongoParameters(mongo_db, collection_name)
