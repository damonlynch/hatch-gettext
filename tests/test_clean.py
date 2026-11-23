#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

import pytest

FILES = {"data": ["data/myapp.desktop.in", "data/myapp.xml.in"]}


def mo_files(root: Path, directory: str = "locale") -> list[Path]:
    """The mo paths the build would create, created on disk as placeholders."""

    paths = [
        root / directory / language / "LC_MESSAGES" / "myapp.mo"
        for language in ("es", "fr")
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"placeholder")
    return paths


def test_clean_removes_the_compiled_mo_files(make_hook, project) -> None:
    created = mo_files(project)
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.clean([])

    assert all(not path.exists() for path in created)
    assert (project / "po" / "es.po").is_file()


def test_clean_prunes_the_empty_locale_tree(make_hook, project) -> None:
    mo_files(project, "build/i18n")
    hook = make_hook({"locale-directory": "build/i18n"}, root=project)
    hook.clean([])

    assert not (project / "build" / "i18n").exists()
    # The locale directory's own parent is left in place
    assert project.is_dir()


def test_clean_keeps_directories_holding_other_files(make_hook, project) -> None:
    created = mo_files(project)
    keeper = project / "locale" / "es" / "LC_MESSAGES" / "keep.mo"
    keeper.write_bytes(b"not mine")
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.clean([])

    assert all(not path.exists() for path in created)
    assert (project / "locale" / "es" / "LC_MESSAGES").is_dir()
    assert keeper.is_file()


def test_clean_removes_merged_translations(make_hook, project) -> None:
    merged = project / "data" / "myapp.desktop"
    merged.parent.mkdir(parents=True, exist_ok=True)
    merged.write_text("Name=left over\n", encoding="utf-8")
    hook = make_hook({"locale-directory": "locale", "files": FILES}, root=project)
    hook.clean([])

    assert not merged.exists()
    # The destination still holds the translatable templates
    assert (project / "data" / "myapp.desktop.in").is_file()


def test_clean_prunes_an_emptied_destination_directory(make_hook, project) -> None:
    merged = project / "data" / "myapp.desktop"
    merged.parent.mkdir(parents=True, exist_ok=True)
    merged.write_text("Name=left over\n", encoding="utf-8")
    for template in (project / "data").glob("*.in"):
        template.unlink()
    hook = make_hook({"locale-directory": "locale", "files": FILES}, root=project)
    hook.clean([])

    assert not (project / "data").exists()


def test_clean_tolerates_nothing_having_been_built(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale", "files": FILES}, root=project)
    hook.clean([])

    assert not (project / "locale").exists()
    assert (project / "po").is_dir()
    assert (project / "data" / "myapp.desktop.in").is_file()


def test_clean_requires_a_valid_configuration(make_hook, project) -> None:
    hook = make_hook({}, root=project)
    with pytest.raises(ValueError, match="locale-directory"):
        hook.clean([])


def test_clean_files_ignores_paths_that_are_absent(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook._clean_files([str(Path("locale") / "no-such" / "myapp.mo")])
    assert not (project / "locale").exists()


def test_has_only_subdirectories_for_an_empty_tree(make_hook, tmp_path) -> None:
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    hook = make_hook({})
    assert hook._has_only_subdirectories(tmp_path / "a")


def test_has_only_subdirectories_is_false_for_a_file(make_hook, tmp_path) -> None:
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    (nested / "f.txt").write_text("x", encoding="utf-8")
    hook = make_hook({})
    assert not hook._has_only_subdirectories(tmp_path / "a")


def test_has_only_subdirectories_is_false_for_a_lone_file(make_hook, tmp_path) -> None:
    (tmp_path / "f.txt").write_text("x", encoding="utf-8")
    hook = make_hook({})
    assert not hook._has_only_subdirectories(tmp_path)


def test_clean_leaves_the_tree_when_a_file_remains(make_hook, project) -> None:
    mo_files(project)
    (project / "locale" / "es" / "notes.txt").write_text("keep", encoding="utf-8")
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.clean([])

    assert (project / "locale").is_dir()
    assert (project / "locale" / "es" / "notes.txt").is_file()
    assert not (project / "locale" / "es" / "LC_MESSAGES" / "myapp.mo").exists()
