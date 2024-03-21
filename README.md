# Hatch Gettext

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-gettext.svg)](https://pypi.org/project/hatch-gettext)

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
