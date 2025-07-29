from typing import Optional

from .alert.alert import Channel
from .alert.alertwrapper import AlertWrapper

alert_wrapper: Optional[AlertWrapper] = None


def setup_alert(alias, channel: Channel, check_duplicated_message=True):
    global alert_wrapper

    alert_wrapper = AlertWrapper(alias, channel, check_duplicated_message)
    alert_wrapper.send_alert(f'{alias} started.', type_='INFO')


def create_sub_alert(alias: str):
    global alert_wrapper
    if alert_wrapper:
        return AlertWrapper(alias, alert_wrapper.alert_channel)
    else:
        raise Exception('AlertWrapper not initialized')


def send_alert(message, error=None, type_='ERROR', alias=None):
    global alert_wrapper
    if alert_wrapper:
        return alert_wrapper.send_alert(message, error, type_, alias)
    else:
        return AlertWrapper.log_msg_error(alias, message, error, type_)
