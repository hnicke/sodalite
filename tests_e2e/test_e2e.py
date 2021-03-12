import os
from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch
from pytest import fixture

from sodalite.ui import graphics


def test_e2e(tmp_path: Path):
    os.chroot(tmp_path)
    graphics.run(tmp_path)


@fixture(autouse=True)
def stdin(monkeypatch: MonkeyPatch):
    number_inputs = StringIO('')
    monkeypatch.setattr('sys.stdin', number_inputs)
