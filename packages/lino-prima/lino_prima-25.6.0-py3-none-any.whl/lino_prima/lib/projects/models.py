# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.html import format_html, mark_safe
from django.utils.text import format_lazy
from django.core.exceptions import ValidationError
from lino.api import dd, rt, _
from lino.utils.html import E, tostring, join_elems
from lino.utils import SumCollector
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.printing.mixins import CachedPrintable
from lino.modlib.system.choicelists import DisplayColors
from lino.modlib.checkdata.choicelists import Checker
from lino.mixins import Referrable, Sequenced, Created
from lino_prima.lib.ratings.mixins import RatingSummary, MaxScoreField
from lino_prima.lib.ratings.utils import RatingCollector, NOT_RATED

from .choicelists import ProjectStates
from .ui import *

USE_GENERAL_RATINGS = True


class ProjectTemplate(BabelDesignated):  # zeignisse.Baustein
    class Meta:
        verbose_name = _("Project template")
        verbose_name_plural = _("Project templates")
        abstract = dd.is_abstract_model(__name__, 'ProjectTemplate')
        ordering = ["grade", "display_color"]
    short_header = dd.CharField(_("Short header"), max_length=20)
    main_skill = dd.ForeignKey('school.Skill', verbose_name=_("Main skill"))
    display_color = DisplayColors.field(blank=True, null=True)
    grade = dd.ForeignKey('school.Grade')

    def as_summary_item(self, ar, text=None):
        if text is None:
            if ar.is_obvious_field("grade"):
                text = f"{self.short_header}"
            else:
                text = f"{self.short_header} ({self.grade})"
        return super().as_summary_item(ar, text)

    def __str__(self):
        return f"{self.short_header} ({self.grade})"
        # return f"{self.enrolment} doing {self.template}"


class ProjectSection(BabelDesignated, Sequenced):  # zeugnisse.BausteinAbschnitt
    class Meta:
        verbose_name = _("Project section")
        verbose_name_plural = _("Project sections")
        abstract = dd.is_abstract_model(__name__, 'ProjectSection')

    project_template = dd.ForeignKey('projects.ProjectTemplate')

    def get_siblings(self):
        return self.__class__.objects.filter(project_template=self.project_template)

    def __str__(self):
        return f"{self.seqno}) {super().__str__()}"

    def as_paragraph(self, ar, **kwargs):
        s = ar.obj2htmls(self)
        if not ar.is_obvious_field("project_template"):
            s += format_html(_(" (in {project_template})"),
                             project_template=ar.obj2htmls(self.project_template))
        # s += "<br/>x" + tostring(self.get_workflow_buttons(ar))
        qs = rt.models.ratings.Challenge.objects.filter(project_section=self)
        s += " ({})".format(", ".join(
            [tostring(e.as_summary_item(ar)) for e in qs.order_by('seqno')]))
        return mark_safe(s)

    def get_ratings_sum(self, enr):
        rc = RatingCollector()
        for r in self.ratings_for_enrolment(enr):
            rc.collect(r.score, r.challenge.max_score,
                       text=r.challenge.skill, period=r.period)
        return rc

    def ratings_for_enrolment(self, enr):
        return rt.models.ratings.ChallengeRating.objects.filter(
              enrolment=enr, challenge__project_section=self)


# class ProjectSkill(BabelDesignated):  # zeugnisse.BausteinArbeit
#     class Meta:
#         verbose_name = _("Rating criterion")
#         verbose_name_plural = _("Rating criteria")
#         abstract = dd.is_abstract_model(__name__, 'ProjectSkill')
#
#     max_score = MaxScoreField()


class Project(RatingSummary, CachedPrintable):
    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        abstract = dd.is_abstract_model(__name__, 'Project')

    enrolment = dd.ForeignKey('school.Enrolment', verbose_name=_("Pupil"))
    template = dd.ForeignKey('projects.ProjectTemplate')
    date_started = models.DateField(_("Started on"), blank=True, null=True)
    remark = dd.TextField(_("Remark"), blank=True)

    def __str__(self):
        if self.template_id is None:
            return super().__str__()
        # return str(self.template)
        return f"{self.enrolment} doing {self.template.short_header}"

    def before_ui_save(self, ar, cw):
        if self.date_started is None:
            self.date_started = dd.today()
        super().before_ui_save(ar, cw)

    def as_summary_item(self, ar, text=None):
        if text is None:
            text = ""
            if not ar.is_obvious_field("template"):
                text += f"{self.template.short_header} "
            if not ar.is_obvious_field("enrolment"):
                text += f"{self.enrolment} "
            text += f"{self.ratings_done}% {self.total_score or NOT_RATED}"
        return super().as_summary_item(ar, text)

    # def get_ratings_todo(self):
    #     project_challenges = Challenge.objects.filter(
    #         project_section__project_template=self.template)
    #     # n = project_challenges.count() + ProjectSkill.objects.count()
    #     n = project_challenges.count() + len(GeneralRatings.get_list_items())
    #     return n

    def get_scores_to_summarize(self):
        project_challenges = rt.models.ratings.Challenge.objects.filter(
            project_section__project_template=self.template)
        for r in rt.models.ratings.ChallengeRating.objects.filter(
                challenge__in=project_challenges,
                enrolment=self.enrolment):
            yield (r.score, r.challenge.max_score)
        for gr in GeneralRatings.get_list_items():
            yield (getattr(self, gr.field_name), gr.max_score)

    def get_printable_target_stem(self):
        return f"{self._meta.verbose_name}-{self.enrolment.pupil}-{self.template.short_header}-{self.pk}"

    def get_printable_context(self, ar=None, **kwargs):
        kwargs.update(use_bulma_css=True)
        return super().get_printable_context(ar, **kwargs)

    def get_ratings_sum(self):
        rc = RatingCollector()
        qs = rt.models.ratings.ChallengeRating.objects.filter(
          enrolment=self.enrolment, challenge__project_section__project_template=self.template)
        for r in qs:
            rc.collect(r.score, r.challenge.max_score)
        return rc

    def get_general_ratings(self):
        rc = RatingCollector()
        for gr in GeneralRatings.get_list_items():
            rc.collect(getattr(self, gr.field_name),
                       gr.max_score, text=gr.text)
        return rc


# class ProjectRating(RatingBase):  # zeugnisse.BausteinBewertung
#     class Meta:
#         verbose_name = _("Project score")
#         verbose_name_plural = _("Project ratings")
#         abstract = dd.is_abstract_model(__name__, 'ProjectRating')
#
#     allow_cascaded_delete = ['project']
#
#     project = dd.ForeignKey('ratings.Project', blank=True, null=True)
#     project_skill = dd.ForeignKey('ratings.ProjectSkill', blank=True, null=True)
#
#     def __str__(self):
#         return f"{self.project_skill}: {self.score or NOT_RATED}/{self.project_skill.max_score}"
