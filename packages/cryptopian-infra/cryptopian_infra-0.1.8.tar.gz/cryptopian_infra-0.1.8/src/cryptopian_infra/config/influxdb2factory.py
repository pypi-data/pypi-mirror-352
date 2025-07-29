import logging
from enum import Enum
from typing import List

from influxdb_client import InfluxDBClient
from onepasswordconnectsdk.models import Item

from .secretmanagerbase import SecretManagerBase, SecretMetadata
from ..utils.dictobj import DictObj


class InfluxPermission(Enum):
    read = 0
    write = 1
    readWrite = 2
    admin = 3


class InfluxToken(DictObj):
    def __init__(self, token: str, permission: InfluxPermission | str, bucket: str = None):
        self.token = token
        if isinstance(permission, InfluxPermission):
            self.permission = permission
        else:
            self.permission = InfluxPermission[permission]
        self.bucket = bucket


class Influxdb2SecretItem(SecretMetadata):
    def __init__(self, url: str, org: str, username: str, password: str, tokens: List[InfluxToken]):
        self.url = url
        self.org = org
        self.username = username
        self.password = password
        self.tokens = tokens

    def metadata(self):
        md = dict(self.__dict__)
        del md['password']
        return md

    def get_token(self, permission: InfluxPermission, bucket: str = None) -> InfluxToken:
        for token in self.tokens:
            if token.bucket == bucket and token.permission == permission:
                return token

    def match_filter(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'org':
                if self.org != value:
                    return False
            elif key == 'bucket':
                if not any(token.bucket == value for token in self.tokens):
                    return False
            elif key == 'permission':
                if not any(token.permission == value for token in self.tokens):
                    return False
        return True


class Influxdb2Factory(SecretManagerBase[Influxdb2SecretItem]):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__class__.__name__)

    def tag_filter(self):
        return 'DB/InfluxDB2'

    def process_item(self, item: Item):
        section_lookup = SecretManagerBase.get_section_lookup(item)
        url = None
        org = None
        username = None
        password = None
        token_sections = {}
        for field in item.fields:
            if field.label == 'url':
                url = field.value
            elif field.label == 'org':
                org = field.value
            elif field.id == 'username':
                username = field.value
            elif field.id == 'password':
                password = field.value
            elif field.section is not None:
                section_id = field.section.id
                if section_id in section_lookup:
                    if section_id not in token_sections:
                        token_sections[section_id] = {}
                    token_sections[section_id][field.label] = field.value
        tokens = [InfluxToken(**token) for token in token_sections.values()]
        return Influxdb2SecretItem(url=url, org=org, username=username, password=password, tokens=tokens)

    def find_item(self, org: str, permission: InfluxPermission, bucket: str = None) -> Influxdb2SecretItem:
        return self.find_one(org=org, bucket=bucket, permission=permission)

    def create_influxdb_client_admin(self, org: str) -> InfluxDBClient:
        item = self.find_item(org=org, permission=InfluxPermission.admin)
        if item:
            token = item.get_token(InfluxPermission.admin)
            self.logger.info(f'Creating admin InfluxDBClient username={item.username}...')
            return InfluxDBClient(url=item.url, token=token.token, org=item.org, timeout=60_000)

    def create_influxdb_client(self, org: str, bucket: str, permission: InfluxPermission) -> InfluxDBClient:
        item = self.find_item(org, permission, bucket)
        if item:
            self.logger.info(f'Creating InfluxDBClient for bucket={bucket}...')
            token = item.get_token(permission, bucket)
            return InfluxDBClient(url=item.url, token=token.token, org=item.org, timeout=60_000)
