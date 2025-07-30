# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""
The certificates plugin for Lino Prima.
"""

from lino.ad import Plugin, _


class Plugin(Plugin):

    verbose_name = _("Certificates")
    menu_group = "cert"
    needs_plugins = ['lino.modlib.printing']

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('cert.CertTemplates')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('cert.CertSections')
        m.add_action('cert.CertElements')
        m.add_action('cert.Certificates')
        m.add_action('cert.AllSectionResponses')
        m.add_action('cert.AllElementResponses')
