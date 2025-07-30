# -*- coding: UTF-8 -*-
# Copyright 2016-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.projects.std.settings import *
from lino.api import _
import lino_prima
try:
    import bulma
except ImportError:
    bulma = None


class Site(Site):

    verbose_name = "Lino Prima"
    url = lino_prima.docs_url
    version = lino_prima.__version__

    demo_fixtures = ['std', 'demo', 'demo2', 'checkdata', 'checksummaries']
    user_types_module = 'lino_prima.lib.prima.user_types'
    migration_class = 'lino_prima.lib.prima.migrate.Migrator'
    textfield_bleached = False

    # preview_limit = 40
    default_build_method = 'weasy2pdf'
    catch_layout_exceptions = False
    with_uploads = True

    def get_installed_plugins(self):
        """Implements :meth:`lino.core.site.Site.get_installed_plugins`.

        """
        if bulma is not None:
            yield 'bulma'  # pip install django-bulma
        yield 'lino.modlib.system'
        yield 'lino_prima.lib.users'
        yield 'lino_prima.lib.prima'
        yield 'lino_prima.lib.school'
        yield 'lino_prima.lib.ratings'
        yield 'lino_prima.lib.projects'
        yield 'lino_prima.lib.cert'
        if self.with_uploads:
            yield 'lino.modlib.uploads'
        yield 'lino.modlib.checkdata'
        yield 'lino.modlib.summaries'
        yield 'lino.modlib.weasyprint'
        yield 'lino.modlib.export_excel'
        yield 'lino.modlib.help'  # ticket #6059 (lino.modlib.help depends on lino_xl)
        yield super().get_installed_plugins()

    def setup_quicklinks(self, ut, tb):
        super().setup_quicklinks(ut, tb)

    def get_plugin_configs(self):
        yield super().get_plugin_configs()
        yield ('users', 'with_nickname', True)
        if self.with_uploads:
            yield ('uploads', 'with_thumbnails', True)
        yield ('periods', 'start_year', 2024)
        yield ('periods', 'year_name', _("Academic year"))
        yield ('periods', 'year_name_plural', _("Academic years"))
        yield ('periods', 'period_name', _("Period"))
        yield ('periods', 'period_name_plural', _("Periods"))
        yield ('periods', 'start_month', 8)
        yield ('periods', 'period_type', 'semester')
