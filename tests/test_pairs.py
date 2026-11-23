#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import pytest


def mo_path(language: str, name: str = "myapp", directory: str = "locale") -> str:
    """The mo filename the build derives for a language, as a relative path."""

    return str(Path(directory) / language / "LC_MESSAGES" / f"{name}.mo")


def test_one_pair_per_po_file_in_sorted_order(make_hook, project) -> None:
    (project / "po" / "de.po").touch()
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    pairs = hook.po_mo_pairs()

    assert [po.name for po, _ in pairs] == ["de.po", "es.po", "fr.po"]
    assert [mo for _, mo in pairs] == [mo_path("de"), mo_path("es"), mo_path("fr")]
    assert all(po.is_file() for po, _ in pairs)


def test_po_files_are_absolute_paths(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert all(po.parent == project / "po" for po, _ in hook.po_mo_pairs())


def test_i18n_name_appears_in_the_mo_filename(make_hook, project) -> None:
    config = {"locale-directory": "build/i18n", "i18n-name": "rapid-photo-downloader"}
    hook = make_hook(config, root=project)
    hook.load_gettextbuild_config()
    assert [mo for _, mo in hook.po_mo_pairs()] == [
        mo_path("es", "rapid-photo-downloader", "build/i18n"),
        mo_path("fr", "rapid-photo-downloader", "build/i18n"),
    ]


def test_linguas_file_restricts_the_languages(make_hook, project) -> None:
    (project / "po" / "LINGUAS").write_text("fr\n", encoding="utf-8")
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert [mo for _, mo in hook.po_mo_pairs()] == [mo_path("fr")]


def test_linguas_accepts_several_languages_and_blank_lines(make_hook, project) -> None:
    (project / "po" / "LINGUAS").write_text("es\n\n fr \n", encoding="utf-8")
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert [po.name for po, _ in hook.po_mo_pairs()] == ["es.po", "fr.po"]


def test_linguas_environment_variable_overrides_the_file(
    make_hook, project, monkeypatch: pytest.MonkeyPatch
) -> None:
    (project / "po" / "LINGUAS").write_text("fr\n", encoding="utf-8")
    monkeypatch.setenv("LINGUAS", "es")
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert [po.name for po, _ in hook.po_mo_pairs()] == ["es.po"]


def test_an_empty_po_directory_yields_nothing(make_hook, tmp_path) -> None:
    (tmp_path / "po").mkdir()
    hook = make_hook({"locale-directory": "locale"}, root=tmp_path)
    hook.load_gettextbuild_config()
    assert hook.po_mo_pairs() == []
    assert hook.mo_files_to_build == []


def test_mo_files_to_build_lists_the_relative_paths(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook.mo_files_to_build == [mo_path("es"), mo_path("fr")]


def test_pairs_are_memoised(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook.po_mo_pairs() is hook.po_mo_pairs()
    assert hook.translate_file_pairs() is hook.translate_file_pairs()


def test_memoisation_does_not_leak_between_instances(make_hook, project) -> None:
    config = {"locale-directory": "locale"}
    first = make_hook(config, root=project)
    first.load_gettextbuild_config()
    second = make_hook(config, root=project)
    second.load_gettextbuild_config()
    assert first.po_mo_pairs() == second.po_mo_pairs()
    assert first.po_mo_pairs() is not second.po_mo_pairs()


def test_translated_file_pairs(make_hook, project) -> None:
    files = {"data": ["data/myapp.desktop.in", "data/myapp.xml.in"]}
    hook = make_hook({"locale-directory": "locale", "files": files}, root=project)
    hook.load_gettextbuild_config()
    pairs = hook.translate_file_pairs()

    assert [in_file.name for in_file, _ in pairs] == [
        "myapp.desktop.in",
        "myapp.xml.in",
    ]
    assert [translated for _, translated in pairs] == [
        str(Path("data") / "myapp.desktop"),
        str(Path("data") / "myapp.xml"),
    ]
    assert all(in_file.is_file() for in_file, _ in pairs)


def test_translated_file_pairs_across_destinations(make_hook, project) -> None:
    (project / "other").mkdir()
    files = {
        "data": ["data/myapp.desktop.in"],
        "other": ["data/myapp.xml.in"],
    }
    hook = make_hook({"locale-directory": "locale", "files": files}, root=project)
    hook.load_gettextbuild_config()
    assert hook.translate_files_to_build == [
        str(Path("data") / "myapp.desktop"),
        str(Path("other") / "myapp.xml"),
    ]


def test_translate_files_to_build_is_empty_without_files(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook.translate_file_pairs() == []
    assert hook.translate_files_to_build == []
