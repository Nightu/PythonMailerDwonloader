#!/usr/bin/python
from functools import lru_cache
from time import sleep
from json import load

from ImapConnector import ImapConnector
from MgmtModules.LoggerConfig import LoggerConfig

global use_debug


class MailerDaemon:
    def __init__(self):
        self.logger = LoggerConfig().logger(MailerDaemon.__name__)

    @lru_cache()
    def __get_data_from_json(self) -> dict:
        with open("/opt/mailer_daemon/config.json") as f:
            return load(f)


    def start_checking_mailbox(self):
        self.logger.info('Daemon is runing')
        __mailbox_user = self.__get_data_from_json().get('mailbox_user')
        __mailbox_passwd = self.__get_data_from_json().get('mailbox_passwd')
        __mailbox_host = self.__get_data_from_json().get('mailbox_host')
        __mailbox_port = int(self.__get_data_from_json().get('mailbox_port'))
        __mailbox_init_download = bool(self.__get_data_from_json().get('mailbox_init_download'))
        __mailbox_use_ssl = bool(self.__get_data_from_json().get('mailbox_use_ssl'))
        __use_debug = bool(self.__get_data_from_json().get('use_debug'))
        self.logger.info('Start checking for email')
        while True:
            if __mailbox_use_ssl:
                self.logger.info("Init is on, download whole mailbox.")
                ImapConnector().start_parsing_mail_from_mailbox(
                    __mailbox_user, __mailbox_passwd, __mailbox_host, __mailbox_port, __mailbox_init_download,
                    __mailbox_use_ssl, __use_debug)
                __mailbox_use_ssl = False
                sleep(5)
            else:
                ImapConnector().start_parsing_mail_from_mailbox(
                    __mailbox_user, __mailbox_passwd, __mailbox_host, __mailbox_port, __use_debug)
                sleep(5)


if __name__ == '__main__':
    MailerDaemon().start_checking_mailbox()
