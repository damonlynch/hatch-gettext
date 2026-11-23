#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import gettext
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from hatch_gettext.plugin import GettextBuildHook, GettextError

# The utilities are external, so the tests that shell out to them are skipped
# rather than failed where they are absent (intltool especially on Windows).
requires_msgfmt = pytest.mark.skipif(
    shutil.which("msgfmt") is None, reason="msgfmt is not installed"
)
requires_intltool_merge = pytest.mark.skipif(
    shutil.which("intltool-merge") is None, reason="intltool-merge is not installed"
)

BROKEN_PO = "this is not a portable object file\n"


def mo_file(root: Path, language: str, name: str = "myapp") -> Path:
    return root / "locale" / language / "LC_MESSAGES" / f"{name}.mo"


def catalog_string(mo: Path) -> str:
    """Read the compiled catalog back, which also proves it is a valid mo file."""

    with mo.open("rb") as stream:
        return gettext.GNUTranslations(stream).gettext("hello")


def loaded(make_hook, root: Path, **config: object) -> GettextBuildHook:
    hook = make_hook({"locale-directory": "locale", **config}, root=root)
    hook.load_gettextbuild_config()
    return hook


@requires_msgfmt
def test_compile_mo_files_writes_working_catalogs(make_hook, project) -> None:
    hook = loaded(make_hook, project)
    hook.compile_mo_files()

    assert catalog_string(mo_file(project, "es")) == "es translation"
    assert catalog_string(mo_file(project, "fr")) == "fr translation"


@requires_msgfmt
def test_compile_mo_files_copes_with_a_path_containing_a_space(
    make_hook, spaced_project
) -> None:
    root = spaced_project
    assert " " in str(root)
    hook = loaded(make_hook, root)
    hook.compile_mo_files()

    assert catalog_string(mo_file(root, "es")) == "es translation"


@requires_msgfmt
def test_i18n_name_is_used_for_the_compiled_filename(make_hook, project) -> None:
    hook = loaded(make_hook, project, **{"i18n-name": "photo-tool"})
    hook.compile_mo_files()

    assert catalog_string(mo_file(project, "es", "photo-tool")) == "es translation"


@requires_msgfmt
def test_a_broken_po_file_reports_the_tool_diagnostics(make_hook, project) -> None:
    broken = project / "po" / "broken.po"
    broken.write_text(BROKEN_PO, encoding="utf-8")
    hook = loaded(make_hook, project)

    with pytest.raises(GettextError, match="Error while invoking msgfmt") as exc_info:
        hook._compile_po_to_mo(broken, mo_file(project, "zz"))

    assert broken.name in str(exc_info.value)


def test_do_work_end_to_end_without_the_tools(make_hook, project, fake_run) -> None:
    files = {"data": ["data/myapp.desktop.in"]}
    hook = make_hook(
        {"locale-directory": "locale", "files": files},
        root=project,
        target_name="wheel",
    )
    build_data = {"artifacts": []}
    hook.initialize("1.2.3", build_data)

    assert build_data["artifacts"] == [
        str(Path("locale") / "es" / "LC_MESSAGES" / "myapp.mo"),
        str(Path("locale") / "fr" / "LC_MESSAGES" / "myapp.mo"),
        str(Path("data") / "myapp.desktop"),
    ]
    assert [cmd[0] for cmd, _ in fake_run.calls] == [
        "msgfmt",
        "msgfmt",
        "intltool-merge",
    ]


def test_do_work_creates_the_directories_it_needs(make_hook, project, fake_run) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project, target_name="wheel")
    hook.do_work({"artifacts": []})

    assert (project / "locale" / "es" / "LC_MESSAGES").is_dir()
    assert (project / "locale" / "fr" / "LC_MESSAGES").is_dir()
    assert [cmd[0] for cmd, _ in fake_run.calls] == ["msgfmt", "msgfmt"]


@pytest.mark.usefixtures("fake_run")
def test_intltool_checks_are_skipped_for_a_wheel(
    make_hook, project, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook = make_hook(
        {
            "locale-directory": "locale",
            "identify-left-out": True,
            "regenerate-template": True,
            "show-report": True,
        },
        root=project,
        target_name="wheel",
    )
    ran: list[str] = []
    stub_intltool_checks(hook, monkeypatch, ran)
    hook.do_work({"artifacts": []})

    assert ran == []


@pytest.mark.usefixtures("fake_run")
def test_intltool_checks_run_for_an_sdist(
    make_hook, project, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook = make_hook(
        {
            "locale-directory": "locale",
            "identify-left-out": True,
            "regenerate-template": True,
            "show-report": True,
        },
        root=project,
        target_name="sdist",
    )
    ran: list[str] = []
    stub_intltool_checks(hook, monkeypatch, ran)
    hook.do_work({"artifacts": []})

    assert ran == ["identify_left_out", "regenerate_template", "show_report"]


INTLTOOL_CHECKS = ("identify_left_out", "regenerate_template", "show_report")


def stub_intltool_checks(hook, monkeypatch: pytest.MonkeyPatch, ran: list[str]) -> None:
    """Record which of the optional sdist-only checks the build asks for."""

    for name in INTLTOOL_CHECKS:
        monkeypatch.setattr(hook, name, record(ran, name))


def record(ran: list[str], name: str) -> Callable[[], None]:
    def stub() -> None:
        ran.append(name)

    return stub


@requires_intltool_merge
def test_translate_files_merges_the_desktop_template(make_hook, project) -> None:
    hook = loaded(make_hook, project, files={"data": ["data/myapp.desktop.in"]})
    hook.translate_files()

    merged = project / "data" / "myapp.desktop"
    assert merged.is_file()
    assert "translation" in merged.read_text(encoding="utf-8")
