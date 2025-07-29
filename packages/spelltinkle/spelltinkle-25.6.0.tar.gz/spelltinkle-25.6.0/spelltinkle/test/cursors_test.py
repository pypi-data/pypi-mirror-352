def test_cursors(run):
    """
    *1
    *2
    """
    run('*1<enter>*2<enter><up>^y^c<up>^y^c')
    run('abc<delete><bs><home>+<end>.<esc>*')
    assert run.doc.lines == ['+ab1.',
                             '+ab2.*',
                             '']


def test_extract_variable(run):
    run('x = 2 + 2')
    run('<ctrl_left>' * 5)
    run('^b^vy<esc>')
    assert run.doc.lines == ['y = 2 + 2',
                             'x = y']
