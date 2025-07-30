# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.utils.text import format_lazy
from lino.api import dd, _, pgettext


class Smilies(dd.ChoiceList):
    verbose_name = _("Smiley")
    verbose_name_plural = _("Smilies")


add = Smilies.add_item
add('4', "++", button_text="😁")  # 1F601
add('3', "+", button_text="😀")  # 1F600
add('2', "-", "default", button_text="😐")  # 1F610)
add('1', "--", button_text="😢")  # 1F622
# add('1', _("sad"), button_text="😒")  # 1F612
# add('0', _("very sad"), button_text="😢")  # 1F622


class Predicates(dd.ChoiceList):
    verbose_name = _("Predicate")
    verbose_name_plural = _("Predicates")


add = Predicates.add_item
add('1', pgettext("rating predicate", "Excellent"),
    button_text=pgettext("rating predicate", "E"))
add('2', pgettext("rating predicate", "Good"),
    button_text=pgettext("rating predicate", "G"))
add('3', pgettext("rating predicate", "Sufficient"), "default",
    button_text=pgettext("rating predicate", "S"))  # ausreichend
add('4', pgettext("rating predicate", "Deficient"),
    button_text=pgettext("rating predicate", "D"))  # mangelhaft
add('5', pgettext("rating predicate", "Insufficient"),
    button_text=pgettext("rating predicate", "I"))  # ungenügend


class RatingType(dd.Choice):
    def __init__(self, value, text, rating_choicelist):
        self.rating_choicelist = rating_choicelist
        self.field_name = value
        super().__init__(value, text, value)

    # def get_rating_choices(self):
    #     if self.rating_choicelist is not None:
    #         return self.rating_choicelist.get_list_items()
    #     return None


class RatingTypes(dd.ChoiceList):
    item_class = RatingType
    verbose_name = _("Rating type")
    verbose_name_plural = _("Rating types")


add = RatingTypes.add_item
# add("10", _("Default"), None, 'default')
add("smiley", _("Smilies"), Smilies)
add("predicate", _("Predicates"), Predicates)


class GeneralRating(dd.Choice):

    def __init__(self, value, text, max_score):
        self.field_name = 'gr_' + value
        self.max_score = max_score
        super().__init__(value, text)

    def get_field(self):
        verbose_name = format_lazy(_("{} ({} points)"), self.text, self.max_score)
        return dd.DecimalField(verbose_name, max_digits=4, decimal_places=1, blank=True, null=True)


class GeneralRatings(dd.ChoiceList):
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
        dd.inject_field('ratings.Project', pf.field_name, pf.get_field())
