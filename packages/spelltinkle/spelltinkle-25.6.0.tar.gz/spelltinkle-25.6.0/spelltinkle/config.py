from pathlib import Path
from typing import Any


class Configuration:
    def __init__(self,
                 home=None,
                 mail=None,
                 calender_file=None):
        self.home = home or Path.home() / '.spelltinkle'
        self.mail = mail or {}
        self.calender_file = calender_file

    def read(self):
        filename = self.home / 'config.py'
        if filename.is_file():
            dct: dict[str, Any] = {}
            exec(filename.read_text(), dct)
            if 'calender_file' in dct:
                self.calender_file = Path(dct['calender_file']).expanduser()
            self.mail = dct.get('mail', {})
