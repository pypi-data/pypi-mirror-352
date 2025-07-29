from spelltinkle.cursors import CursorsMode


def extract_variable(doc):
    """Transform

        x = 2 + 2

    to

        s = 2 + 2
        x = s
    """
    r1, c1, r2, c2 = doc.view.marked_region()
    if r1 != r2:
        return
    line = doc.lines[r1]
    indent = ' ' * (len(line) - len(line.lstrip(' ')))
    doc.change(r1, c1, r2, c2, [''])
    doc.change(r1, 0, r1, 0, [indent + ' = ' + line[c1:c2], ''])
    doc.view.mark = None
    doc.view.cursors = {(r1, len(indent)), (r1 + 1, c1)}
    doc.handler = CursorsMode(doc, add_cursor=False)
