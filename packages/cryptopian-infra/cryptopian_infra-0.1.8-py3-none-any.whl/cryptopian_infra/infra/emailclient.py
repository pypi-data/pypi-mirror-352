import smtplib  # https://docs.python.org/2/library/smtplib.html
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import cached_property
from os.path import basename
from typing import List


class EmailClientDummy:
    def __init__(self):
        pass

    def sendmail(self, from_address: str, to_addresses, subject: str, body: str, file_attachments: List[str] = None):
        pass


class EmailClient:
    def __init__(self, email_client_config: dict):
        self.config = email_client_config

    @cached_property
    def email_client(self):
        return self.__create_email_client(self.config)

    @staticmethod
    def __create_email_client(config):
        email_client = smtplib.SMTP_SSL(config['host'], config['port'])
        auth = config['auth']
        email_client.login(auth['user'], auth['pass'])
        return email_client

    def send_raw_message(self, to_addresses, message):
        message['To'] = self.join_to_addresses(to_addresses)
        self.email_client.send_message(message)

    def sendmail(self, from_address: str, to_addresses, subject: str, body: str, file_attachments: List[str] = None):
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = self.join_to_addresses(to_addresses)
        msg['Subject'] = subject
        body = MIMEText(body)
        msg.attach(body)

        for f in file_attachments or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=basename(f))
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        try:
            self.email_client.send_message(msg)
        except smtplib.SMTPServerDisconnected:
            del self.email_client
            self.email_client.send_message(msg)

    @staticmethod
    def join_to_addresses(to_addresses):
        if type(to_addresses) is list:
            to_addresses = ','.join(to_addresses)
        return to_addresses
