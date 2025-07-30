# -*- coding: UTF-8 -*-
# Copyright 2016-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _
from lino.modlib.users.models import *
from .ui import *


class User(User):

    class Meta(User.Meta):
        abstract = dd.is_abstract_model(__name__, 'User')

# dd.update_field(User, 'username', blank=True)
