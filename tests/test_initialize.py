#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import sys
from collections.abc import Callable
from typing import Any

import pytest

from hatch_gettext.hooks import hatch_register_build_hook
from hatch_gettext.plugin import GettextBuildHook

CONFIG = {"locale-directory": "locale"}


def stubbed(
    make_hook, monkeypatch: pytest.MonkeyPatch, **kwargs: Any
) -> tuple[GettextBuildHook, list[dict[str, Any]]]:
    """A hook whose do_work() only records the build data it is handed."""

    config = {**CONFIG, **kwargs.pop("config", {})}
    hook = make_hook(config, **kwargs)
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(hook, "do_work", calls.append)
    return hook, calls


def quiet_do_work() -> Callable[[dict[str, Any]], None]:
    def stub(build_data: dict[str, Any]) -> None:
        build_data["artifacts"].append("stubbed")

    return stub


def test_initialize_skips_unknown_targets(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook, calls = stubbed(make_hook, monkeypatch, target_name="custom-target")
    hook.initialize("1.2.3", {"artifacts": []})
    assert calls == []


def test_initialize_skips_a_configured_platform(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    hook, calls = stubbed(
        make_hook,
        monkeypatch,
        target_name="wheel",
        config={**CONFIG, "skip-platforms": ["linux"]},
    )
    hook.initialize("1.2.3", {"artifacts": []})
    assert calls == []


def test_initialize_skips_whichever_platform_runs_the_tests(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook, calls = stubbed(
        make_hook,
        monkeypatch,
        target_name="wheel",
        config={**CONFIG, "skip-platforms": [sys.platform]},
    )
    hook.initialize("1.2.3", {"artifacts": []})
    assert calls == []


def test_initialize_runs_on_other_platforms(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    hook, calls = stubbed(
        make_hook,
        monkeypatch,
        target_name="wheel",
        config={**CONFIG, "skip-platforms": ["win32", "cygwin"]},
    )
    hook.initialize("1.2.3", {"artifacts": []})
    assert len(calls) == 1


def test_initialize_runs_without_the_option(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook, calls = stubbed(make_hook, monkeypatch, target_name="wheel")
    hook.initialize("1.2.3", {"artifacts": []})
    assert len(calls) == 1


def test_initialize_runs_for_an_sdist(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook, calls = stubbed(make_hook, monkeypatch, target_name="sdist")
    hook.initialize("1.2.3", {"artifacts": []})
    assert len(calls) == 1


def test_initialize_passes_the_build_data_through(
    make_hook, monkeypatch: pytest.MonkeyPatch
) -> None:
    hook, calls = stubbed(make_hook, monkeypatch, target_name="wheel")
    build_data = {"artifacts": []}
    hook.initialize("1.2.3", build_data)
    assert len(calls) == 1
    assert calls[0] is build_data


def test_verbose_builds_report_progress(
    make_hook, project, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    hook = make_hook(CONFIG, root=project, target_name="wheel", verbosity=2)
    monkeypatch.setattr(hook, "do_work", quiet_do_work())
    hook.initialize("1.2.3", {"artifacts": []})

    printed = capsys.readouterr().out
    assert "Building gettext translations" in printed
    assert "Finished building gettext translations" in printed


def test_quiet_builds_say_nothing(
    make_hook, project, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    hook = make_hook(CONFIG, root=project, target_name="wheel", verbosity=0)
    monkeypatch.setattr(hook, "do_work", quiet_do_work())
    hook.initialize("1.2.3", {"artifacts": []})
    assert capsys.readouterr().out == ""


def test_verbose_cleaning_reports_progress(make_hook, project, capsys) -> None:
    hook = make_hook(CONFIG, root=project, verbosity=2)
    hook.clean([])

    printed = capsys.readouterr().out
    assert "Cleaning gettext translations" in printed
    assert "Finished cleaning gettext translations" in printed


def test_hook_is_registered_as_the_gettext_plugin() -> None:
    assert hatch_register_build_hook() is GettextBuildHook
