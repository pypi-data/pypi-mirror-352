import json
import logging

from .alert import Channel
from ..threading import MessagePump


class AlertWrapper(MessagePump):
    def __init__(self, alias, alert_channel: Channel, check_duplicated_message=True):
        super().__init__(f'{alias}-Alert')
        self.alias = alias
        self.alert_channel = alert_channel
        self.check_duplicated_message = check_duplicated_message
        self.last_error = ''

    @staticmethod
    def log_msg_error(alias, message, error, type_):
        if alias is not None:
            print_msg = f"[{alias}] {message}"
        else:
            print_msg = f"{message}"

        # handle common error formatting
        if error:
            try:
                print_msg += '\n' + json.dumps(error)
            except:
                print_msg += '\n' + repr(error)

        if type_.upper() == 'ERROR':
            logging.error(print_msg)
        else:
            logging.info(type_ + ': ' + print_msg)
        return print_msg

    def handle_message(self, message):
        try:
            self.alert_channel.post_msg(message)
        except:
            logging.exception('Error sending alert')

            try:
                self.alert_channel.post_msg(message)
            except:
                logging.exception('Give up sending slack messages...')

    def send_alert(self, message, error=None, type_='ERROR', alias=None):
        should_send_alert = True
        if alias is None:
            alias = self.alias
        print_msg = self.log_msg_error(alias, message, error, type_)

        if self.last_error == print_msg:
            should_send_alert = False
        else:
            self.last_error = print_msg

        if not self.check_duplicated_message or should_send_alert:
            self.post_message(print_msg)
            return print_msg
        return None
