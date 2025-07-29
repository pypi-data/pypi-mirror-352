# type: ignore

"""
jj jensj@fysik.dtu.dk Jens Jørgen Mortensen
jj jj@smoerhul.dk Jens Jørgen Mortensen
nm

from, to(s), time, size, attachments?, title, summary, replied?, forwarded?
"""

from spelltinkle.color import Color
from spelltinkle.document import Document
# from spelltinkle.input import Input
from spelltinkle.text import TextDocument


class MailDocument(Document):
    def __init__(self):
        Document.__init__(self)
        self.color = Color()
        # M.logout()

    def set_session(self, session):
        Document.set_session(self, session)
        # self.list()
        self.changes = 42

    def list(self):
        # self.color.colors = colors = []

        # self.change(0, 0, len(self.lines) - 1, 0, lines2)
        self.view.move(0, 0)

    def enter(self):
        for i, doc in enumerate(self.session.docs):
            if doc.filename == self.conf.calender_file:
                self.session.docs.append(self.session.docs.pop(i))
                return
        doc = TextDocument()
        doc.read(self.conf.calender_file, self.session.read())
        return doc


def mail(event):
    import smtplib
    from email.mime.text import MIMEText
    subject = f'{event.start}: {event.text}'
    msg = MIMEText('bla')
    msg['Subject'] = subject
    to = 'jensj@fysik.dtu.dk'
    msg['From'] = to
    msg['To'] = to
    s = smtplib.SMTP('mail.fysik.dtu.dk')
    s.sendmail(msg['From'], [to], msg.as_string())
    s.quit()
