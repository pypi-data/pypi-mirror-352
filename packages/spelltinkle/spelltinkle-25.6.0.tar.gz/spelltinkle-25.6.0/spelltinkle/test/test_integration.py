"""Integration tests."""
import stat
from pathlib import Path


def test_writeas(run, tmp_dir):
    run.args = ['asdf']
    run('^d^k^k12345<enter><home><home>^k^p^p^a^k^p^p^a^k^p^p^p^p.<enter>')
    run('# hello<enter>')
    run('A' * 25 * 1)
    run('<up>^a^b^b<down>^c<page-up>^p')
    run('if 1:<enter>a = 1<enter>b = a')
    run('<enter>^ys<bs><bs><bs><bs>writeas.txt<enter>')


def test_open2(run, tmp_dir):
    run.args = ['open2.py']
    with open('open2.py', 'w') as fd:
        fd.write('# hello\na = 42\n')
    run('<home><home>^fhello^f <home>^b^b<up>^d')
    run('^fA<right>^k^ys')
    run('<bs>' * len('open2.py'))
    run('open2b.py<enter>')
    run('^oopen2.py<enter>^s2^q')


def test_tabs(run, tmp_dir):
    run.args = ['tabs.txt']
    Path('tabs.txt').write_text('hello\n\tworld\n')

    run('        hello<enter>')
    run('^q')

    txt = Path('tabs.txt').read_text()
    assert txt == '\thello\n\thello\n\tworld\n'


def test_mouse(run):
    run.session.scr.position = (3, 1)
    run('a.bc<enter><mouse1-clicked>^d')
    assert run.doc.lines[0] == 'abc'
    run.session.scr.position = (3, 4)
    run('<mouse1-clicked>')
    assert run.doc.view.pos == (1, 0)
    run('1<enter>2<enter><up><up><up><end><down>')
    assert run.doc.view.pos == (1, 1)


def test_noend(run, tmp_dir):
    with open('noend.py', 'w') as fd:
        fd.write('a = {\n}')
    run('^onoend.py<enter>')
    assert run.doc.lines[1] == '}'


def test_complete_import(run):
    run.args = ['hmm1.py']
    run('from col')
    run.doc.completion.thread.join()
    run('<tab>')
    assert run.doc.lines[0].endswith('collections')
    run('.ab')
    run('<ctrl_down>')
    run.doc.completion.thread.join()
    run('<tab>')
    assert run.doc.lines[0].endswith('collections.abc')
    run(' import Seq')
    run.doc.completion.thread.join()
    run('<tab>')
    assert run.doc.lines[0].endswith('Sequence')


def test_replace(run, tmp_dir):
    with open('Replace.py', 'w') as fd:
        fd.write('a = {\n}')
    run('^oRepl<tab><enter><end><end><enter>aa<enter>aaa<enter>aaaa<enter>')
    run('<home><home>^x/a/12<enter>ynyyynn!<down>.')
    run('<home><home>^x/12/A<enter>!^s')
    txt = '|'.join(run.doc.lines)
    assert txt == 'A = {|}|aA|AAa|aAAA|.', txt


def test_open_line(run, tmp_dir):
    (tmp_dir / 'openline.txt').write_text('1\n2\n')
    run.args = ['openline.txt:2']
    assert run.pos == (1, 0), run.doc.view.pos


def test_test9(run):
    run('abc<enter>')
    run('123<enter>')
    run.session.scr.position = (4, 1)
    run('<mouse1-clicked>')
    run.session.scr.position = (5, 2)
    run('<mouse1-released>')
    run.session.scr.position = (2, 1)
    run('<mouse2-clicked>')
    assert ''.join(run.lines) == 'c123abc123'


def test_search_backwards(run):
    run('AAA^rA^r^r')
    pos = run.pos
    assert pos == (0, 1)


def test_jedi(run):
    run.args = ['hmm.py']
    run('a11 = 8<enter>')
    run('a12 = 8<enter>')
    run('a1')
    run.doc.completion.thread.join()
    run('<tab>')
    x = run.doc.lines[-1]
    assert x == 'a11', run.doc.lines


def test_write(run, tmp_dir):
    run.args = ['abc.txt']
    run('abc')
    with open('abc.txt', 'w') as fd:
        fd.write('123')
    run('^s')
    assert run.doc.modified
    run('^yS')
    assert not run.doc.modified
    run.doc.timestamp = -100000
    run('123^y^d^y^r')
    assert run.doc.timestamp > -100000
    run('^s')


def test_fileinput(run, tmp_dir):
    dir = tmp_dir / 'mmmm/grrr'
    dir.mkdir(parents=True)
    (dir / 'abc.txt').write_text('hmm')
    run('^ommm<tab><tab><tab><enter>')
    print(run.lines)
    assert run.lines[0] == 'hmm'


def test_rectangle_insert(run):
    run('aaa<enter>')
    run('a<enter>')
    run('aa<enter>')
    run('aaa<enter>')
    run('12^a^k<up><right><ctrl_up><up><up><right>^b^p')
    assert '+'.join(run.lines) == 'a12a+a+a12+a12a+'


def test_mark_and_copy(run):
    run('a1234<left>^w^p')
    assert run.lines[0] == 'a1234a1234'


def test_mail(run):
    # from ..config import Configuration
    # conf = Configuration()
    run.conf.mail = {'test': {'host': 'test', 'user': 'test'}}
    mail = run.conf.home / 'mail'
    test = mail / 'test'
    test.mkdir(parents=True)
    pw = test / 'pw'
    pw.write_text('test')
    pw.chmod(stat.S_IRUSR | stat.S_IWUSR)
    (mail / 'addresses.csv').write_text('Sloof Lirpa <test@test.org>,test\n')
    run('^vmr')
    print(run.lines)


def test_calender(run):
    run('^vc^q^q')


def test_goto_line(run):
    run('1<enter>2<enter>3^x2<enter>')
    assert run.pos == (1, 0)


def test_resolve_conflict(run):
    run('<<<<<<<<<<<<<<<enter>1<enter>=======<enter>2<enter>>>>>>>>><enter>')
    run('^x1<enter>^y^r')
    assert run.lines == ['1', '']


def test_diff(run, tmp_dir):
    run('1<enter>2<enter>3<enter>4<enter>')
    run('^s1234<enter>')
    run('^x2<enter>.')
    run('^y^d')
    run('^x6<enter>^y^r^y^d')
    assert ''.join(run.lines) == '1234'


def test_diff2(run, tmp_dir):
    run('tttt<enter>^sxx<enter><up>^k^k1=a<enter><enter>3<enter>4<enter>')
    run('1234<enter>')
    run('^y^d')


def test_indent(run):
    run('def f(<enter>):<enter>')
    assert run.pos == (2, 4)


def test_open_file_under_cursor(run, tmp_dir):
    run('  xyz.txt abc/ty<enter>^sxyz.txt<enter><up>^y^o^q')


def test_convert_dict(run):
    run('dct_1A.A_2x = 4')
    run('^r.<left>^y.')
    assert run.lines[0] == "dct_1A['A_2x'] = 4"
    run('^r[<left>^y.')
    assert run.lines[0] == 'dct_1A.A_2x = 4'
