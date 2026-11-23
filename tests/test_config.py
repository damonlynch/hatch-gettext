#  SPDX-FileCopyrightText: 2024-2026 Damon Lynch <damonlynch@gmail.com>
#  SPDX-License-Identifier: GPL-3.0-or-later

import pytest

SECTION = "[tool.hatch.build.hooks.gettext]"


def test_po_directory_defaults_to_po(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook._po_dir == project / "po"


def test_custom_po_directory_is_honoured(make_hook, project) -> None:
    (project / "translations").mkdir()
    hook = make_hook(
        {"po-directory": "translations", "locale-directory": "locale"}, root=project
    )
    hook.load_gettextbuild_config()
    assert hook._po_dir == project / "translations"


def test_locale_directory_is_relative_to_the_project_root(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "build/i18n"}, root=project)
    hook.load_gettextbuild_config()
    assert hook._locale_dir == project / "build" / "i18n"


def test_i18n_name_defaults_to_the_project_name(make_hook, project) -> None:
    hook = make_hook(
        {"locale-directory": "locale"},
        root=project,
        project_name="rapid-photo-downloader",
    )
    hook.load_gettextbuild_config()
    assert hook._i18n_name == "rapid-photo-downloader"


def test_i18n_name_can_be_overridden(make_hook, project) -> None:
    hook = make_hook(
        {"locale-directory": "locale", "i18n-name": "other"},
        root=project,
        project_name="myapp",
    )
    hook.load_gettextbuild_config()
    assert hook._i18n_name == "other"


def test_optional_booleans_default_to_false(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook._identify_left_out is False
    assert hook._regenerate_template is False
    assert hook._show_report is False


def test_optional_booleans_are_read(make_hook, project) -> None:
    hook = make_hook(
        {
            "locale-directory": "locale",
            "identify-left-out": True,
            "regenerate-template": True,
            "show-report": True,
        },
        root=project,
    )
    hook.load_gettextbuild_config()
    assert hook._identify_left_out is True
    assert hook._regenerate_template is True
    assert hook._show_report is True


def test_files_is_unset_when_unconfigured(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    assert hook._gtb_files is None


def test_files_are_read(make_hook, project) -> None:
    files = {"data": ["data/myapp.desktop.in"]}
    hook = make_hook({"locale-directory": "locale", "files": files}, root=project)
    hook.load_gettextbuild_config()
    assert hook._gtb_files == files


def test_config_name_identifies_the_toml_section(make_hook) -> None:
    assert make_hook({}).config_name() == SECTION


def test_missing_po_directory_is_reported(make_hook, tmp_path) -> None:
    hook = make_hook({"locale-directory": "locale"}, root=tmp_path / "empty")
    with pytest.raises(ValueError, match="po-directory"):
        hook.load_gettextbuild_config()


def test_missing_locale_directory_is_reported(make_hook, project) -> None:
    hook = make_hook({}, root=project)
    with pytest.raises(ValueError, match="locale-directory") as exc_info:
        hook.load_gettextbuild_config()
    # Users are told which configuration section to fix
    assert SECTION in str(exc_info.value)


def test_empty_locale_directory_is_reported(make_hook, project) -> None:
    hook = make_hook({"locale-directory": ""}, root=project)
    with pytest.raises(ValueError, match="locale-directory"):
        hook.load_gettextbuild_config()


def test_locale_directory_cannot_be_the_project_root(make_hook, project) -> None:
    hook = make_hook({"locale-directory": "."}, root=project)
    with pytest.raises(ValueError, match="root directory"):
        hook.load_gettextbuild_config()


def test_locale_directory_cannot_be_the_po_directory(make_hook, project) -> None:
    hook = make_hook({"po-directory": "po", "locale-directory": "po"}, root=project)
    with pytest.raises(ValueError, match="different from the po directory"):
        hook.load_gettextbuild_config()


def test_configuration_survives_a_second_load(make_hook, project) -> None:
    # initialize() and clean() each load the configuration during one build
    hook = make_hook({"locale-directory": "locale"}, root=project)
    hook.load_gettextbuild_config()
    first = hook._locale_dir
    hook.load_gettextbuild_config()
    assert hook._locale_dir == first
    assert hook._locale_dir == project / "locale"
