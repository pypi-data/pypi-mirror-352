import subprocess
import sys
from pathlib import Path


def execute(text: str, folder: Path) -> str:
    p = subprocess.run([sys.executable, '-'],
                       input=text.encode(),
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    return p.stdout.decode()


def execute_python_code(doc):
    if not doc.view.mark:
        return
    r1, _, r2, _ = doc.view.marked_region()
    text = execute('\n'.join(doc.lines[r1:r2]), doc.path)
    if text:
        doc.change(r2, 0, r2, 0, text.splitlines() + [''])
        doc.view.mark = (r2, 0)
