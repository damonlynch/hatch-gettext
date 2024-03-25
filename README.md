# Hatch Gettext

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![GitButler](https://img.shields.io/badge/GitButler-%23B9F4F2?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMzkiIGhlaWdodD0iMjgiIHZpZXdCb3g9IjAgMCAzOSAyOCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTI1LjIxNDUgMTIuMTk5N0wyLjg3MTA3IDEuMzg5MTJDMS41NDI5NSAwLjc0NjUzMiAwIDEuNzE0MDYgMCAzLjE4OTQ3VjI0LjgxMDVDMCAyNi4yODU5IDEuNTQyOTUgMjcuMjUzNSAyLjg3MTA3IDI2LjYxMDlMMjUuMjE0NSAxNS44MDAzQzI2LjcxOTcgMTUuMDcyMSAyNi43MTk3IDEyLjkyNzkgMjUuMjE0NSAxMi4xOTk3WiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTEzLjc4NTUgMTIuMTk5N0wzNi4xMjg5IDEuMzg5MTJDMzcuNDU3MSAwLjc0NjUzMiAzOSAxLjcxNDA2IDM5IDMuMTg5NDdWMjQuODEwNUMzOSAyNi4yODU5IDM3LjQ1NzEgMjcuMjUzNSAzNi4xMjg5IDI2LjYxMDlMMTMuNzg1NSAxNS44MDAzQzEyLjI4MDMgMTUuMDcyMSAxMi4yODAzIDEyLjkyNzkgMTMuNzg1NSAxMi4xOTk3WiIgZmlsbD0idXJsKCNwYWludDBfcmFkaWFsXzMxMF8xMjkpIi8%2BCjxkZWZzPgo8cmFkaWFsR3JhZGllbnQgaWQ9InBhaW50MF9yYWRpYWxfMzEwXzEyOSIgY3g9IjAiIGN5PSIwIiByPSIxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgZ3JhZGllbnRUcmFuc2Zvcm09InRyYW5zbGF0ZSgxNi41NzAxIDE0KSBzY2FsZSgxOS44NjQxIDE5LjgzODMpIj4KPHN0b3Agb2Zmc2V0PSIwLjMwMTA1NiIgc3RvcC1vcGFjaXR5PSIwIi8%2BCjxzdG9wIG9mZnNldD0iMSIvPgo8L3JhZGlhbEdyYWRpZW50Pgo8L2RlZnM%2BCjwvc3ZnPgo%3D)](https://gitbutler.com/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/damonlynch?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/damonlynch)
[![PyPI - Version](https://img.shields.io/pypi/v/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
-----

This provides a [build hook](https://hatch.pypa.io/latest/config/build/#build-hooks) plugin 
for [Hatch](https://github.com/pypa/hatch) that compiles multi-lingual messages with GNU 
gettext's tools `msgfmt` and (optionally) translates files using 
gettext's `intltool-merge`.

**Table of Contents**

- [Configuration](#configuration)
  - [Calling the plugin](#calling-the-plugin)
  - [Compiling messages with msgfmt](#compiling-messages-with-msgfmt)
  - [Translating files using intltool-merge](#translating-files-using-intltool-merge)
- [Cleaning output files](#cleaning-output-files)
- [License](#license)

## Configuration

The [build hook plugin](https://hatch.pypa.io/latest/plugins/build-hook/) 
name is `gettext`.

### Calling the plugin

Modify `pyproject.toml` to include the plugin as a build dependency:

```toml
[build-system]
requires = ["hatchling", "hatch-gettext"]
build-backend = "hatchling.build"
```

### Compiling messages with msgfmt
 
This plugin requires `.mo` files be created; it also requires that the 
directory storing them is within the project's base directory, and is not 
equal to the project's base directory or the directory in which `po` files
are sourced.  

For example, for a project named `myproject`, and a src layout 
`src/myproject`, an acceptable directory in which to store the 
`LC_MESSAGES/myproject.mo` files would be `src/myproject/locale`

```toml
[tool.hatch.build.hooks.gettext]
locale_directory = "src/myproject/locale"
```

Optionally, specify values for the gexttext output name
and the source directory where po files are found:

```toml
[tool.hatch.build.hooks.gettext]
locale_directory = "src/myproject/locale"
i18n_name = "myproject" 
po_directory = "po-files"
```

If `i18n_name` is not specified, the `name` in `[project]` in the 
`pyproject.toml` is used. If `po_directory` is not specified, the 
directory `po` is used.

### Translating files using intltool-merge

This plugin allows for but does not mandate translating `.xml` and 
`.desktop` files using `intltool-merge`. Using 
`[tool.hatch.build.hooks.gettext.files]`, specify the destination directories
for the translated files on the left, and arrays of source files on the 
right. For example:  

```toml
[tool.hatch.build.hooks.gettext.files]
"share/applications" = ["data/net.myproject.desktop.in"]
"share/solid/actions" = ["data/kde/net.myproject.desktop.in"]
"share/metainfo" = ["data/net.myproject.metainfo.xml.in"]
```

## Cleaning output files

The plugin includes logic to remove the files it outputs using hatch's
`clean` hook. As well as individual files, any output directories created 
will also be removed, as long as these directories do not contain files 
created by something other than this plugin.

## License

`hatch-gettext` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
