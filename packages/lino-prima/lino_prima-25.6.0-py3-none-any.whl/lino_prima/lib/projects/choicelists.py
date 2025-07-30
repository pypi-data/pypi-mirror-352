# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.utils.text import format_lazy
from lino.api import dd, _
from lino.core.roles import Explorer


class ProjectStates(dd.ChoiceList):
    verbose_name = _("Project state")
    verbose_name_plural = _("Project states")

add = ProjectStates.add_item
add("1", _("Not started"), "default", button_text="☐")   # u2610 Noch nichts eingetragen
add("2", _("Started"), button_text="✎")  # u270e Teilweise eingetragen
add("3", _("Done"), button_text="☑")     # u2611 Kommentar + alle Bausteinarbeiten eingetragen.


class GeneralRating(dd.Choice):

    def __init__(self, value, text, max_score):
        self.field_name = 'gr_' + value
        self.max_score = max_score
        super().__init__(value, text)

    def get_field(self):
        verbose_name = format_lazy(_("{} ({} points)"), self.text, self.max_score)
        return dd.DecimalField(verbose_name, max_digits=4, decimal_places=1, blank=True, null=True)


class GeneralRatings(dd.ChoiceList):
    required_roles = dd.login_required(Explorer)
    item_class = GeneralRating
    verbose_name = _("General rating")
    verbose_name_plural = _("General ratings")


add = GeneralRatings.add_item
add("1", _("Cleanliness"), 3)  # Sauberkeit
add("2", _("Correction"), 3)  # Korrektur
add("3", _("Time managment"), 3)  # Zeitmanagement
add("4", _("Work behaviour"), 3)  # Arbeitsverhalten


@dd.receiver(dd.pre_analyze)
def inject_general_rating_fields(sender, **kw):
    for pf in GeneralRatings.get_list_items():
        dd.inject_field('projects.Project', pf.field_name, pf.get_field())
