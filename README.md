# Hatch Gettext

| |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --- |----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Package | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext) [![PyPI - Version](https://img.shields.io/pypi/v/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Meta | [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![GitButler](https://img.shields.io/badge/GitButler-%23B9F4F2?logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMzkiIGhlaWdodD0iMjgiIHZpZXdCb3g9IjAgMCAzOSAyOCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTI1LjIxNDUgMTIuMTk5N0wyLjg3MTA3IDEuMzg5MTJDMS41NDI5NSAwLjc0NjUzMiAwIDEuNzE0MDYgMCAzLjE4OTQ3VjI0LjgxMDVDMCAyNi4yODU5IDEuNTQyOTUgMjcuMjUzNSAyLjg3MTA3IDI2LjYxMDlMMjUuMjE0NSAxNS44MDAzQzI2LjcxOTcgMTUuMDcyMSAyNi43MTk3IDEyLjkyNzkgMjUuMjE0NSAxMi4xOTk3WiIgZmlsbD0iYmxhY2siLz4KPHBhdGggZD0iTTEzLjc4NTUgMTIuMTk5N0wzNi4xMjg5IDEuMzg5MTJDMzcuNDU3MSAwLjc0NjUzMiAzOSAxLjcxNDA2IDM5IDMuMTg5NDdWMjQuODEwNUMzOSAyNi4yODU5IDM3LjQ1NzEgMjcuMjUzNSAzNi4xMjg5IDI2LjYxMDlMMTMuNzg1NSAxNS44MDAzQzEyLjI4MDMgMTUuMDcyMSAxMi4yODAzIDEyLjkyNzkgMTMuNzg1NSAxMi4xOTk3WiIgZmlsbD0idXJsKCNwYWludDBfcmFkaWFsXzMxMF8xMjkpIi8%2BCjxkZWZzPgo8cmFkaWFsR3JhZGllbnQgaWQ9InBhaW50MF9yYWRpYWxfMzEwXzEyOSIgY3g9IjAiIGN5PSIwIiByPSIxIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSIgZ3JhZGllbnRUcmFuc2Zvcm09InRyYW5zbGF0ZSgxNi41NzAxIDE0KSBzY2FsZSgxOS44NjQxIDE5LjgzODMpIj4KPHN0b3Agb2Zmc2V0PSIwLjMwMTA1NiIgc3RvcC1vcGFjaXR5PSIwIi8%2BCjxzdG9wIG9mZnNldD0iMSIvPgo8L3JhZGlhbEdyYWRpZW50Pgo8L2RlZnM%2BCjwvc3ZnPgo%3D)](https://gitbutler.com/) [![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) [![GitHub Sponsors](https://img.shields.io/github/sponsors/damonlynch?logo=GitHub%20Sponsors&style=social)](https://github.com/sponsors/damonlynch)  |


-----

This provides a [build hook](https://hatch.pypa.io/latest/config/build/#build-hooks) plugin 
for [Hatch](https://github.com/pypa/hatch) that compiles multi-lingual messages with GNU 
gettext's tools `msgfmt`. It can also (optionally) use `intltool` to: 
- translate .xml and .desktop files
- search for left out files
- regenerate the .pot template 
- display a status report for all translations

**Table of Contents**

<!-- TOC -->
* [Hatch Gettext](#hatch-gettext)
  * [Configuration](#configuration)
    * [Calling the plugin](#calling-the-plugin)
    * [Compiling messages with msgfmt](#compiling-messages-with-msgfmt)
    * [Identifying left out files using intltool-update](#identifying-left-out-files-using-intltool-update)
    * [Regenerating the .pot template using intltool-update](#regenerating-the-pot-template-using-intltool-update)
    * [Displaying a status report using intltool-update](#displaying-a-status-report-using-intltool-update)
    * [Translating files using intltool-merge](#translating-files-using-intltool-merge)
  * [Cleaning output files](#cleaning-output-files)
  * [Related Hatch plugin](#related-hatch-plugin)
  * [License](#license)
<!-- TOC -->

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
are sourced. The mo file directory is set using `locale-directory`, which is 
required. 

For example, for a project named `myproject`, and a src layout 
`src/myproject`, an acceptable directory in which to store the 
`LC_MESSAGES/myproject.mo` files would be `src/myproject/locale`

```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
```

Optionally, specify values for the gexttext output name
and the source directory where po files are found:

```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
i18n-name = "myproject" 
po-directory = "po-files"
```

If `i18n-name` is not specified, the `name` in `[project]` in the 
`pyproject.toml` is used. If `po-directory` is not specified, the 
directory `po` is used.

### Identifying left out files using intltool-update

With every source distribution (sdist) build, to search for left out files, 
which should have been listed in `POTFILES.in` or `POTFILES.skip`, set 
`identify-left-out` to true (the default value is false):

```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
identify-left-out = true
```

### Regenerating the .pot template using intltool-update

To regenerate the .pot template with every sdist build, set 
`regenerate-template` to true (the default value is false):

```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
regenerate-template = true
```

### Displaying a status report using intltool-update

To display a status report for all translations, set `show-report` to true 
(the default value is false):

```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
show-report = true
```

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

## Related Hatch plugin

To automatically generate a manual page from an `ArgumentParser` object,
see [hatch-argparse-manpage](https://github.com/damonlynch/hatch-argparse-manpage).

## License

`hatch-gettext` is distributed under the terms of the [GPL-3.0-or-later](https://spdx.org/licenses/GPL-3.0-or-later.html) license.
