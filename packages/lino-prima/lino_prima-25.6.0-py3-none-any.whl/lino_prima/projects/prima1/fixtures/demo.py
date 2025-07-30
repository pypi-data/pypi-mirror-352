# -*- coding: UTF-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
"""General demo data for Lino Prima.

"""

from lino.api import rt


def objects():
    """This will be called by the :ref:`dpy` deserializer during
    :cmd:`pm prep` and must yield a list of object instances to
    be saved.

    """
    return []
