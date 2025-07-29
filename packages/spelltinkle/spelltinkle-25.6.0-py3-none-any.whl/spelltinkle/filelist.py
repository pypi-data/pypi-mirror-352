from typing import Dict

from .document import Document


class FileList(Document):
    def __init__(self) -> None:
        Document.__init__(self)
        self.name = '[list]'
        self.mail: Dict[str, str] = {}

    def set_session(self, session):
        Document.set_session(self, session)
        lines = [doc.name for doc in session.docs[::-1]]
        for key, name in zip('mM', session.conf.mail):
            lines.append(f'MAIL: {name}')
            self.mail[key] = name
        self.change(0, 0, 0, 0, lines + [''])
        self.view.move(2, 0)
        "save Saveall quit/del/bs enter copy open esc"

    def insert_character(self, char):
        if char.isdigit():
            i = int(char)
            if 0 < i < len(self.session.docs):
                return self.choose(i)
            else:
                char = 'mM'[i - len(self.session.docs)]
        if char == 'q':
            r = self.view.r
            doc = self.session.docs[-(r + 2)]
            if doc.modified:
                return
            doc.quit()
            self.change(r, 0, r + 1, 0, [''])

        if char == 'c':
            from spelltinkle.calender import CalenderDocument
            self.session.docs.pop()
            return CalenderDocument(self.session.conf.calender_file)
        if char in 'mM':
            from spelltinkle.mail.folder import MailFolderDocument
            self.session.docs.pop()
            name = self.mail[char]
            return MailFolderDocument(name, self.session)

    def choose(self, i):
        self.session.docs.pop()
        return self.session.docs.pop(-i)

    def enter(self):
        return self.choose(self.view.r + 1)

    def esc(self):
        return self.choose(1)

    def view_files(self):
        return self.insert_character('2')
