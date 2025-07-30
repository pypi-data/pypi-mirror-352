# -*- coding: UTF-8 -*-
# Copyright 2016-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""Defines the standard user roles for Lino Prima."""

from lino.core.roles import UserRole, SiteAdmin, SiteUser, SiteStaff
from lino.modlib.users.choicelists import UserTypes
from lino.modlib.office.roles import OfficeStaff
from django.utils.translation import gettext_lazy as _

from lino_prima.lib.school.roles import PrimaPupil, PrimaTeacher, PrimaStaff

class Pupil(SiteUser, PrimaPupil): pass
class Teacher(SiteUser, PrimaTeacher): pass
class SiteStaff(SiteStaff, PrimaStaff, OfficeStaff): pass
class SiteAdmin(SiteAdmin, SiteStaff): pass

UserTypes.clear()
add = UserTypes.add_item
add('000',
    _("Anonymous"),
    UserRole,
    'anonymous',
    readonly=True,
    authenticated=False)
add('100', _("User"), SiteUser, 'user')
add('200', _("Teacher"), Teacher, 'teacher')
add('300', _("Pupil"), Pupil, 'pupil')
add('500', _("Staff"), SiteStaff, 'staff')
add('900', _("Administrator"), SiteAdmin, 'admin')


from django.conf import settings
settings.SITE.models.periods.PeriodTypes.semester.ref_template = "{period}"
