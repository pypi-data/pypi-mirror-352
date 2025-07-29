from typing import List


def complete(line: str, point: int, word: str, previous: str) -> List[str]:
    opts = ['-h', '--help', '-m', '--module']
    if word[:1] == '-':
        return opts

    if previous in ['-m', '--module']:
        return complete_module(word)

    return []


def complete_module(word: str) -> List[str]:
    from jedi import Script  # type: ignore
    s = Script('import ' + word)
    completions = s.complete(1, len(word) + 7)
    names = []
    for comp in completions:
        names.append(comp.name_with_symbols)
    return names


if __name__ == '__main__':
    import os
    import sys
    line = os.environ['COMP_LINE']
    point = int(os.environ['COMP_POINT'])
    word, previous = sys.argv[2:]
    words = complete(line, point, word, previous)
    for w in words:
        if w.startswith(word):
            print(w)
