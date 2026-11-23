#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import subprocess
from pathlib import Path

import pytest

from hatch_gettext.plugin import GettextBuildHook, GettextError


def configured(make_hook, root: Path, **config: object) -> GettextBuildHook:
    """A hook with its configuration loaded, ready for command-level tests."""

    hook = make_hook({"locale-directory": "locale", **config}, root=root)
    hook.load_gettextbuild_config()
    return hook


def test_msgfmt_is_invoked_with_an_argv_list(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    po_file = project / "po" / "es.po"
    mo_file = project / "locale" / "es" / "LC_MESSAGES" / "myapp.mo"
    hook._compile_po_to_mo(po_file, mo_file)

    assert fake_run.cmd == ["msgfmt", f"--output-file={mo_file}", str(po_file)]


def test_msgfmt_options(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    hook._compile_po_to_mo(project / "po" / "es.po", project / "es.mo")

    assert fake_run.kwargs["check"] is False
    assert fake_run.kwargs["capture_output"] is True
    assert fake_run.kwargs["text"] is True


@pytest.mark.parametrize(
    ("in_file", "switch"),
    [("myapp.desktop.in", "-d"), ("myapp.xml.in", "-x")],
)
def test_intltool_merge_uses_the_switch_for_the_file_type(
    make_hook, project, fake_run, in_file: str, switch: str
) -> None:
    hook = configured(make_hook, project)
    hook._translate_file(
        project / "po", project / "data" / in_file, project / "data" / "myapp"
    )

    assert fake_run.cmd == [
        "intltool-merge",
        switch,
        str(project / "po"),
        str(project / "data" / in_file),
        str(project / "data" / "myapp"),
    ]


def test_unknown_translatable_file_type_is_rejected(
    make_hook, project, fake_run
) -> None:
    hook = configured(make_hook, project)
    with pytest.raises(KeyError, match=r"\.bad"):
        hook._translate_file(
            project / "po",
            project / "data" / "myapp.bad.in",
            project / "data" / "myapp",
        )
    assert fake_run.calls == []


def test_paths_containing_a_space_stay_whole(
    make_hook, spaced_project, fake_run
) -> None:
    root = spaced_project
    assert " " in str(root)
    hook = configured(make_hook, root)
    po_file = root / "po" / "es.po"
    mo_file = root / "locale" / "es" / "LC_MESSAGES" / "my app.mo"
    hook._compile_po_to_mo(po_file, mo_file)

    cmd = fake_run.cmd
    assert isinstance(cmd, list)
    assert cmd[1:] == [f"--output-file={mo_file}", str(po_file)]


def test_intltool_merge_paths_with_a_space_stay_whole(
    make_hook, spaced_project, fake_run
) -> None:
    root = spaced_project
    hook = configured(make_hook, root)
    in_file = root / "data" / "my app.desktop.in"
    out_file = root / "data" / "my app.desktop"
    hook._translate_file(root / "po", in_file, out_file)

    assert fake_run.cmd[-3:] == [str(root / "po"), str(in_file), str(out_file)]


def test_a_failing_utility_raises_with_its_diagnostics(
    make_hook, project, fake_run
) -> None:
    hook = configured(make_hook, project)
    fake_run.fail(stderr="msgfmt: cannot open input file")

    with pytest.raises(GettextError, match="Error while invoking msgfmt") as exc_info:
        hook._compile_po_to_mo(project / "missing.po", project / "es.mo")

    assert "cannot open input file" in str(exc_info.value)


def test_stderr_is_preferred_over_stdout(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    fake_run.fail(stdout="noise", stderr="the real problem")

    with pytest.raises(GettextError, match="the real problem") as exc_info:
        hook._compile_po_to_mo(project / "es.po", project / "es.mo")

    assert "noise" not in str(exc_info.value)


def test_stdout_is_used_when_stderr_is_empty(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    fake_run.fail(stdout="intltool complained here", stderr="   ")

    with pytest.raises(GettextError, match="intltool complained here"):
        hook._translate_file(
            project / "po", project / "data" / "myapp.desktop.in", project / "x.desktop"
        )


def test_intltool_merge_failure_names_the_utility(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    fake_run.fail(stderr="bad xml")

    with pytest.raises(GettextError, match="Error while invoking intltool-merge"):
        hook._translate_file(
            project / "po", project / "data" / "myapp.xml.in", project / "x.xml"
        )


def test_identify_left_out_command(make_hook, project, fake_run) -> None:
    hook = configured(make_hook, project)
    fake_run.stdout = ""
    hook.identify_left_out()

    assert fake_run.cmd == ["intltool-update", "-m"]
    assert fake_run.kwargs["cwd"] == project / "po"
    assert fake_run.kwargs["stderr"] is subprocess.STDOUT
    assert fake_run.kwargs["stdout"] is subprocess.PIPE
    assert fake_run.kwargs["check"] is False


def test_identify_left_out_reports_the_missing_files(
    make_hook, project, fake_run, capsys
) -> None:
    hook = configured(make_hook, project)
    fake_run.stdout = "data/myapp.desktop.in\n"

    with pytest.raises(ValueError, match="missing from translation"):
        hook.identify_left_out()

    assert "data/myapp.desktop.in" in capsys.readouterr().out


def test_identify_left_out_passes_when_nothing_is_listed(
    make_hook, project, fake_run
) -> None:
    hook = configured(make_hook, project)
    fake_run.stdout = ""
    hook.identify_left_out()
    assert len(fake_run.calls) == 1


@pytest.mark.parametrize(
    ("method", "flag"), [("regenerate_template", "-p"), ("show_report", "-r")]
)
def test_intltool_update_invocations(
    make_hook, project, fake_run, method: str, flag: str
) -> None:
    hook = configured(make_hook, project, **{"i18n-name": "photo-tool"})
    getattr(hook, method)()

    assert fake_run.cmd == ["intltool-update", flag, "-g", "photo-tool"]
    assert fake_run.kwargs["check"] is True
    assert fake_run.kwargs["cwd"] == project / "po"
