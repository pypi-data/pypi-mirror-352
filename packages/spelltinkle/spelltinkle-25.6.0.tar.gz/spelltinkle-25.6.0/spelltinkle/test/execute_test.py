from spelltinkle.text import TextDocument


def test_execute():
    doc = TextDocument()
    doc.change(0, 0, 0, 0, ['x = 2 + 2', 'print(x)', '2 / 0', ''])
    doc.view.mark = (0, 0)
    doc.view.pos = (2, 0)
    doc.execute()
    doc.view.mark = (0, 0)
    doc.view.pos = (4, 0)
    doc.execute()
    print(doc.lines)
    assert doc.lines == [
        'x = 2 + 2',
        'print(x)',
        '4',
        '2 / 0',
        '4',
        'Traceback (most recent call last):',
        '  File "<stdin>", line 4, in <module>',
        'ZeroDivisionError: division by zero',
        '']
