# Copyright 2015-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.core.roles import UserRole

class PrimaUser(UserRole): pass
class PrimaPupil(PrimaUser): pass
class PrimaTeacher(PrimaUser): pass
class PrimaStaff(PrimaTeacher, PrimaPupil): pass
