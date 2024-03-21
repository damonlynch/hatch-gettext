# SPDX-FileCopyrightText: Copyright 2024 Damon Lynch <damonlynch@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from hatchling.plugin import hookimpl

from hatch_gettext.plugin import GettextBuildHook


@hookimpl
def hatch_register_build_hook():
    return GettextBuildHook
