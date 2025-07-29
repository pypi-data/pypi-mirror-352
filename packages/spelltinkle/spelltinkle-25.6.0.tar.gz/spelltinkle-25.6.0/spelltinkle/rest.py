"""Find :ref:`name` in ReST documents.

Target::

  .. _name:

Reference to target::

  :ref:`name`
"""

from pathlib import Path


def find_reference(name: str,
                   folder: Path) -> tuple[Path, int]:
    while not (folder / 'conf.py').is_file():
        parent = folder.parent
        if parent == folder:
            raise ValueError('Could not find root of ReST tree')
        folder = parent
    ref = f'.. _{name}:'
    for path in folder.glob('**/*.rst'):
        for c, line in enumerate(path.read_text().splitlines()):
            if ref in line:
                return path, c
    raise ValueError('Reference not found')
