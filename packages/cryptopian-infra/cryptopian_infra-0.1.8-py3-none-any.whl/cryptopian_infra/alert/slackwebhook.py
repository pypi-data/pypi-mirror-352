import json
import logging
from socket import timeout
from urllib.error import URLError
from urllib.request import Request, urlopen

from .alert import Channel


class SlackWebhook(Channel):
    def __init__(self, channel: str, url: str):
        super().__init__("slack")
        self.url = url
        self.channel = channel
        self.timeout_error = False

    def post_msg(self, msg, **kwargs):
        """

        :param msg:
        :param kwargs: override any parameters if necessary
        :return:
        """
        if self.timeout_error:
            return None
        args = {
            "text": msg,
            "channel": self.channel
        }
        args.update(kwargs)

        try:
            return self.__send(args)
        except URLError as ue:
            if isinstance(ue.reason, timeout):
                logging.warning("Timeout error detected! Disable sending slack messages.")
                self.timeout_error = True
                return None
            else:
                raise

    def __send(self, args):
        data = json.dumps(args).encode()
        req = Request(self.url, data=data, headers={"Content-type": "application/json"}, method="POST")
        return urlopen(req, timeout=1).read().decode()
