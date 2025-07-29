from .input import InputHandler


class MoveToCharacter(InputHandler):
    def __init__(self, doc):
        self.session = doc.session
        self.doc = doc

    def insert_character(self, char):
        r, c = self.doc.view.pos
        for r, line in enumerate(self.doc.lines[r:], start=r):
            c = line.find(char, c)
            if c != -1:
                self.doc.view.move(r, c)
                break
            c = 0
        self.doc.handler = None

    def unknown(self, name):
        self.doc.handler = None
        return getattr(self.doc, name)()
