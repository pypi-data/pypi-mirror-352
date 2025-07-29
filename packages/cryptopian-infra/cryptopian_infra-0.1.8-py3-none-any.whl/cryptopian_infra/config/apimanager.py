import json
from typing import Dict

from onepasswordconnectsdk.models import Item

from .secretmanagerbase import SecretManagerBase, SecretMetadata

READONLY_API_LABEL = 'READONLY API'
TRADE_API_LABEL = 'TRADE API'


class Api:
    def __init__(self, apiKey=None, secret=None, password=None):
        self.apiKey = apiKey
        self.secret = secret
        self.password = password


class ApiItem(SecretMetadata):
    def __init__(self, metadata: dict, api_lookup: Dict[str, dict]):
        self._metadata = metadata
        self.api_lookup = api_lookup

    def metadata(self):
        return self._metadata

    def get_api(self, section_header) -> dict:
        return self.api_lookup.get(section_header, {})

    @property
    def readonly_api(self) -> Api:
        return Api(**self.get_api(READONLY_API_LABEL))

    @property
    def trade_api(self) -> Api:
        return Api(**self.get_api(TRADE_API_LABEL))

    def __repr__(self):
        return json.dumps(self._metadata)

    def __str__(self):
        return repr(self)


class ApiManager(SecretManagerBase[ApiItem]):
    def __init__(self):
        super().__init__()

    def tag_filter(self):
        return 'api'

    def process_item(self, item: Item) -> ApiItem:
        section_lookup = SecretManagerBase.get_section_lookup(item)

        metadata = {}
        api_lookup = {}

        for field in item.fields:
            if field.id == 'username':
                metadata['username'] = field.value
            elif field.section is not None:
                section_id = field.section.id
                if section_id in section_lookup:
                    section_label = section_lookup[section_id]
                    if section_label == 'METADATA':
                        metadata[field.label] = field.value
                    else:
                        if section_label not in api_lookup:
                            api_lookup[section_label] = {}
                        api_lookup[section_label][field.label] = field.value
        return ApiItem(metadata, api_lookup)
