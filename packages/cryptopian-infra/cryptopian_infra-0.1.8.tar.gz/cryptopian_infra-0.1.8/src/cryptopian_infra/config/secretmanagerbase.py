from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from onepasswordconnectsdk import new_client_from_environment
from onepasswordconnectsdk.client import Client
from onepasswordconnectsdk.models import Item


class SecretMetadata(ABC):
    @abstractmethod
    def metadata(self) -> dict:
        """
        Secret item metadata for filtering.
        Section Label: METADATA + username
        !!! Make sure it does not contain password !!!
        :return: dict
        """
        pass

    def __repr__(self):
        return repr(self.metadata())

    def __str__(self):
        return repr(self)

    def match_filter(self, **kwargs):
        metadata = self.metadata()
        for key, value in kwargs.items():
            if key not in metadata or not value == metadata[key]:
                return False
        return True


S = TypeVar('S', bound=SecretMetadata)


class SecretItem(SecretMetadata):
    def __init__(self, metadata: dict):
        self._metadata = metadata

    def metadata(self) -> dict:
        return self._metadata


class SecretManagerBase(ABC, Generic[S]):
    def __init__(self):
        # creating client using OP_CONNECT_TOKEN and OP_CONNECT_HOST environment variables
        self.client: Client = new_client_from_environment()

    def find_all(self):
        return self.find()

    def find(self, **metadata_filter):
        return self.__find(False, **metadata_filter)

    def __find(self, find_one, **metadata_filter):
        results = []
        vaults = self.client.get_vaults()
        for vault in vaults:
            vault_items = self.client.get_items(vault.id)
            for vault_item in vault_items:
                item = self.client.get_item(vault_item.id, vault.id)
                if item.tags is not None and self.tag_filter() in item.tags:
                    secret_item = self.process_item(item)
                    if secret_item is not None and secret_item.match_filter(**metadata_filter):
                        results.append(secret_item)
                        if find_one:
                            return results
        return results

    def find_one(self, **metadata_filter):
        results = self.__find(True, **metadata_filter)
        if len(results) > 0:
            return results[0]

    @staticmethod
    def get_section_lookup(item: Item) -> dict:
        section_lookup = {}
        if item.sections:
            for section in item.sections:
                if section.label is not None:
                    section_lookup[section.id] = section.label
        return section_lookup

    @abstractmethod
    def tag_filter(self):
        pass

    @abstractmethod
    def process_item(self, item) -> S:
        pass
