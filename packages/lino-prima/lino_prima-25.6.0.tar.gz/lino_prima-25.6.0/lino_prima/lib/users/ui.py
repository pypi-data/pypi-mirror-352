# -*- coding: UTF-8 -*-
# Copyright 2016-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from lino.modlib.users.ui import *


class UserDetail(UserDetail):

    main = "general contact"

    general = dd.Panel("""
    box1
    school.EnrolmentsByPupil school.CastsByUser
    """, label=_("General"))
    # school.EnrolmentsByPupil

    box1 = """
    username user_type:20
    id created modified
    """

    contact = dd.Panel("""
    first_name last_name email
    language time_zone nickname initials
    users.AuthoritiesGiven users.AuthoritiesTaken
    """, label=_("Contact"))


Users.detail_layout = UserDetail()

Users.column_names = "first_name last_name email user_type *"
