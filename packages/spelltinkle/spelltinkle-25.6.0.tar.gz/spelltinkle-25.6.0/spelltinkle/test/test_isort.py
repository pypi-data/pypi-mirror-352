from spelltinkle.text import TextDocument


def test_isort():
    doc = TextDocument()
    doc.change(0, 0, 0, 0, ['import b', 'import a'])
    doc.isort()
    assert doc.lines == ['import a', 'import b']
