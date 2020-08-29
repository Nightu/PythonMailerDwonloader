# %%
from json import dumps, dump, loads
from os import remove, path, makedirs, chown, getenv, walk
from ssl import create_default_context
from datetime import date, datetime
from re import sub

from imap_tools import MailBox, AND
from certifi.core import where
from MgmtModules.LoggerConfig import LoggerConfig


class ImapConnector:

    def __init__(self):
        self.logger = LoggerConfig().logger(ImapConnector.__name__)
        self.ssl_context = create_default_context(cafile=where())
        self.mail_json_loader = {}
        self.mailer_path = '/python_mailer'
        self.debug_file = f'{self.mailer_path}/debug.json'
        self.current_date = datetime.now()

    def __connect_to_mailbox(self, mail_user: str, mail_passwd: str, mailbox_host: str, mailbox_port: int,
                             mailbox_use_ssl: bool) -> MailBox:
        if mailbox_use_ssl:
            mailbox = MailBox(host=mailbox_host, port=mailbox_port, ssl_context=self.ssl_context)
        else:
            mailbox = MailBox(host=mailbox_host, port=mailbox_port)
        mailbox.login(username=mail_user, password=mail_passwd)

        try:
            if status := mailbox.login_result[0] == "OK":
                self.logger.info(f"Successfully connect to mailbox: {status}")
                return mailbox
        except Exception as e:
            self.logger.warning(f"There was problem with connecting to mailbox: {e}")

    def search_for_email_with_criteria(self, mailbox: MailBox, use_debug: bool, init_mail_download: bool = False):
        if init_mail_download:
            search_for_mail = mailbox.fetch()
            with open('/opt/mailer_daemon/config.json', 'r') as f:
                lines = f.readlines()
            with open("/opt/mailer_daemon/config.json", "w") as f:
                for line in lines:
                    if "mailbox_init_download" not in line:
                        f.write(line)
        else:
            search_for_mail = mailbox.fetch(AND(date=(date(
                year=self.current_date.year, month=self.current_date.month, day=self.current_date.day))))
        for message in search_for_mail:
            self.mail_json_loader[message.uid] = {
                'headers': message.headers,
                'subject': message.subject,
                'from': message.from_,
                'to': message.to,
                'content': message.text,
                'date': str(message.date.strftime('%Y-%-m-%d'))
            }

        if use_debug:
            self.logger.info(f"Debug is on, blob file is saved in {self.debug_file}")
            if path.isfile(self.debug_file):
                remove(self.debug_file)
            with open(self.debug_file, 'x') as f:
                json_file = loads(
                    dumps(self.mail_json_loader, sort_keys=True)
                        .replace('\\n', '')
                        .replace('\\r', '')
                        .replace('\\t', ''))
                dump(json_file, f)

    def change_permission(self, object_path):
        chown(object_path, 1000, 1000) if getenv('user_remap') == 'true' \
            else chown(object_path, 33, 33)

    def change_permission_by_dir(self, object_path):
        for root, subdirs, files in walk(f"{self.mailer_path}/{object_path}"):
            print(root)
            self.change_permission(root)

    def create_catalogs_with_file(self):
        self.logger.info(f'Found {len(self.mail_json_loader.keys())} emails.')
        for mail in self.mail_json_loader:
            current_processing_mail = self.mail_json_loader.get(mail)
            added_number = 0
            mail_date = current_processing_mail.get('date').split('-')
            format_subject = sub('[^0-9a-zA-Z]+', '-', current_processing_mail.get('subject')).lower()
            path_list = [f"{self.mailer_path}/timeline/{mail_date[0]}/{mail_date[1]}/{mail_date[2]}",
                         f"{self.mailer_path}/sender/{current_processing_mail.get('from')}"]
            set_current_processing_file_name = f"{current_processing_mail.get('from')}" \
                                               f"-{format_subject}{added_number}.json"
            for single_path in path_list:
                if not path.exists(single_path):
                    self.logger.info(f"Create path for: {single_path}")
                    makedirs(single_path)
                    self.logger.info(f"{single_path.split('/')[2]},{single_path.split('/')}")
                    self.change_permission_by_dir(single_path.split('/')[2])

                if path.isfile(f"{single_path}/{set_current_processing_file_name}"):
                    added_number += 1
                    set_current_processing_file_name = f"{current_processing_mail.get('from')}" \
                                                       f"-{format_subject}{added_number}.json"

                else:
                    current_file = f"{single_path}/{set_current_processing_file_name}"
                    with open(current_file, 'x') as f:
                        json_file = loads(dumps(current_processing_mail, sort_keys=True)
                                          .replace('\\n', '')
                                          .replace('\\r', '')
                                          .replace('\\t', ''))
                        dump(json_file, f)
                        self.change_permission(current_file)

    def start_parsing_mail_from_mailbox(self, __mail_user: str, __mail_passwd: str, __mailbox_host: str,
                                        __mailbox_port: int, init_mail_download: bool, __mailbox_use_ssl: bool = False,
                                        use_debug: bool = False):
        self.search_for_email_with_criteria(
            self.__connect_to_mailbox(__mail_user, __mail_passwd, __mailbox_host, __mailbox_port, __mailbox_use_ssl),
            use_debug, init_mail_download)
        self.create_catalogs_with_file()
