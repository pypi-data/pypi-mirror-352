import datetime as dt
from ..calender import parse1, parse2, CalenderDocument

DAY = dt.timedelta(days=1)

calender = """
2013
sep
27 Spelltinkle [0 years]

2020
may
5 16:30-18 Event
"""


def test_calender():
    begin = dt.datetime(2020, 5, 1)
    end = begin + 200 * DAY
    events = parse1(calender.splitlines())
    things = sorted(parse2(events, begin, end))
    found = 0
    for t1, t2, row, text in things:
        if text == 'Spelltinkle [7 years]':
            found += 1
    assert found == 1


def test_calender_doc(tmp_path, config):
    cal = tmp_path / 'calender.txt'
    cal.write_text(calender)
    config.calender_file = cal
    doc = CalenderDocument(cal)
    doc.list(begin=dt.datetime(2020, 5, 1), days=220)
    print(doc.lines)
