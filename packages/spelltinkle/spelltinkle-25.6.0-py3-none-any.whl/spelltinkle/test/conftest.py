import os
# from typing import NamedTuple, List, Dict, Callable, Tuple, Iterator

import pytest

from ..config import Configuration
from ..input import str2keys
from ..session import Session
from ..text import TextDocument


@pytest.fixture
def tmp_dir(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(cwd)


class TestLoop:
    def __init__(self):
        self.calls = []

    def is_running(self):
        return True

    def call_soon_threadsafe(self, func):
        self.calls.append(func)

    def call_soon(self, func):
        self.calls.append(func)

    def stop(self):
        pass


class Run:
    def __init__(self, conf):
        self.conf = conf
        self._session: Session | None = None
        self.args = []

    @property
    def session(self):
        if self._session is None:
            self._session = Session(Screen(10, 30), self.conf)  # type: ignore
            for path in self.args:
                doc = TextDocument(self._session)
                doc.read(path)
                self._session.docs.append(doc)
            if not self._session.docs:
                self._session.docs.append(TextDocument(self._session))

            self._session.loop = TestLoop()  # type: ignore
            self._session.update()
        return self._session

    @property
    def doc(self):
        return self.session.docs[-1]

    @property
    def lines(self):
        return self.doc.lines

    @property
    def pos(self):
        return self.doc.view.pos

    def __call__(self, keys):
        self.session.scr.keys = [key for key in str2keys(keys)]
        while self.session.scr.keys:
            print(self.session.scr.keys[0])
            self.session.input1()
        for func in self.session.loop.calls:
            func()


@pytest.fixture(scope='session')
def config(tmp_path_factory):
    home = tmp_path_factory.mktemp('conf')
    return Configuration(home)


@pytest.fixture
def run(config):
    r = Run(config)
    return r


class Screen:
    def __init__(self, h, w, stream=None):
        self.h = h
        self.w = w
        self.stream = stream
        self.keys = []

    def subwin(self, a, b, c, d):
        return Screen(a, b)

    def erase(self):
        pass

    def refresh(self):
        pass

    def move(self, a, b):
        pass

    def write(self, line, colors):
        pass

    def input(self):
        return self.keys.pop(0)
