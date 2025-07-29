"""
Ma 27
Ti 28
      ==== December: ===========================
On  1
To  2
Fr  3
Lø  4
Sø  5
      ---- uge 43: --------------------------------

"""
import datetime as dt
import re
from pathlib import Path
from typing import List

from spelltinkle.color import Color
from spelltinkle.document import Document
from spelltinkle.i18n import translate as _
# from spelltinkle.input import Input
from spelltinkle.text import TextDocument


MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
          'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

DAYS = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']

DAY = dt.timedelta(days=1)
HOUR = dt.timedelta(hours=1)


def hm(s):
    if ':' in s:
        return (int(x) for x in s.split(':'))
    else:
        return (int(s), 0)


def weeknumber(t):
    t1 = dt.datetime(t.year + 1, 1, 1)
    n = t1.weekday()
    if 0 < n < 4 and t.month == 12 and t.day > 31 - n:
        return 1
    t1 = dt.datetime(t.year, 1, 1)
    n = t1.weekday()
    if n <= 3:
        return ((t - t1).days + n) // 7 + 1
    wn = ((t - t1).days + n) // 7
    if wn == 0:
        return weeknumber(t1 - DAY)
    return wn


def parse1(lines):
    months = [_(month) for month in MONTHS]
    for row, line in enumerate(lines):
        words = line.strip().split()
        if not words or words[0][0] == '#':
            continue
        w = words.pop(0)
        if len(words) == 0:
            if w.isnumeric():
                year = int(w)
            else:
                month = months.index(w) + 1
            continue

        if '-' in w:
            day1, day2 = (int(day) for day in w.split('-'))
            t1 = dt.datetime(year, month, day1)
            month2 = month
            year2 = year
            if day2 < day1:
                month2 += 1
                if month2 == 13:
                    month2 = 1
                    year2 += 1
            t2 = dt.datetime(year2, month2, day2)

            t2 += DAY
        else:
            day = int(w)

            w = words.pop(0)
            if re.match(r'\d+(:\d+)?(-(\d+(:\d+)?)?)?$', w):
                if '-' in w:
                    w1, w2 = w.split('-')
                    t1 = dt.datetime(year, month, day, *hm(w1 or '0'))
                    t2 = dt.datetime(year, month, day, *hm(w2 or '23:59'))
                else:
                    if ':' in w:
                        hour, minute = hm(w)
                    else:
                        hour = int(w)
                        minute = 0
                        if hour > 24:
                            hour = 0
                            words[:0] = [w]
                    t1 = dt.datetime(year, month, day, hour, minute)
                    t2 = t1 + HOUR
            else:
                t1 = dt.datetime(year, month, day)
                t2 = t1 + DAY
                words[:0] = [w]

        birthday = -1
        alarm = -1
        if words[-1][-1] == ']':
            for i, word in enumerate(reversed(words)):
                if word[0] == '[':
                    for note in ' '.join(words[-1 - i:])[1:-1].split(','):
                        note = note.strip()
                        if note.endswith((_('year'), _('years'))):
                            birthday = int(note.split()[0])
                        elif note.startswith('*'):
                            alarm = 1
                    words = words[:-1 - i]
                    break
            else:
                1 / 0  # '[' not found!

        yield t1, t2, row, ' '.join(line.split()[1:]), birthday, alarm


def plural(n, thing):
    t = _(thing if n == 1 else thing + 's')
    return f'{n} {t}'


def parse2(events, start, stop):
    for t1, t2, row, text, birthday, alarm in events:
        if birthday != -1:
            t = dt.datetime(start.year, t1.month, t1.day, t1.hour, t1.minute)
            while t < start:
                t = dt.datetime(t.year + 1, t.month, t.day, t.hour, t.minute)
            while t < stop:
                y = t.year - t1.year + birthday
                years = plural(y, 'year')
                i = text.rfind('[')
                text = text[:i] + f'[{years}]'
                yield t, t - t1 + t2, row, text
                t = dt.datetime(t.year + 1, t.month, t.day, t.hour, t.minute)
        else:
            if t2 > start and t1 < stop:
                yield t1, t2, row, text


class CalenderDocument(Document):
    def __init__(self, calender_file: Path):
        self.calender_file = calender_file
        Document.__init__(self)
        self.color = Color()
        self._gutterwidth = 6
        self._gutter: List[str] = []
        self.name = _('calender')
        self.list()
        self.changes = 42

    def gutter(self, r: int) -> str:
        return self._gutter[r]

    def list(self, begin: dt.date | None = None, days: int = 500):
        begin = begin or dt.date.today()
        begin = dt.datetime(begin.year, begin.month, begin.day)
        end = begin + days * DAY
        with self.calender_file.open() as fd:
            events1 = parse1(fd)
            events = sorted(parse2(events1, begin, end))
        lines = []
        day = begin
        for t1, t2, row, text in events:
            day1 = dt.datetime(t1.year, t1.month, t1.day)
            while day < day1:
                lines.append((day, ''))
                day += DAY
            lines.append((day1, text))
            day += DAY

        lines2 = []
        colors: list[bytearray] = []
        self.color.colors = colors
        self._gutter = []
        nweekdayprev = -1
        week = _('week').title()
        for t1, description in lines:
            nweekday = t1.weekday()
            if nweekday == nweekdayprev:
                weekday = '  '
            else:
                nweekdayprev = nweekday
                if t1.day == 1:
                    m = _(MONTHS[t1.month - 1]).title()
                    lines2.append(
                        f'{m} {t1.year}: = = = = = = = = = =')
                    self._gutter.append('      ')
                if nweekday == 0:
                    lines2.append(
                        f'{week} {weeknumber(t1)}: - - - - - -')
                    self._gutter.append('      ')
                weekday = _(DAYS[nweekday]).title()

            lines2.append(description)
            self._gutter.append(f'{weekday} {t1.day:2d} ')

        for line in lines2:
            if line.endswith('= = ='):
                color = 2
            elif line.endswith('- - -'):
                color = 4
            else:
                color = 0
            colors.append(bytearray([color] * len(line)))

        self.lines = lines2
        self.view.move(0, 0)

    def enter(self, session):
        self.session.docs.pop()
        for i, doc in enumerate(session.docs):
            if doc.path == session.conf.calender_file:
                session.docs.pop(i)
                return doc
        doc = TextDocument()
        doc.read(session.conf.calender_file)
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
