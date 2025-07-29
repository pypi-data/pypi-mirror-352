from .input import InputHandler


class ResizeMode(InputHandler):
    def __init__(self, doc):
        self.doc = doc
        self.size = doc.session.scr.size
        self.original_size = self.size

    def resize(self, dw=0, dh=0, reset=False):
        if reset:
            w, h = self.original_size
        else:
            w, h = self.size
            w += dw
            h += dh
        self.size = (w, h)
        print(f'\x1b[8;{h};{w}t')
        self.doc.session.resize()

    def home(self):
        self.resize(reset=True)

    def up(self):
        self.resize(dh=-1)

    def down(self):
        self.resize(dh=1)

    def left(self):
        self.resize(dw=-1)

    def right(self):
        self.resize(dw=1)

    def unknown(self, key):
        self.doc.handler = None
        return getattr(self.doc, key)()
