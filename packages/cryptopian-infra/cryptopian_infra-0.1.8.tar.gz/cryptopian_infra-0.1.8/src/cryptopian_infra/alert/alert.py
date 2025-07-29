import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, UTC
from typing import Dict


class Channel(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def post_msg(self, msg, **kwargs):
        pass


class Alert:
    def __init__(self):
        self.reminder: Dict[str, timedelta] = {}
        self.alert_sent: Dict[str, datetime] = {}
        self.channels: Dict[str, Channel] = {}

    def register_channel(self, channel: Channel):
        self.channels[channel.name] = channel

    def on_first_alert(self, topic, reminder: timedelta = None):
        if topic not in self.alert_sent:
            self.alert_sent[topic] = datetime.now(UTC)
            if reminder:
                self.reminder[topic] = reminder
            return True
        else:
            if topic in self.reminder:
                utc_now = datetime.now(UTC)
                if utc_now - self.alert_sent[topic] > self.reminder[topic]:
                    self.alert_sent[topic] = utc_now
                    return True

        return False

    def reset_alert(self, topic):
        if topic in self.alert_sent:
            del self.alert_sent[topic]
            logging.info(f"{topic} reset")

    def post_msg(self, msg, **kwargs):
        logging.info(msg)
        for name, channel in self.channels.items():
            try:
                channel.post_msg(msg, **kwargs)
            except:
                logging.exception(f'Failed to post on {name}')
