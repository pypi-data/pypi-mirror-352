from ..color import Color
from ..document import Document
from ..session import Session
from .addresses import create_addresses
from spelltinkle.mail.server import create_mail_server


class MailFolderDocument(Document):
    def __init__(self,
                 name: str,
                 session: Session,
                 folder: str = 'INBOX'):
        Document.__init__(self)
        self.name = name
        self.session = session
        self.folder = folder

        self.addresses = create_addresses(
            session.conf.home / 'mail/addresses.csv')

        self.server = create_mail_server(name, session.conf)
        uids, self.folders = self.server.folder(folder)
        self.mails = self.server.mails(uids)
        self.uids: list[str] = []
        self.color = Color()
        self.list()

    def list(self):
        # self.color.colors = colors = []

        lines = []
        for mail in self.mails.values():
            fro = self.addresses.short_name(mail.fro)
            to = ','.join(self.addresses.short_name(t) for t in mail.to)
            subject = mail.subject.replace('\r\n', ' ')
            line = f'{mail.date_string} {fro}->{to} {subject}'
            lines.append(line)
            self.uids.append(mail.uid)

        if lines:
            self.change(0, 0, 0, 0, lines)
        self.view.move(0, 0)

    def insert_character(self, char: str) -> None:
        if char == 'r':
            self.refresh()

    def refresh(self):
        uids, mails, self.folders = self.server.refresh(
            self.mails, self.folder)
        self.mails = {uid: self.mails.get(uid, mails.get(uid))
                      for uid in uids}
        self.list()

    def enter(self):
        self.server.text(self.folder, self.uids[0], 1)
