# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino_prima.lib.prima.settings import *


class Site(Site):

    is_demo_site = True
    # the_demo_date = 20241009
    the_demo_date = 20250206
    languages = "en de"
    # languages = "de"
    default_ui = 'lino_react.react'
    demo_fixtures = ["std", "demo", "demo2", "checkdata"]
    site_locale = "de_BE.UTF-8"

    def get_plugin_configs(self):
        yield ('checkdata', 'responsible_user', 'rolf')
        yield super().get_plugin_configs()


SITE = Site(globals())

DEBUG = True
USE_TZ = False
# TIME_ZONE = 'UTC'
