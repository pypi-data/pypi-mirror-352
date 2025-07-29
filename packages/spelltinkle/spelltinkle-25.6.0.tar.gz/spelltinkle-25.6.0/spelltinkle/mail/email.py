from __future__ import annotations
from datetime import datetime

from .addresses import Addresses


class EMail:
    def __init__(self,
                 uid: int,
                 date: datetime,
                 subject: str,
                 fro: str,
                 to: list[str],
                 parts: list[str],
                 attachments: list[str] | None = None,
                 reply_to: str | None = None,
                 cc: list[str] | None = None,
                 bcc: list[str] | None = None,
                 forwards: list[int] | None = None,
                 replies: list[int] | None = None):
        self.uid = uid
        self.date = date
        self.subject = subject
        self.fro = fro
        self.to = to
        self.parts = parts
        self.attachments = attachments
        self.reply_to = reply_to
        self.cc = cc
        self.bcc = bcc
        self.forwards = forwards
        self.replies = replies

        self._date_string = ''
        self.excerpt = None

    def __repr__(self):
        attrs = ['uid', 'date', 'subject', 'fro', 'to',
                 'attachments', 'reply_to', 'cc', 'bcc',
                 'forwards', 'replies']
        things = []
        for attr in attrs:
            x = getattr(self, attr)
            if x:
                things.append(f'{attr}={x!r}')
        args = ', '.join(things)
        return f'Email({args})'

    # @functools.cached_property
    @property
    def date_string(self):
        if not self._date_string:
            self._data_string = f'{self.date:%y%b%d-%H:%M}'
        return self._date_string

    def to_line(self, addresses: Addresses) -> str:
        to = ','.join(addresses.short_name(a) for a in self.to)
        text = self.subject
        return f'{self.date} {self.fro}->{to} {text}'
