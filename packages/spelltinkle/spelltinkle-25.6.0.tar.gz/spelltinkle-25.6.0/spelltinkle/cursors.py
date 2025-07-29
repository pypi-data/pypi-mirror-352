from .input import InputHandler


class CursorsMode(InputHandler):
    def __init__(self, doc, add_cursor=True):
        self.doc = doc
        self.view = doc.view
        self.known = {'delete', 'bs', 'end', 'home'}
        if add_cursor:
            self.cursor()

    def insert_character(self, char: str):
        if 'left' not in self.known:
            self.known.update(['left', 'right'])
        self.multi(lambda: self.doc.insert_character(char))

    def multi(self, function):
        cursors = set()
        for pos in self.view.cursors:
            self.view.pos = pos
            function()
            cursors.add(self.view.moved)
        self.view.cursors = cursors
        self.view.pos = max(cursors)

    def unknown(self, name):
        if name in self.known:
            return self.multi(getattr(self.doc, name))

        return getattr(self.doc, name)()

    def esc(self):
        self.view.cursors.clear()
        self.doc.handler = None
        self.view.move(*self.view.pos)

    def cursor(self):
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            if c1 != c2:
                return
            for r in range(r1, r2 + 1):
                line = self.doc.lines[r]
                if c1 < len(line):
                    self.view.cursors.add((r, c1))
            self.view.mark = None
            return

        pos = self.view.pos
        if pos in self.view.cursors:
            self.view.cursors.remove(pos)
        else:
            self.view.cursors.add(pos)
        if not self.view.cursors:
            self.doc.handler = None
