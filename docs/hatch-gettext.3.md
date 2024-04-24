% hatch-gettext(3) | Hatch build hook plugin for GNU gettext

# NAME

hatch-gettext

# SYNOPSIS

Modify `pyproject.toml`:

```
[build-system]
requires = ["hatchling", "hatch-gettext"]
build-backend = "hatchling.build"

[tool.hatch.build.hooks.gettext]
locale-directory = "RELATIVE MO FILE DIRECTORY"
i18n-name = "GETTEXT OUTPUT NAME"
po-directory = "RELATIVE PO FILE DIRECTORY"
identify-left-out = BOOLEAN
regenerate-template = BOOLEAN
show-report = BOOLEAN

[tool.hatch.build.hooks.gettext.files]
"RELATIVE DIRECTORY" = ["RELATIVE FILE PATH", ]
```

# DESCRIPTION

**Hatch-gettext** provides a build hook plugin for Hatch that compiles multi-lingual messages with GNU gettext's tools _msgfmt_.
It can also (optionally) use _intltool_ to:

- search for left out files
- regenerate the .pot template 
- display a status report for all translations
- translate .xml and .desktop files

## Directory layout
This plugin requires that the directory storing generated _mo_ files is within the 
project's base directory, and is not equal to the project's base directory or the 
directory in which _po_ files are sourced.

For example, for a project named _myproject_, and a src layout 
_src/myproject_, an acceptable directory in which to store the 
_LC_MESSAGES/myproject.mo_ files would be _src/myproject/locale_.

## Required key value

`locale-directory`

: The destination directory in which _mo_ files and their associated subdirectories will be generated into.

## Optional key values

`i18n-name`

: The gexttext output name. The default is *name* in *[project]* in the *pyproject.toml*.

`po-directory`

:  The source directory where po files are found. The default is *po*.

`identify-left-out`

: Boolean specifying whether to use _intltool-update_ to search for left out files which should have been listed in _POTFILES.in_ or _POTFILES.skip_. The default is _false_.

`regenerate-template`

: Boolean specifying whether to use _intltool-update_ to regenerate the .pot template with every sdist build. The default is _false_.


`show-report`

: Boolean specifying whether to use _intltool-update_ to display a status report for all translations. The default is _false_.

## Translating files using intltool-merge

This plugin allows for but does not mandate translating _.xml_ and 
_.desktop_ files using _intltool-merge_. Using 
_\[tool.hatch.build.hooks.gettext.files]_ in _pyproject.toml_, specify the destination directories
for the translated files using keys, and arrays of source files as values. 


## Cleaning output files

The plugin includes logic to remove the files it outputs using hatch's
`clean` hook. As well as individual files, any output directories created 
will also be removed, as long as these directories do not contain files 
created by something other than this plugin.

# EXAMPLES

Compiling messages with msgfmt:
```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
```

Identifying left out files using intltool-update:
```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
identify-left-out = true
```

Regenerating the .pot template using intltool-update:
```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
regenerate-template = true
```

Displaying a status report using intltool-update:
```toml
[tool.hatch.build.hooks.gettext]
locale-directory = "src/myproject/locale"
show-report = true
```

Translating files using intltool-merge:
```toml
[tool.hatch.build.hooks.gettext.files]
"share/applications" = ["data/net.myproject.desktop.in"]
"share/solid/actions" = ["data/kde/net.myproject.desktop.in"]
"share/metainfo" = ["data/net.myproject.metainfo.xml.in"]
```

# AUTHOR

Damon Lynch <damonlynch@gmail.com>

# COPYRIGHT

Copyright 2024 Damon Lynch.
