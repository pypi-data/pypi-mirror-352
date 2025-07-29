import subprocess


def run_unittest(doc):
    r, _ = doc.view.pos
    while r >= 0:
        if doc.lines[r].startswith('def test_'):
            break
        r -= 1
    else:  # no break
        return
    funcname = doc.lines[r].split('(')[0][4:]
    cmd = f'pytest {doc.name}::{funcname}'
    subprocess.run(['gnome-terminal',
                    '--geometry',
                    '84x40',
                    '--',
                    'sh',
                    '-c',
                    f'history -s "{cmd}" & {cmd} & bash'],
                   stderr=subprocess.DEVNULL,
                   cwd=doc.path.parent)
