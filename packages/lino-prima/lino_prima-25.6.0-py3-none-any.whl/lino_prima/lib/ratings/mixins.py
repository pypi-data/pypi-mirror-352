# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import locale
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import models
from lino.api import dd, rt, _
from lino.mixins import Created
from lino.utils.html import E, join_elems
from lino.modlib.summaries.mixins import Summarized
from .choicelists import Smilies, Predicates, RatingTypes
from .utils import ZERO, NOT_RATED, ScoreValue

# def RatingField(verbose_name=None, **kwargs):
#     if verbose_name is None:
#         verbose_name = _("Rating")
#     kwargs.update(max_length=2, blank=True, verbose_name=verbose_name)
#     return models.CharField(**kwargs)


def ScoreField(verbose_name=None, **kwargs):
    if verbose_name is None:
        verbose_name = _("Score")
    return dd.DecimalField(
        verbose_name, max_digits=4, decimal_places=1,
        blank=True, null=True, **kwargs)


def MaxScoreField(verbose_name=None, **kwargs):
    if verbose_name is None:
        verbose_name = _("Max. score")
    return dd.DecimalField(
        verbose_name, max_digits=4, decimal_places=1, default=10, **kwargs)


class SetScoreValue(dd.Action):
    """Set the score value of this response."""

    label = _("Set score value")
    icon_name = None
    show_in_toolbar = False
    parameters = dict(score=ScoreField(),
                      smiley=Smilies.field(blank=True, null=True),
                      predicate=Predicates.field(blank=True, null=True))

    params_layout = "score"
    # params_layout = """
    # score
    # smiley
    # predicate
    # """

    def get_action_permission(self, ar, obj, state):
        return not ar.get_user().is_anonymous

    # @dd.chooser(instance_values=True)
    # def rating_choices(cls, rating_type):
    #     # print(f"20241203 {repr(rating_type)}")
    #     if not rating_type:
    #         return []
    #     return rating_type.rating_choicelist.get_list_items()

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        pv = ar.action_param_values
        for k, v in pv.items():
            setattr(obj, k, v)
        # obj.score = pv.score
        # obj.smiley = pv.smiley
        # obj.predicate = pv.predicate
        obj.before_ui_save(ar, None)
        obj.full_clean()
        obj.save()
        ar.success(refresh=True)


class SetScoreValueDirectly(SetScoreValue):
    no_params_window = True
    params_layout = """
    smiley
    predicate
    """


class Ratable(dd.Model):

    class Meta:
        abstract = True

    score = ScoreField()
    smiley = Smilies.field(blank=True, null=True)
    predicate = Predicates.field(blank=True, null=True)

    set_score_action = SetScoreValue()
    set_score_action_directly = SetScoreValueDirectly()

    def get_skill(self):
        raise NotImplementedError

    def get_max_score(self):
        raise NotImplementedError

    def get_rating_type(self):
        raise NotImplementedError

    def disabled_fields(self, ar):
        rv = super().disabled_fields(ar)
        if self.get_rating_type() is not None:
            rv.add("score")
        return rv

    def full_clean(self):
        super().full_clean()
        rating_type = self.get_rating_type()
        if rating_type is not None and self.score is not None:
            # needed only after csv2db
            setattr(self, rating_type.field_name, str(self.score))
            # if rating_type == RatingTypes.smiley:
            #     self.smiley = str(self.score)
            # elif rating_type == RatingTypes.predicate:
            #     self.predicate = str(self.score)
            # rating = rating_type.rating_choicelist.get_by_value(str(self.score))
            # if rating is None:
            #     raise ValidationError("20241203")
            # self.rating = rating.value
            self.score = None

    # @dd.chooser(instance_values=True)
    # def rating_choices(cls, rating_type):
    #     # print(f"20241203 {repr(rating_type)}")
    #     if not rating_type:
    #         return []
    #     return rating_type.rating_choicelist.get_list_items()

    @dd.virtualfield(RatingTypes.field(blank=True, null=True))
    def rating_type(self, ar):
        return self.get_rating_type()

    @property
    def score_value(self):
        return ScoreValue(self.score, self.get_max_score())

    def __str__(self):
        return str(self.score_value)
        # return f"{self.score or NOT_RATED}/{max_score}"

    def get_rating_buttons(self, ar, detail_link=True):
        if ar is None:
            return

        ssa = ar.actor.get_action_by_name('set_score_action')
        ssad = ar.actor.get_action_by_name('set_score_action_directly')

        rating_type = self.get_rating_type()
        if rating_type is None:
            # max_score = format_rating(self.get_max_score())
            # txt = f"{self.score or NOT_RATED}/{max_score}"
            txt = self.score_value.absolute
            kw = dict(action_param_values=dict(score=self.score))
            yield ar.row_action_button(
                self, ssa, label=txt, request_kwargs=kw)
        else:
            found_existing = False
            value = getattr(self, rating_type.field_name)
            for ch in rating_type.rating_choicelist.get_list_items():
                kw = dict(action_param_values={rating_type.field_name: ch.value})
                label = ch.button_text or ch.text
                if value == ch.value:
                    yield E.span(str(label),
                                 style="font-size:1.5em")
                    # style="border:5px solid gray; background-color: gray")
                    found_existing = True
                else:
                    yield ar.row_action_button(
                        self, ssad,
                        label=label, request_kwargs=kw, style="font-size:0.7em")
            if value is not None and not found_existing:
                # value is set but was not found in choicelist
                yield str(value) + "!"
        if detail_link:
            # yield ar.obj2html(self, "🖉")  # #1f589
            yield ar.obj2html(self, "🛈")  # #1f6c8

    @dd.displayfield(_("Max. score"), max_length=3)
    def max_score(self, ar=None):
        if self.get_rating_type() is None:
            return str(self.get_max_score())
        return _("N/A")

    @dd.displayfield(_("Rate it"))
    def rating_buttons(self, ar):
        if ar is None:
            return ""
        return E.span(*join_elems(self.get_rating_buttons(
            ar, detail_link=False), sep=", "))


class RatingBase(Ratable):
    class Meta:
        abstract = True
    teacher = dd.ForeignKey('users.User', verbose_name=_(
        "Teacher"), blank=True, null=True, editable=False)
    period = dd.ForeignKey('periods.StoredPeriod', blank=True, null=True)
    # done = models.DateTimeField(_("Done"), editable=False, null=True)
    date_done = models.DateField(_("Done since"), blank=True, null=True)

    def mark_done(self):
        # self.done = timezone.now()
        self.date_done = dd.today()

    def before_ui_save(self, ar, cw):
        if not self.period_id:
            self.period = rt.models.periods.StoredPeriod.get_or_create_from_date(
                dd.today())
        if not self.teacher:
            self.teacher = ar.get_user()
        if not self.date_done:
            self.mark_done()
        super().before_ui_save(ar, cw)

    @classmethod
    def get_simple_parameters(cls):
        for p in super().get_simple_parameters():
            yield p
        yield 'teacher'
        yield 'period'


# class RatingSummaryBase(dd.Model):
#     class Meta:
#         abstract = True

class RatingSummary(Summarized):

    class Meta:
        abstract = True

    ratings_done = dd.PercentageField(
        _("Ratings done"), decimal_places=0, blank=True, null=True, editable=False)
    total_score = dd.DecimalField(
        _("Total score"), max_digits=5, decimal_places=1, blank=True, null=True, editable=False)
    total_max_score = dd.DecimalField(
        _("Total max score"), max_digits=5, decimal_places=1, blank=True, null=True, editable=False)

    def get_scores_to_summarize(self):
        return []

    def compute_summary_values(self):
        ratings_todo = 0  # self.get_ratings_todo()
        ratings_done = 0
        total_max_score = 0
        total_score = 0
        for score, max_score in self.get_scores_to_summarize():
            ratings_todo += 1
            if score is not None:
                ratings_done += 1
                total_score += score
                total_max_score += max_score

        self.total_score = round(total_score, 1)
        self.total_max_score = round(total_max_score, 1)
        if ratings_todo == 0:
            self.ratings_done = None
        else:
            self.ratings_done = round(ratings_done * 100 / ratings_todo, 0)

        self.full_clean()
        self.save()

    @property
    def total(self):
        return ScoreValue(self.total_score, self.total_max_score)

    def computed_text(self):
        max_score = self.get_max_score()
        if self.total_max_score:
            text = f"{self.total_score or NOT_RATED}/{self.total_max_score}"
            rel_score = round(self.total_score * max_score / self.total_max_score, 1)
            text += f" → {rel_score}/{max_score}"
        else:
            text = _("N/A")
        return text


class ExamTypes(dd.ChoiceList):
    verbose_name = _("Examination type")
    verbose_name_plural = _("Examination types")


add = ExamTypes.add_item
add("10", _("ProjectTemplates"), "project")   # Bausteine
add("20", _("Tests"), "test")         # Tests
add("30", _("Final tests"), "final")  # Abschlusstests
