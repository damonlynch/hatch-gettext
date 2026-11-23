#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from hatch_gettext.plugin import GettextBuildHook

PO_TEMPLATE = """msgid ""
msgstr ""
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "hello"
msgstr "{translated}"
"""

DESKTOP_TEMPLATE = """[Desktop Entry]
Type=Application
_Name=hello
"""

XML_TEMPLATE = """<?xml version="1.0"?>
<document>
  <title translatable="true">hello</title>
</document>
"""


class FakeRun:
    """
    Stand in for subprocess.run so that the gettext utilities need not be
    installed. Every call is recorded, and the canned streams are returned.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[list[str] | str, dict[str, Any]]] = []
        self.returncode = 0
        self.stdout = ""
        self.stderr = ""

    def fail(self, stdout: str = "", stderr: str = "") -> None:
        self.returncode = 1
        self.stdout = stdout
        self.stderr = stderr

    def __call__(self, cmd: list[str] | str, **kwargs: Any) -> SimpleNamespace:
        self.calls.append((cmd, kwargs))
        return SimpleNamespace(
            returncode=self.returncode, stdout=self.stdout, stderr=self.stderr
        )

    @property
    def cmd(self) -> list[str] | str:
        return self.calls[-1][0]

    @property
    def kwargs(self) -> dict[str, Any]:
        return self.calls[-1][1]


@pytest.fixture(autouse=True)
def isolate_linguas(monkeypatch: pytest.MonkeyPatch) -> None:
    """An inherited LINGUAS would silently subset every po glob."""

    monkeypatch.delenv("LINGUAS", raising=False)


@pytest.fixture
def fake_run(monkeypatch: pytest.MonkeyPatch) -> FakeRun:
    """Replace subprocess.run for the duration of the test."""

    fake = FakeRun()
    monkeypatch.setattr(subprocess, "run", fake)
    return fake


@pytest.fixture
def make_hook(tmp_path: Path) -> Callable[..., GettextBuildHook]:
    """
    Build a real hook instance with the dependencies Hatch injects stubbed, so
    its root, config, metadata, target_name and app properties behave exactly
    as they do during a build.
    """

    def factory(
        config: dict[str, Any] | None = None,
        project_name: str = "myapp",
        root: Path | str | None = None,
        target_name: str = "wheel",
        verbosity: int = 0,
    ) -> GettextBuildHook:
        hook = GettextBuildHook(
            root=str(tmp_path if root is None else root),
            config={} if config is None else config,
            build_config=None,
            metadata=SimpleNamespace(name=project_name),
            directory="",
            target_name=target_name,
            app=SimpleNamespace(verbosity=verbosity),
        )
        # Hatch only reaches the plug-in through initialize()/clean(), which set
        # the console up first, so do the same when testing methods directly
        hook.setup_console()
        return hook

    return factory


@pytest.fixture
def make_project() -> Callable[[Path], Path]:
    """
    Create a minimal gettext project tree in the given directory: a po
    directory holding two languages, and translatable .desktop and .xml files.
    """

    def factory(root: Path) -> Path:
        po_dir = root / "po"
        po_dir.mkdir(parents=True, exist_ok=True)
        for language in ("es", "fr"):
            (po_dir / f"{language}.po").write_text(
                PO_TEMPLATE.format(translated=f"{language} translation"),
                encoding="utf-8",
            )
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "myapp.desktop.in").write_text(DESKTOP_TEMPLATE, encoding="utf-8")
        (data_dir / "myapp.xml.in").write_text(XML_TEMPLATE, encoding="utf-8")
        return root

    return factory


@pytest.fixture
def project(tmp_path: Path, make_project: Callable[[Path], Path]) -> Path:
    return make_project(tmp_path)


@pytest.fixture
def spaced_project(tmp_path: Path, make_project: Callable[[Path], Path]) -> Path:
    """
    The same tree below a directory whose name contains a space, as Windows
    user homes and project paths frequently do.
    """

    return make_project(tmp_path / "spaced project")
