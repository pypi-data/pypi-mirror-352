from spelltinkle.spellcheck import SpellcheckDocument


def test_spellcheck():
    doc = SpellcheckDocument(
        0, 0, ['A pyton is a snake', 'asdfasdg tyypo'], 'txt')
    assert 'Python' in doc.lines[0]
