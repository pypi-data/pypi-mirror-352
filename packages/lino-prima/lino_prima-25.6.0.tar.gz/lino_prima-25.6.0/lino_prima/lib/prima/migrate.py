# -*- coding: UTF-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Default data migrator for Lino Prima.


"""

from django.conf import settings
from lino.api import dd, rt
from lino.utils.dpy import Migrator, override


class Migrator(Migrator):
    """The standard migrator for Lino Prima.

    This is used because
    :class:`lino_prima.projects.prima.settings.Site` has
    :attr:`migration_class <lino.core.site.Site.migration_class>` set
    to ``"lino_prima.lib.prima.migrate.Migrator"``.

    """

    def migrate_from_0_0_1(self, globals_dict):
        # do something here
        return '0.0.2'
