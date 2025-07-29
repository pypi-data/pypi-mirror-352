from typing import Dict

keynames = {
    '^a': 'home',
    '^l': 'home',
    '^c': 'copy',
    '^d': 'delete',
    '^e': 'end',
    '^f': 'search_forward',
    '^g': 'code_analysis',
    '^h': 'help',
    '^i': 'tab',
    '^k': 'delete_to_end_of_line',
    '^n': 'down1',
    '^o': 'open',
    '^p': 'paste',
    '^q': 'quit',
    '^r': 'search_backward',
    '^s': 'write',
    '^t': 'swap',
    '^u': 'undo',
    '^v': 'view_files',
    '^w': 'mark_word',
    '^x': 'command',
    '^z': 'stop',
    '^ ': 'normalize_space'}

doubles: Dict[str, Dict[str, str]] = {
    '^b': {'^d': 'rectangle_delete',
           '^p': 'rectangle_insert',
           '<': 'dedent',
           '>': 'indent',
           '^v': 'extract_variable'},
    '^y': {'^b': 'go_to_bookmark',
           'b': 'create_bookmark',
           '^c': 'cursor',
           '^d': 'diff',
           '^f': 'format',
           'f': 'toggle_f_string',
           '^g': 'jedi',  # goto def
           'i': 'isort',
           '^m': 'macro',
           '^o': 'open_file_under_cursor',
           'Q': 'quit_force',
           '^r': 'resolve_conflict',
           '^s': 'spell_check',
           's': 'write_as',
           'S': 'write_force',
           'T': 'terminal',
           '^t': 'run_unittest',
           '^u': 'usages',
           'u': 'unicode',
           'U': 'untab',
           '^x': 'execute',
           '^y': 'complete',  # old complete
           '.': 'convert_dict',
           '+': 'upper',
           '-': 'lower',
           '8': 'yapf'}}

again = {'delete_to_end_of_line'}

repeat = {'home', 'end'}

typos = {'imoprt': 'import'}

aliases = {'np': 'import numpy as np',
           'plt': 'import matplotlib.pyplot as plt',
           'path': 'from pathlib import Path',
           'dd': 'from collections import defaultdict',
           'main': "if __name__ == '__main__':",
           'init': 'def __init__(self):',
           'hint': 'from typing import Sequence',
           'fut': 'from __future__ import annotations'}

unicode_aliases = {
    'alpha': 'α',
    'beta': 'β',
    'gamma': 'γ',
    'delta': 'δ',
    'epsilon': 'ε',
    'zeta': 'ζ',
    'eta': 'η',
    'theta': 'θ',
    'iota': 'ι',
    'kappa': 'κ',
    'lamda': 'λ',
    'mu': 'μ',
    'nu': 'ν',
    'xi': 'ξ',
    'omicron': 'ο',
    'pi': 'π',
    'rho': 'ρ',
    'sigma': 'σ',
    'tau': 'τ',
    'upsilon': 'υ',
    'phi': 'φ',
    'chi': 'χ',
    'psi': 'ψ',
    'omega': 'ω',
    'dagger': '†'}


def main():
    import unicodedata as ud
    for n in range(940, 980):
        c = chr(n)
        print(f"'{ud.name(c).split()[-1].lower()}': '{c}',")


if __name__ == '__main__':
    main()
