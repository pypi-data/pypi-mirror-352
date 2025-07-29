import os
import re
import subprocess
import textwrap
from functools import cached_property
from pathlib import Path
from typing import Callable, List, Optional

from .complete import complete_word
from .document import Document
from .keys import aliases, typos, unicode_aliases
from .utils import convert_dict_syntax, tolines


class TextDocument(Document):
    completions = None

    def insert_character(self, char) -> None:
        r, c = self.view.pos
        for key in typos:
            if self.session.chars.endswith(key):
                self.change(r, c - len(key) + 1, r, c, [typos[key]])
                self.session.chars = ''
                return

        self.change(r, c, r, c, [char])
        self.completion.run(self, r, c, self.session.loop)

    def mouse2_clicked(self) -> None:
        x, y = self.session.scr.position
        if y == 0:
            return
        r, c = self.view.mouse(x, y)
        try:
            txt = subprocess.check_output(['xclip', '-o'])
        except FileNotFoundError:
            txt = self.session.xclip
        lines, _ = tolines(line + '\n' for line in txt.decode().split('\n'))
        self.change(r, c, r, c, lines[:-1])
        self.view.mark = None

    def bs(self) -> None:
        r2, c2 = self.view.pos
        if self.lines[r2][:c2].isspace():
            c1 = (c2 - 1) // 4 * 4
            r1 = r2
        else:
            r1, c1 = self.view.prev()
        self.change(r1, c1, r2, c2, [''])

    def swap(self) -> None:
        r, c = self.view.pos
        ab = self.lines[r][c - 1:c + 1]
        if len(ab) == 2:
            self.change(r, c - 1, r, c + 1, [ab[::-1]])

    def upper(self, func: Callable[[str], str] = str.upper) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            self.view.mark = None
        else:
            r1, c1 = self.view.pos
            r2, c2 = self.view.next()
        lines = self.change(r1, c1, r2, c2, [''])
        self.change(r1, c1, r1, c1, [func(line) for line in lines])

    def lower(self) -> None:
        self.upper(str.lower)

    def toggle_f_string(self) -> None:
        r, c0 = self.view.pos
        line = self.lines[r]
        c = c0 - 1
        while c >= 0:
            if line[c] == "'":
                break
            c -= 1
        else:  # no break
            return

        if c == 0 or line[c - 1] != 'f':
            self.change(r, c, r, c, ['f'])
            self.view.move(r, c0 + 1)
        else:
            self.change(r, c - 1, r, c, [''])
            self.view.move(r, c0 - 1)

    def delete(self) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            lines = self.change(r1, c1, r2, c2, [''])
            self.session.memory = lines
            self.view.mark = None
        else:
            r1, c1 = self.view.pos
            r2, c2 = self.view.next()
            self.change(r1, c1, r2, c2, [''])

    def rectangle_delete(self) -> None:
        r1, c1, r2, c2 = self.view.marked_region()
        if c1 == c2:
            return
        if c2 < c1:
            c1, c2 = c2, c1
        lines = []
        for r in range(r1, r2 + 1):
            line = self.lines[r]
            n = len(line)
            if c1 >= n:
                continue
            c3 = min(n, c2)
            line = self.change(r, c1, r, c3, [''])[0]
            lines.append(line)

        self.session.memory = lines
        self.view.mark = None
        self.changed = 42

    def rectangle_insert(self) -> None:
        r1, c1, r2, c2 = self.view.marked_region()
        if c2 < c1:
            c1, c2 = c2, c1
        line = self.session.memory[0]
        for r in range(r1, r2 + 1):
            n = len(self.lines[r])
            if n >= c2:
                self.change(r, c1, r, c2, [line])

        self.view.mark = None
        self.changed = 42

    def indent(self, direction=1) -> None:
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            if c2 > 0:
                r2 += 1
        else:
            r1 = self.view.r
            r2 = r1 + 1
        if direction == 1:
            for r in range(r1, r2):
                self.change(r, 0, r, 0, ['    '])
        else:
            for line in self.lines[r1:r2]:
                if line and not line[:4].isspace():
                    return
            for r in range(r1, r2):
                self.change(r, 0, r, min(4, len(self.lines[r])), [''])
            assert self.view.mark is not None
            r, c = self.view.mark
            self.view.mark = r, min(c, len(self.lines[r]))
            self.view.move(*self.view.pos)

    def dedent(self) -> None:
        self.indent(-1)

    def undo(self) -> None:
        self.history.undo(self)

    def redo(self) -> None:
        self.history.redo(self)

    def paste(self) -> None:
        r, c = self.view.pos
        self.change(r, c, r, c, self.session.memory)
        self.view.mark = None

    def delete_more(self) -> None:
        r, c = self.view.pos
        line = self.lines[r]
        c2 = c
        while c2 < len(line) and line[c2].isidentifier():
            c2 += 1
        if c2 > c:
            lines = self.change(r, c, r, c2, [''])
            self.session.memory = lines
            return
        self.delete()

    def delete_to_end_of_line(self, append: bool = False) -> None:
        r, c = self.view.pos
        if (r, c) == self.view.next():
            return
        line = self.lines[r]
        if c == 0 and line.strip() == '' and r < len(self.lines) - 1:
            lines = self.change(r, 0, r + 1, 0, [''])
        elif c == len(line):
            lines = self.change(r, c, r + 1, 0, [''])
        else:
            lines = self.change(r, c, r, len(line), [''])
        if append:
            if self.session.memory[-1] == '':
                self.session.memory[-1:] = lines
            else:
                self.session.memory.append('')
        else:
            self.session.memory = lines

    def delete_to_end_of_line_again(self) -> None:
        self.delete_to_end_of_line(True)

    def enter(self) -> None:
        r, c = self.view.pos
        self.change(r, c, r, c, ['', ''])
        self.view.pos = (r + 1, 0)
        s = self.lines[r][:c]
        if s and not s.isspace():
            self.indent_line()

    def normalize_space(self) -> None:
        r, c = self.view.pos
        line = self.lines[r]
        n = len(line)
        c1 = len(line[:c].rstrip())
        c2 = n - len(line[c:].lstrip())
        if c1 == c2:
            return
        if c2 < n:
            if not (line[c2] in ')]}' or
                    c1 > 0 and line[c1 - 1] in '([{'):
                c2 -= 1
        self.change(r, c1, r, c2, [''])
        self.view.move(r, c1)

    def complete(self) -> None:
        complete_word(self)

    @cached_property
    def jedi_environment(self):
        from jedi import create_environment, settings  # type: ignore
        settings.case_insensitive_completion = False
        venv = os.environ.get('VIRTUAL_ENV')
        if venv:
            return create_environment(venv)
        return None

    def jedi(self) -> Optional[Document]:
        import jedi  # type: ignore
        r, c = self.view.pos
        s = jedi.Script('\n'.join(self.lines),
                        environment=self.jedi_environment)
        defs = s.infer(r + 1, c)
        self.view.message = f'Definitions found: {len(defs)}'
        if not defs:
            return None
        df = defs[-1]
        self.log((df, df.module_path, df.name, df.type, df.module_name,
                  df.full_name))
        if df.module_path is None:
            self.view.move(df.line - 1, 0)
            return None

        path = Path(df.module_path)
        docs = self.session.docs
        for i, doc in enumerate(docs):
            if doc.path == path:
                docs.pop(i)
                doc.view.move(df.line - 1, 0)
                # doc.view.moved = (df.line, 0)
                # doc.changed = 42
                return doc

        doc = TextDocument()
        doc.read(f'{path}:{df.line}')
        return doc

    def format(self) -> None:
        r1 = self.view.r
        txt = self.lines[r1]
        indent = (len(txt) - len(txt.lstrip())) * ' '
        txt = txt.lstrip()
        r2 = r1 + 1
        while r2 < len(self.lines):
            line = self.lines[r2]
            if len(line) == 0 or line.startswith(indent + ' '):
                break
            r2 += 1
            txt += ' ' + line.lstrip()
        width = self.view.text.w - self.view.wn - 4 - len(indent)
        lines = textwrap.wrap(
            txt,
            width - 3,
            break_long_words=False,
            fix_sentence_endings=True,
            break_on_hyphens=False)
        self.change(r1, 0, r2 - 1, len(self.lines[r2 - 1]),
                    [indent + line for line in lines])

    def tab(self) -> None:
        r, c = self.view.pos
        for key in aliases:
            if self.session.chars.endswith(key):
                self.change(r, c - len(key), r, c, [aliases[key]])
                self.session.chars = ''
                return

        if self.completion.active:
            self.change(r, c, r, c, [self.completion.word()])
            return

        self.indent_line()

    def unicode(self):
        r, c = self.view.pos
        line = self.lines[r]
        for mo in re.finditer(r'\w*', line):
            c1 = mo.start()
            c2 = mo.end()
            if c1 <= c <= c2:
                name = line[c1:c2]
                char = unicode_aliases.get(name)
                if char is not None:
                    self.change(r, c1, r, c2, [char])
                return

    def indent_line(self) -> None:
        r, c = self.view.pos
        r0 = r - 1
        p: List[str] = []
        pend = False
        indent = None
        while r0 >= 0:
            line = self.lines[r0]
            if line and not line.isspace():
                n = len(line)
                for i in range(n - 1, -1, -1):
                    x = line[i]
                    j = '([{'.find(x)
                    if j != -1:
                        if not p:
                            if i < n - 1:
                                indent = i + 1
                                break
                            pend = True
                        elif p.pop() != ')]}'[j]:
                            indent = 0
                            # message
                            break
                    elif x in ')]}':
                        p.append(x)

                if indent is not None:
                    break

                if not p:
                    indent = len(line) - len(line.lstrip())
                    break

            r0 -= 1
        else:
            indent = 0
            line = '?'

        if pend or self.lines[r - 1].rstrip()[-1:] == ':':
            indent += 4

        line = self.lines[r]
        i = len(line) - len(line.lstrip())
        if i < indent:
            self.change(r, 0, r, 0, [' ' * (indent - i)])
        elif i > indent:
            self.change(r, 0, r, i - indent, [''])
        c += indent - i
        if c < indent:
            c = indent
        self.view.move(r, c)

    def replace2(self) -> None:
        pass

    def yapf(self) -> None:
        from yapf.yapflib.yapf_api import FormatCode  # type: ignore

        r1, c1, r2, c2 = self.view.marked_region()
        if r2 > r1:
            if c2 > 0:
                r2 += 1
            c1 = 0
            c2 = 0

        lines = self.get_range(r1, c1, r2, c2)

        new, changed = FormatCode('\n'.join(lines))

        if changed:
            self.view.mark = None
            if r2 == r1:
                lines = [new.strip()]
            else:
                lines = new.splitlines()
        self.change(r1, c1, r2, c2, lines + [''])

    def isort(self) -> None:
        import isort
        new = isort.code('\n'.join(self.lines) + '\n')
        self.view.mark = None
        self.change(0, 0, len(self.lines) - 1, len(self.lines[-1]),
                    new.splitlines())
        self.view.move(0, 0)

    def spell_check(self) -> Document:
        _, _, kind = self.name.partition('.')
        if self.view.mark:
            r1, c1, r2, c2 = self.view.marked_region()
            lines = self.get_range(r1, c1, r2, c2)
            if r1 == r2:
                kind = 'txt'
        else:
            lines = self.lines
            r1 = 0
            c1 = 0
        from spelltinkle.spellcheck import SpellcheckDocument
        return SpellcheckDocument(r1, c1, lines, kind)

    def resolve_conflict(self):
        r, c = self.view.pos
        for r1 in range(r, -1, -1):
            if self.lines[r1].startswith('<<<<<<<'):
                break
        else:
            return self.move_to_next_conflict()
        for r3 in range(r, len(self.lines)):
            if self.lines[r3].startswith('>>>>>>>'):
                break
        else:
            return self.move_to_next_conflict()
        for r2 in range(r1 + 1, r3):
            if self.lines[r2].startswith('======='):
                break
        else:
            return self.move_to_next_conflict()
        if r == r2:
            self.change(r3, 0, r3 + 1, 0, [''])
            self.change(r2, 0, r2 + 1, 0, [''])
            self.change(r1, 0, r1 + 1, 0, [''])
        elif r < r2:
            self.change(r2, 0, r3 + 1, 0, [''])
            self.change(r1, 0, r1 + 1, 0, [''])
        else:
            self.change(r3, 0, r3 + 1, 0, [''])
            self.change(r1, 0, r2 + 1, 0, [''])

    def move_to_next_conflict(self):
        r, c = self.view.pos
        for r1 in range(r, len(self.lines)):
            if self.lines[r1].startswith('<<<<<<<'):
                break
        else:  # no break
            for r1 in range(r):
                if self.lines[r1].startswith('<<<<<<<'):
                    break
            else:  # no break
                return
        self.view.move(max(r1 - 1, 0), 0)

    def convert_dict(self):
        """dct.key <-> dct['key']"""
        r, c = self.view.pos
        line = self.lines[r]
        c1, c2, text = convert_dict_syntax(line, c)
        if text:
            self.change(r, c1, r, c2, [text])

    def diff(self):
        import difflib
        if self.path is None:
            return
        with open(self.path, encoding='UTF-8') as fd:
            blines, _ = tolines(fd)
        alines = self.lines
        if alines[-1] != '':
            r = len(alines) - 1
            c = len(alines[r])
            self.change(r, c, r, c, ['', ''])
        if blines[-1] != '':
            blines.append('')
        s = difflib.SequenceMatcher(a=alines[:-1], b=blines[:-1])
        blocks = s.get_matching_blocks()
        a, b, _ = blocks[0]
        if not (a == 0 and b == 0):
            blocks.insert(0, difflib.Match(0, 0, 0))
        b2 = blocks[-1]
        for b1 in blocks[-2::-1]:
            na = b2.a - (b1.a + b1.size)
            nb = b2.b - (b1.b + b1.size)
            if na or nb:
                self.change(b2.a, 0, b2.a, 0,
                            ['======='] +
                            blines[b2.b - nb:b2.b] +
                            ['>>>>>>> file on disk', ''])
                self.change(b2.a - na, 0, b2.a - na, 0,
                            ['<<<<<<< this document', ''])
            b2 = b1
        self.timestamp = self.path.stat().st_mtime

    def usages(self) -> Optional[Document]:
        import jedi
        r, c = self.view.pos
        s = jedi.Script('\n'.join(self.lines), r + 1, c, '')
        usages = s.usages()
        if not usages:
            return None
        doc = TextDocument()
        doc.change(0, 0, 0, 0, [usage for usage in usages])
        return doc

    def extract_variable(self):
        from spelltinkle.extract_variable import extract_variable
        extract_variable(self)

    def execute(self):
        from spelltinkle.execute import execute_python_code
        execute_python_code(self)

    def run_unittest(self):
        from spelltinkle.run_unittest import run_unittest
        run_unittest(self)

    def terminal(self):
        if self.path is None:
            return
        dir = self.path.parent.absolute()
        subprocess.run(['gnome-terminal',
                        '--geometry',
                        '84x40',
                        f'--working-directory={dir}'])
