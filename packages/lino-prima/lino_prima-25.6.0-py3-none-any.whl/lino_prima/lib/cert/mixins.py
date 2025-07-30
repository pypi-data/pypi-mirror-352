# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from lino.api import dd, _
from lino_prima.lib.school.roles import PrimaStaff, PrimaTeacher



class CertificateStates(dd.ChoiceList):
    verbose_name = _("Certificate state")
    verbose_name_plural = _("Certificate states")

add = CertificateStates.add_item
add("1", _("Draft"), "default")  # Unfertig -> Entwurf
add("2", _("To discuss"))  # Zu besprechen
add("3", _("Ready"))       # Fertig
