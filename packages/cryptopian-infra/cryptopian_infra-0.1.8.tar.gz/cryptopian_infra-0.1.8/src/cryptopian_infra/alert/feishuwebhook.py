from .alert import Channel
import requests


class FeishuWebhook(Channel):
    def __init__(self, webhook_url):
        super().__init__('feishu')
        self.webhook_url = webhook_url

    def post_msg(self, msg, **kwargs):
        payload = {
            "msg_type": "text",
            "content": {
                "text": msg
            }
        }
        response = requests.post(self.webhook_url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to send message: {response.text}")
        return response.json()
