# SPDX-FileCopyrightText: Copyright 2024 Damon Lynch <damonlynch@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import functools
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from rich.console import Console


class GettextBuildHook(BuildHookInterface):
    """
    Compile GNU gettext translation files from po-format into
    mo-format using the GNU gettext utility msgfmt, and optionally translate files
    using the GNU gettext utility intltool-merge.

    Cleans up any files that it creates, and any resulting directories, but
    only if the directories are empty.
    """

    PLUGIN_NAME = "gettext"

    GETTEXT_SWITCHES = {
        ".xml": "-x",
        ".desktop": "-d",
    }

    def config_name(self) -> str:
        return f"[tool.hatch.build.hooks.{self.PLUGIN_NAME}]"

    @staticmethod
    def _assemble_command(cmd: str) -> list[str] | str:
        if sys.platform == "win32":
            return cmd
        return shlex.split(cmd)

    def _compile_po_to_mo(self, po_file: Path, mo_file: Path) -> None:
        """
        Compile po-file to mo-file using the GNU gettext utility msgfmt

        :param po_file: the full path to the po file
        :param mo_file: the full path to the mo file
        """

        cmd = self._assemble_command(f"msgfmt --output-file={mo_file} {po_file}")
        process = subprocess.run(cmd, text=True, capture_output=True)
        if process.returncode:
            raise Exception(f"Error while invoking msgfmt:\n{process.stdout}")

    def _translate_file(
        self, po_dir: Path, in_file: Path, translated_file: Path
    ) -> None:
        """
        Translate a .desktop or .xml file using the GNU gettext utility intltool-merge

        :param po_dir: directory containing the po files
        :param in_file: the full path to the .desktop.in or .xml.in file
        :param translated_file: the full path to the output .desktop or .xml file
        """

        file_extension = in_file.suffixes[-2]
        switch = self.GETTEXT_SWITCHES[file_extension]
        cmd = self._assemble_command(
            f"intltool-merge {switch} {po_dir} {in_file} {translated_file}"
        )
        process = subprocess.run(cmd, text=True, capture_output=True)
        if process.returncode:
            raise Exception(f"Error while invoking intltool-merge:\n{process.stdout}")

    def _clean_files(self, relative_file_paths: list[str]) -> None:
        project_root: Path = Path(self.root)
        for p in relative_file_paths:
            full_path = project_root / p
            if full_path.exists():
                self.console_output(
                    f"Removing {full_path}", level=2, style=self._style_level_debug
                )
                full_path.unlink()

    def _has_only_subdirectories(self, path: Path) -> bool:
        """
        Checks if a directory has only subdirectories and no files.

        :param path: the full path to the directory to check
        :return: True if the directory has only subdirectories and no files
        """

        for entry in path.iterdir():
            if entry.is_file():
                return False
            # Recursively check subdirectories
            if entry.is_dir() and not self._has_only_subdirectories(entry):
                return False
        return True

    def _clean_directory_tree_only_if_has_empty_subdirectories(
        self, folder: Path
    ) -> None:
        """
        Removes a directory tree only if it contains no files and any of its
        subdirectories in its tree likewise contain no files

        :param folder: full path of the directory
        """

        if folder.is_dir() and self._has_only_subdirectories(folder):
            self.console_output(
                f"Removing {folder}", level=2, style=self._style_level_debug
            )
            shutil.rmtree(folder)

    def clean(self, versions: list[str]) -> None:
        """
        Remove all files created by this plug-in, if they exist.

        Remove all their directories only they contain no other files,
        with the same being true of their subdirectories.

        :param versions: see Hatch documentation for details
        """

        self.setup_console()
        self.console_output(
            "Cleaning gettext translations", level=1, style=self._style_level_waiting
        )

        self.load_gettextbuild_config()

        if self._locale_dir.is_dir():
            self._clean_files(self.mo_files_to_build)

        if self._gtb_files:
            self._clean_files(self.translate_files_to_build)

        self._clean_directory_tree_only_if_has_empty_subdirectories(self._locale_dir)

        project_root = Path(self.root)
        for translated_file in self.translate_files_to_build:
            folders = (project_root / p for p in Path(translated_file).parents)
            translated_subfolders = filter(lambda p: p != project_root, folders)
            for folder in translated_subfolders:
                self._clean_directory_tree_only_if_has_empty_subdirectories(folder)
        self.console_output(
            "Finished cleaning gettext translations",
            level=1,
            style=self._style_level_success,
        )

    def load_gettextbuild_config(self) -> None:
        """
        Load the gettextbuild config from pyproject.toml using hatch's interface
        and assign the values to private class variables.
        """

        self._i18n_name: str = self.config.get("i18n-name") or self.metadata.name
        self._identify_left_out: bool = self.config.get("identify-left-out", False)
        self._regenerate_template: bool = self.config.get("regenerate-template", False)
        self._show_report: bool = self.config.get("show-report", False)

        project_root = Path(self.root)

        self._po_dir = project_root / (self.config.get("po-directory", "po"))
        if not self._po_dir.is_dir():
            raise ValueError(
                f'Configure "po-directory" in "{self.config_name()}" in pyproject.toml '
                'to the project\'s po directory [default: "po"], and ensure the '
                "directory exists."
            )
        try:
            self._locale_dir = project_root / self.config["locale-directory"]
        except KeyError:
            raise ValueError(
                f'Configure "locale-directory" in "{self.config_name()}" in '
                "pyproject.toml to the directory in which compiled mo files will be "
                "written to."
            )
        try:
            assert self._locale_dir != project_root
        except AssertionError:
            raise ValueError(
                "The locale directory must be different from the project's root "
                "directory."
            )
        try:
            assert self._po_dir != self._locale_dir
        except AssertionError:
            raise ValueError(
                "The locale directory must be different from the po directory."
            )

        self._gtb_files = self.config.get("files")

    @functools.cache
    def po_mo_pairs(self) -> list[tuple[Path, str]]:
        """
        :return: a list of tuples containing po files, and their corresponding mo
         filenames that the build will create.

         Each po file will be a full Path, but the mo files' path will be a string
         whose path is relative to the project root.

         If a LINGUAS file is found in the po directory or as an environment variable,
         only specified po files will be included.
        """

        filter_languages: list[str] = []
        linguas_file = self._po_dir / "LINGUAS"
        if linguas_file.is_file():
            with open(linguas_file) as f:
                filter_languages = f.read().split()
        if "LINGUAS" in os.environ:
            filter_languages = os.environ["LINGUAS"].split()

        po_files = self._po_dir.glob("*.po")
        if filter_languages:
            po_files = (p for p in po_files if p.stem in filter_languages)

        po_files = list(po_files)
        po_files.sort()

        return [
            (
                Path(po_file),
                str(
                    Path(self.config["locale-directory"])
                    / po_file.stem
                    / "LC_MESSAGES"
                    / f"{self._i18n_name}.mo"
                ),
            )
            for po_file in po_files
        ]

    @functools.cache
    def translate_file_pairs(self) -> list[tuple[Path, str]]:
        """
        :return: a list of tuples containing .in files, and their corresponding
         files to be translated by intltool-merge that the build will create.

         Each .in file will be a full Path, but the translated files' path will be a
         string whose path is relative to the project root.
        """

        if self._gtb_files is None:
            return []

        project_root: Path = Path(self.root)
        files_to_build = []
        for folder, files in self._gtb_files.items():
            for in_file in files:
                translated_file = Path(folder) / Path(in_file).stem
                files_to_build.append((project_root / in_file, str(translated_file)))
        return files_to_build

    @property
    def mo_files_to_build(self) -> list[str]:
        """
        :return: a list of mo filenames with relative paths that the build will create
        """

        return [pair[1] for pair in self.po_mo_pairs()]

    @property
    def translate_files_to_build(self) -> list[str]:
        """
        :return: a list of files translated by intltool-merge that the build will create

         Each file's path will be a string whose path is relative to the project root.
        """

        return [pair[1] for pair in self.translate_file_pairs()]

    def compile_mo_files(self) -> None:
        """
        Compile .po files into .mo files using msgfmt
        """

        project_root: Path = Path(self.root)

        for po_file, m in self.po_mo_pairs():
            self.console_output(f'Compiling "{po_file.name}"', level=2)
            mo_file = project_root / m
            mo_file.parent.mkdir(parents=True, exist_ok=True)
            self._compile_po_to_mo(po_file, mo_file)

    def translate_files(self) -> None:
        """
        Translate .desktop and .xml files using intltool-merge
        """

        project_root: Path = Path(self.root)
        for in_file, to_translate in self.translate_file_pairs():
            path_to_translate = project_root / to_translate
            path_to_translate.parent.mkdir(parents=True, exist_ok=True)
            self.console_output(f'Translating "{path_to_translate.stem}"', level=2)
            self._translate_file(self._po_dir, in_file, path_to_translate)

    def identify_left_out(self) -> None:
        cmd = self._assemble_command("intltool-update -m")
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=self._po_dir,
        )
        if p.stdout:
            self.console_output(p.stdout, level=0, style=self._style_level_error)
            raise ValueError("Files missing from translation template")

    def regenerate_template(self) -> None:
        cmd = self._assemble_command(f"intltool-update -p -g {self._i18n_name}")
        self.console_output(
            "Regenerating .pot template", level=2, style=self._style_level_debug
        )
        subprocess.run(cmd, check=True, cwd=self._po_dir)

    def show_report(self) -> None:
        cmd = self._assemble_command(f"intltool-update -r -g {self._i18n_name}")
        self.console_output("Generating report", level=2, style=self._style_level_debug)
        subprocess.run(cmd, check=True, cwd=self._po_dir)

    def do_work(self, build_data: dict[str, Any]) -> None:
        self.load_gettextbuild_config()

        if self.target_name == "sdist":
            if self._identify_left_out:
                self.identify_left_out()
            if self._regenerate_template:
                self.regenerate_template()
            if self._show_report:
                self.show_report()

        build_data["artifacts"].extend(self.mo_files_to_build)
        self.compile_mo_files()

        if self._gtb_files:
            build_data["artifacts"].extend(self.translate_files_to_build)
            self.translate_files()

    def setup_console(self) -> None:
        if self.app.verbosity < 0:
            return
        self.console = Console(force_terminal=True, force_interactive=False)

        # Match default Hatch color config:
        self._style_level_success = "bold cyan"
        self._style_level_error = "bold red"
        self._style_level_warning = "bold yellow"
        self._style_level_waiting = "bold magenta"
        self._style_level_info = "bold"
        self._style_level_debug = "bold"

    def console_output(self, message: str, level: int = 0, style: str = "") -> None:
        if self.app.verbosity < level:
            return
        self.console.print(message, style=style)

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        if self.target_name not in ["wheel", "sdist"]:
            return

        self.setup_console()
        self.console_output(
            "Building gettext translations", level=1, style=self._style_level_waiting
        )
        self.do_work(build_data)
        self.console_output(
            "Finished building gettext translations",
            level=1,
            style=self._style_level_success,
        )
