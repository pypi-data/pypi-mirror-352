# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils.html import format_html, mark_safe
from django.utils.text import format_lazy
from django.core.exceptions import ValidationError
from lino.utils.html import E, tostring, join_elems
from lino.utils import SumCollector
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.printing.mixins import CachedPrintable
from lino.modlib.system.choicelists import DisplayColors
from lino.modlib.summaries.mixins import SlaveSummarized
from lino.modlib.checkdata.choicelists import Checker
from lino.mixins import Referrable, Sequenced, Created
from lino.api import dd, rt, _

from .ui import *
from .mixins import RatingBase, RatingSummary, ScoreField, MaxScoreField
from .utils import format_percentage, format_score, ScoreValue, RatingCollector
# from .mixins import RatingSummaryBase
from .choicelists import Predicates, Smilies


# class Exam(UserAuthored, BabelDesignated, Sequenced):   # zeugnisse.Test
class Exam(UserAuthored, Sequenced):   # zeugnisse.Test
    class Meta:
        verbose_name = _("Exam")
        verbose_name_plural = _("Exams")
        abstract = dd.is_abstract_model(__name__, 'Exam')
        ordering = ['group', 'subject', 'seqno']
    group = dd.ForeignKey('school.Group', related_name='enrolments')
    subject = dd.ForeignKey('school.Subject')
    heading = dd.CharField(_("Title"), max_length=250)
    # cast = dd.ForeignKey('school.Cast')
    date = models.DateField(_("Date"), blank=True, null=True)
    period = dd.ForeignKey('periods.StoredPeriod')

    def get_siblings(self):
        return self.__class__.objects.filter(group=self.group, subject=self.subject)

    def date_changed(self, ar):
        self.period = None
        # full_clean() will then set the default period according to date.

    # def on_create(self, ar):
    #     self.date = dd.today()
    #     return super().on_create(ar)

    def after_ui_create(self, ar):
        super().after_ui_create(ar)
        self.fix_problems.run_from_ui(ar)

    def __str__(self):
        return self.heading

    def full_clean(self):
        if not self.date:
            date = dd.today()
            if not self.group.year.covers_date(date):
                # date = date.replace(year=self.group.year.start_date.year)
                date = self.group.year.end_date
            self.date = date
        if not self.group.year.covers_date(self.date):
            raise ValidationError(_("Date {} is not in {}").format(
                self.date, self.group.year))
        if not self.period_id:
            P = rt.models.periods.StoredPeriod
            # date = self.date or dd.today()
            self.period = P.get_or_create_from_date(self.date)
            # qs = P.objects.filter(
            #     year=self.group.year,
            #     start_date__lte=date,
            #     end_date__gte=date)
            # # print("20241030", qs)
            # period = qs.first()
            # if period is None:
            #     period = P.get_or_create_from_date(date)
            # self.period = period
        super().full_clean()

    @dd.displayfield(_("Completion"))
    def completion(self, ar=None):
        if not self.pk:
            return ""
        qs = rt.models.ratings.ChallengeRating.objects.filter(
            challenge__exam=self, enrolment__group=self.group)
        todo = qs.count()
        if todo == 0:
            return NOT_RATED
        done = qs.filter(score__isnull=False).count()
        # return format_score(100 * done / todo) + "%"
        return format_percentage(done, todo)


dd.update_field(Exam, 'user', verbose_name=_("Teacher"))


class Challenge(Sequenced):  # zeugnisse.Leistung
    # Other names: Expectation, ExamQuestion, Achievement, Feat
    class Meta:
        verbose_name = _("Challenge")
        verbose_name_plural = _("Challenges")
        abstract = dd.is_abstract_model(__name__, 'Challenge')
        unique_together = ('exam', 'project_section', 'skill')

    allow_cascaded_delete = ["exam", "project_section"]

    skill = dd.ForeignKey('school.Skill', blank=True, null=True)
    exam = dd.ForeignKey('ratings.Exam', blank=True, null=True)
    project_section = dd.ForeignKey('projects.ProjectSection', blank=True, null=True)
    max_score = MaxScoreField()

    def get_siblings(self):
        if self.exam_id:
            return self.__class__.objects.filter(exam=self.exam)
        return self.__class__.objects.filter(project_section=self.project_section)

    @dd.displayfield(_("Section"))
    def exam_or_section(self, ar=None):
        if self.exam_id:
            return self.exam.as_summary_item(ar)
        return self.project_section.as_summary_item(ar)
        # return f"{self.project_section.project_template.short_header}:{self.project_section}"

    @dd.chooser()
    def skill_choices(cls, exam, project_section):
        # print(f"20241212 {exam}")
        if exam is not None:
            qs = rt.models.school.Skill.objects.filter(subject=exam.subject)
        elif project_section is not None:
            qs = rt.models.school.Skill.objects.all()
        else:
            qs = rt.models.school.Skill.objects.all()
        return qs

    def __str__(self):
        # return f"{self.project_section or self.exam} ({self.id})"
        # return str(self.project_section or self.exam)
        # return f"{self.max_score} for {self.skill} in {self.project_section or self.exam}"
        # return f"{self.skill} in {self.project_section or self.exam}"
        return _("{skill} /{max_score} in {exam_or_section}").format(
            max_score=format_score(self.max_score), skill=self.skill,
            exam_or_section=self.exam_or_section)

    # def as_summary_item(self, ar, text=None):
    #     if text is None:
    #         text = ""
    #         if ar.is_obvious_field("skill"):
    #             text = f"{self} in {self.exam_or_section}"
    #         elif ar.is_obvious_field("exam") or ar.is_obvious_field("project_section"):
    #             text = f"{self} for {self.skill} in {self.exam_or_section}"
    #         else:
    #             text = str(self.skill)
    #     return super().as_summary_item(ar, text)

    # def as_summary_item(self, ar, text=None):
    #     if ar.is_obvious_field("skill"):
    #         if self.project_section_id is not None:
    #             obj = self.project_section.project_template
    #         if self.exam_id is not None:
    #             obj = self.exam
    #         else:
    #             obj = super()
    #     else:
    #         obj = self.skill or super()
    #     txt = obj.as_summary_item(ar, text)
    #     return format_html("{1} ({0})", self.max_score, tostring(txt))


class ChallengeRating(RatingBase):  # zeugnisse.LeistungsBewertung
    class Meta:
        verbose_name = _("Challenge rating")
        verbose_name_plural = _("Challenge ratings")
        abstract = dd.is_abstract_model(__name__, 'ChallengeRating')
    enrolment = dd.ForeignKey(
        'school.Enrolment', verbose_name=_("Pupil"), editable=False)
    challenge = dd.ForeignKey('ratings.Challenge', editable=False)
    allow_cascaded_delete = ['challenge']

    def get_skill(self):
        if self.challenge_id:  # avoid RelatedObjectDoesNotExist
            return self.challenge.skill

    def get_max_score(self):
        if self.challenge_id:  # avoid RelatedObjectDoesNotExist
            return self.challenge.max_score

    def get_rating_type(self):
        if self.challenge_id:  # avoid RelatedObjectDoesNotExist
            return self.challenge.skill.subject.rating_type

    def as_paragraph(self, ar, **kwargs):
        # s = ar.obj2htmls(self)

        # elems = list(self.get_rating_buttons(ar))
        # s = tostring(E.span(*join_elems(elems, sep=" | ")))
        # s = tostring(E.span(*join_elems(self.get_rating_buttons(ar), sep=" | ")))
        s = " | ".join(map(tostring, self.get_rating_buttons(ar)))

        if not ar.is_obvious_field("challenge"):
            s += " " + format_html(_("in {subject}:{skill}"),
                                   subject=self.challenge.skill.subject,
                                   skill=self.challenge.skill)
        if not ar.is_obvious_field("enrolment"):
            s += " " + format_html(_("for {pupil}"), pupil=ar.obj2htmls(self.enrolment))
        return mark_safe(s)


class ResponseScoreField(dd.VirtualField):
    editable = True

    def __init__(self, seqno):
        self._seqno = seqno
        t = ScoreField(str(seqno))
        dd.VirtualField.__init__(self, t, None)

    def value_from_object(self, obj, ar):
        try:
            rating = ChallengeRating.objects.get(
                challenge__exam=obj.exam,
                challenge__seqno=self._seqno,
                enrolment=obj.enrolment)
        except ChallengeRating.DoesNotExist:
            return None
        except ChallengeRating.MultipleObjectsReturned:
            qs = ChallengeRating.objects.filter(
                challenge__seqno=self._seqno,
                challenge__exam=obj.exam,
                enrolment=obj.enrolment)
            # print(f"20241212 {qs}")
            return None
        return rating.score

    def set_value_in_object(self, ar, obj, value):
        if ar is None:  # e.g. when called by loaddata
            return
        Enrolment = rt.models.school.Enrolment
        ExamResponse = rt.models.ratings.ExamResponse
        Challenge = rt.models.ratings.Challenge
        ChallengeRating = rt.models.ratings.ChallengeRating
        assert isinstance(obj, ExamResponse)
        # print(f"20241017 cellattrs {ar.renderer.cellattrs}")
        try:
            challenge = Challenge.objects.get(exam=obj.exam, seqno=self._seqno)
        except Challenge.DoesNotExist:
            ar.warning(_("20241212 Oops"))
            return
        except Challenge.MultipleObjectsReturned:
            ar.warning(_("{} has multiple challenges with seqno {}").format(
                obj, self._seqno))
            return
        rating, created = ChallengeRating.objects.get_or_create(
            enrolment=obj.enrolment, challenge=challenge)
        rating.score = value
        rating.full_clean()
        rating.save()


class ExamResponse(dd.Model):
    class Meta:
        verbose_name = _("Exam response")
        verbose_name_plural = _("Exam responses")
        abstract = dd.is_abstract_model(__name__, 'ExamResponse')
        unique_together = ['enrolment', 'exam']

    enrolment = dd.ForeignKey(
        'school.Enrolment', verbose_name=_("Pupil"), editable=False)
    exam = dd.ForeignKey('ratings.Exam', editable=False)
    remark = dd.RichTextField(_("Remark"), blank=True, format="plain")

    allow_cascaded_delete = ["exam"]

    # score1 = ResponseScoreField(1)
    # score2 = ResponseScoreField(2)

    def disabled_fields(self, ar):
        df = super().disabled_fields(ar)
        df |= set(SCORE_FIELDS)
        for o in Challenge.objects.filter(exam=self.exam):
            df.discard("score" + str(o.seqno))
        return df

    @classmethod
    def get_simple_parameters(cls):
        for p in super().get_simple_parameters():
            yield p
        yield 'enrolment'
        yield 'exam'

    @dd.displayfield(_("Ratings"))
    def ratings(self, ar):
        if ar is None:
            return ''
        elems = []

        # Enrolment = rt.models.school.Enrolment
        # ExamResponse = rt.models.ratings.ExamResponse
        Challenge = rt.models.ratings.Challenge
        ChallengeRating = rt.models.ratings.ChallengeRating
        # exam = ar.master_instance
        exam = self.exam
        # print(f"20250531 {repr(exam)}")
        challenges = Challenge.objects.filter(exam=exam)
        if not challenges.exists():
            return _("No {challenges} in {exam}.").format(
                challenges=Challenge._meta.verbose_name_plural, exam=exam)
        sar = ChallengeRatingsByEnrolment.create_request(
            parent=ar, master_instance=self.enrolment)
        # insert_button_attrs = dict(style="text-align: center;")

        def rating_elem(challenge):
            try:
                rating = ChallengeRating.objects.get(
                    enrolment=self.enrolment, challenge=challenge)
            except ChallengeRating.DoesNotExist:
                return f"{NOT_RATED} / {challenge.max_score}"
                # btn = sar.gen_insert_button(None, insert_button_attrs,
                #         challenge=str(challenge), challengeHidden=challenge.pk)
                # if btn is None:
                #     return ""
                # return btn
                # return E.p(txt, btn, align="center")
                # return str("+")
            # txt = f"{rating.score or NOT_RATED}"
            # return sar.obj2html(rating, txt)
            return sar.obj2html(rating)

        for chl in challenges:
            elems.append(rating_elem(chl))
        return E.p(*join_elems(elems, sep=", "))


max_skills_per_exam = dd.get_plugin_setting("ratings", "max_skills_per_exam", 0)

SCORE_FIELDS = []
for i in range(1, max_skills_per_exam+1):
    name = "score" + str(i)
    SCORE_FIELDS.append(name)
    dd.inject_field(ExamResponse, name, ResponseScoreField(i))


class FinalExam(dd.Model):  # zeugnisse.AbschlussTest
    class Meta:
        verbose_name = _("Final exam")
        verbose_name_plural = _("Final exams")
        abstract = dd.is_abstract_model(__name__, 'FinalExam')
        ordering = ['designation']

    designation = dd.CharField(_("Final exam"), max_length=200)
    skill = dd.ForeignKey('school.Skill', blank=True, null=True)
    max_score = MaxScoreField()

    @classmethod
    def get_simple_parameters(cls):
        for p in super().get_simple_parameters():
            yield p
        yield 'skill'


class FinalExamRating(RatingBase):  # zeugnisse.AbschlussTestBewertung
    class Meta:
        verbose_name = _("Final exam rating")
        verbose_name_plural = _("Final exam ratings")
        abstract = dd.is_abstract_model(__name__, 'FinalExamRating')

    allow_cascaded_delete = ['enrolment', 'exam']

    enrolment = dd.ForeignKey(
        'school.Enrolment', verbose_name=_("Pupil"), editable=False)
    exam = dd.ForeignKey('ratings.FinalExam', editable=False)

    def get_skill(self):
        return self.exam.skill

    def get_max_score(self):
        return self.exam.max_score

    def get_rating_type(self):
        return self.exam.skill.subject.rating_type

    @classmethod
    def get_simple_parameters(cls):
        for p in super().get_simple_parameters():
            yield p
        yield 'enrolment'
        yield 'exam'


class RatingsSummary(SlaveSummarized):
    class Meta:
        verbose_name = _("Rating summary")
        verbose_name_plural = _("Rating summaries")
        abstract = dd.is_abstract_model(__name__, 'ChallengeSummary')
        ordering = ('master', 'skill__subject', 'skill', 'enrolment')
    master = dd.ForeignKey('school.Group')
    skill = dd.ForeignKey('school.Skill')
    challenge = dd.ForeignKey('ratings.Challenge', blank=True, null=True)
    enrolment = dd.ForeignKey(
        'school.Enrolment', verbose_name=_("Pupil"), blank=True, null=True)
    score = dd.DecimalField(_("Score"), max_digits=5,
                            decimal_places=1, blank=True, null=True)
    max_score = dd.DecimalField(_("Max score"), max_digits=5,
                                decimal_places=1, blank=True, null=True)
    delete_them_all = True

    def __str__(self):
        if self.challenge_id is None:
            if self.enrolment_id is None:
                return _("{subject}:{skill} in {group}").format(
                    group=self.master, subject=self.skill.subject, skill=self.skill)
            else:
                return f"{self.enrolment.pupil} {self.score}"
        elif self.enrolment_id is None:
            return f"{self.challenge}"
        return super().__str__()
        # return f"{self.master} {self.skill} {self.challenge} {self.enrolment} -> {self.score}"

    @classmethod
    def update_for_filter(cls, master=None):
        by_enrolment = SumCollector()
        by_challenge = SumCollector()
        by_skill = SumCollector()

        def loop():
            for r in ChallengeRating.objects.filter(
                enrolment__group=master, score__isnull=False
            ):
                yield (r.enrolment, r.challenge, r.score, r.challenge.max_score)
        for enr, challenge, score, max_score in loop():
            v = ScoreValue(score, max_score)
            skill = challenge.skill
            by_enrolment.collect((skill, enr), v)
            by_challenge.collect((skill, challenge), v)
            by_skill.collect(skill, v)

        def create_or_update(v, **kwargs):
            self, created = cls.objects.get_or_create(master=master, **kwargs)
            self.score = round(v._score, 1)
            self.max_score = round(v._max_score, 1)
            self.full_clean()
            self.save()

        for skill, v in by_skill.items():
            create_or_update(v.rebase(100), skill=skill)
        for skill_enr, v in by_enrolment.items():
            skill, enr = skill_enr
            create_or_update(v.rebase(100), enrolment=enr, skill=skill)
        for skill_chl, v in by_challenge.items():
            skill, chl = skill_chl
            create_or_update(v.rebase(100), challenge=chl, skill=skill)

    def get_summary_collectors(self):
        qs = rt.models.ratings.Challenge.objects.filter(ticket=self)
        yield (self.add_from_session, qs)

    def get_scores_to_summarize(self):
        if self.enrolment_id is not None:
            flt.update(enrolment=self.enrolment)
        elif self.challenge_id is not None:
            flt.update(challenge=self.enrolment)
        project_challenges = Challenge.objects.filter(
            project_section__project_template=self.template)
        for r in ChallengeRating.objects.filter(
                challenge__in=project_challenges,
                enrolment=self.enrolment):
            yield (r.score, r.challenge.max_score)
        for prj in rt.models.projects.Project.objects.filter(
                challenge__in=project_challenges,
                enrolment=self.enrolment):
            for gr in GeneralRatings.get_list_items():
                yield (getattr(self, gr.field_name), gr.max_score)


class ChallengeChecker(Checker):
    verbose_name = _("Check for missing or duplicate challenge ratings")
    model = Challenge
    msg_missing = _("No challenge rating for {} pupils.")
    msg_duplicate = _("Duplicate challenge rating(s) for {} pupils.")

    def get_checkdata_problems(self, ar, obj, fix=False):
        Enrolment = rt.models.school.Enrolment
        PeriodStates = rt.models.periods.PeriodStates
        missing = []
        duplicate = 0
        if obj.exam_id is not None:
            if obj.exam.period.state != PeriodStates.open:
                return
            enrolments = Enrolment.objects.filter(group=obj.exam.group)
        elif obj.project_section_id is not None:
            prjtpl = obj.project_section.project_template
            enrolments = Enrolment.objects.filter(
                group__grade=prjtpl.grade, group__year__state=PeriodStates.open)
        else:
            yield (False, "Invalid challenge")
        for enr in enrolments:
            qs = ChallengeRating.objects.filter(challenge=obj, enrolment=enr)
            if qs.count() == 0:
                missing.append(ChallengeRating(challenge=obj, enrolment=enr))
            elif qs.count() > 1:
                duplicate += 1
        if duplicate > 0:
            yield (False, format_lazy(self.msg_duplicate, duplicate))
        if len(missing) > 0:
            yield (True, format_lazy(self.msg_missing, len(missing)))
            if fix:
                for row in missing:
                    row.full_clean()
                    row.save()


ChallengeChecker.activate()


class ExamChecker(Checker):
    verbose_name = _("Check for missing or duplicate exam responses")
    model = Exam
    msg_missing = _("No response for {} enrolments.")
    msg_duplicate = _("Duplicate response(s) for {} enrolments.")

    def get_checkdata_problems(self, ar, obj, fix=False):
        if obj.period.state != rt.models.periods.PeriodStates.open:
            return
        Enrolment = rt.models.school.Enrolment
        ExamResponse = rt.models.ratings.ExamResponse
        missing = []
        duplicate = 0
        enrolments = Enrolment.objects.filter(group=obj.group)
        for enr in enrolments:
            qs = ExamResponse.objects.filter(exam=obj, enrolment=enr)
            if qs.count() == 0:
                missing.append(ExamResponse(exam=obj, enrolment=enr))
            elif qs.count() > 1:
                duplicate += 1
        if duplicate > 0:
            yield (False, format_lazy(self.msg_duplicate, duplicate))
        if len(missing) > 0:
            yield (True, format_lazy(self.msg_missing, len(missing)))
            if fix:
                for row in missing:
                    row.full_clean()
                    row.save()


ExamChecker.activate()
