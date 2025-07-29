from onepasswordconnectsdk.models import Item

from .secretmanagerbase import SecretManagerBase, SecretItem
from ..alert.slackwebhook import SlackWebhook


class SlackWebhookItem(SecretItem):
    def __init__(self, metadata: dict, channel_url_lookup: dict):
        super().__init__(metadata)
        self.channel_url_lookup = channel_url_lookup

    def get_webhook_config(self, channel: str):
        return {'channel': channel, 'url': self.channel_url_lookup[channel]}

    def match_filter(self, **kwargs):
        metadata = self.metadata()
        for key, value in kwargs.items():
            if key == 'channel':
                if value not in self.channel_url_lookup:
                    return False
            elif key not in metadata or not value == metadata[key]:
                return False
        return True


class SlackWebhookFactory(SecretManagerBase[SlackWebhookItem]):

    def __init__(self):
        super().__init__()

    def tag_filter(self):
        return 'Slack/Webhook'

    def process_item(self, item: Item):
        section_lookup = SecretManagerBase.get_section_lookup(item)

        webhook_configs = {}
        metadata = {}
        for field in item.fields:
            if field.id == 'username':
                metadata['username'] = field.value
            elif field.section is not None:
                section_id = field.section.id
                if section_id in section_lookup:
                    section_label = section_lookup[section_id]
                    if section_label == 'WEBHOOK':
                        if section_id not in webhook_configs:
                            webhook_configs[section_id] = {}
                        webhook_configs[section_id][field.label] = field.value

        channel_url_lookup = {}
        for webhook_config in webhook_configs.values():
            channel_url_lookup[webhook_config['channel']] = webhook_config['url']

        return SlackWebhookItem(metadata, channel_url_lookup)

    def create_webhook(self, channel: str):
        item = self.find_one(channel=channel)
        return SlackWebhook(**item.get_webhook_config(channel))
