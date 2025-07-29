from .input import Input


class Command(Input):
    def __init__(self, doc):
        self.doc = doc
        self.view = doc.view
        Input.__init__(self)

    def update(self, string=None):
        Input.update(self, string)
        self.view.message = self.string
        self.view.update_info_line()

    def enter(self):
        s = self.string
        if not s:
            return
        try:
            line_number = int(s)
        except ValueError:
            pass
        else:
            self.view.move(line_number - 1, 0)
            self.doc.handler = None
            return

        if s[:1] == '/':
            if s[1:2] == '/':
                regex = True
                s = s[1:]
            else:
                regex = False
            find, replace = s[1:].split('/')
            from .replace import Replace
            self.doc.handler = Replace(self.doc, find, replace, regex)
