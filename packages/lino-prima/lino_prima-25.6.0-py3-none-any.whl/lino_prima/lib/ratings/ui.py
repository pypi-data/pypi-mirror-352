# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.html import format_html, mark_safe
from etgen import html as xghtml
from lino.utils.html import E, join_elems, tostring, SAFE_EMPTY
from lino.core import constants
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.system.choicelists import DisplayColors
from lino.mixins import Referrable, Sequenced, Created
from lino.api import dd, rt, _, gettext

from lino_prima.lib.school.roles import PrimaStaff, PrimaTeacher, PrimaPupil
from lino.core.roles import Explorer

from .choicelists import GeneralRatings
from .utils import NOT_RATED, format_score


class RatingsSummaries(dd.Table):
    required_roles = dd.login_required(Explorer)
    model = "ratings.RatingsSummary"
    extra_display_modes = {constants.DISPLAY_MODE_LIST}
    detail_layout = """
    id master skill enrolment challenge
    ratings.ChallengesByGroupSkill:70 ratings.EnrolmentsByGroupSkill:70
    """


class SummariesByCourse(RatingsSummaries):
    required_roles = dd.login_required(PrimaTeacher)
    master = "school.Course"
    column_names = "skill score max_score *"

    @classmethod
    def get_request_queryset(self, ar, **filter):
        mi = ar.master_instance
        assert isinstance(mi, rt.models.school.Course)
        qs = super().get_request_queryset(ar, **filter)
        qs = qs.filter(
            master=mi.group, skill__subject=mi.subject,
            enrolment__isnull=True, challenge__isnull=True)
        return qs


class SkillsByGroup(RatingsSummaries):
    required_roles = dd.login_required(PrimaTeacher)
    # master = "school.Group"
    master_key = "master"
    filter = Q(challenge__isnull=True, enrolment__isnull=True)
    label = _("Skills overview")
    column_names = "skill__subject skill score *"
    group_by = [lambda obj: obj.skill.subject]
    default_display_modes = {
        70: constants.DISPLAY_MODE_HTML,
        None: constants.DISPLAY_MODE_LIST}
    # default_display_modes = {None: constants.DISPLAY_MODE_HTML}

    @classmethod
    def before_group_change(cls, gh, obj):
        return format_html("<h2>{}</h2>", obj.skill.subject)


class ChallengesByGroupSkill(RatingsSummaries):
    required_roles = dd.login_required(PrimaTeacher)
    master = "ratings.RatingsSummary"
    # master_key = "master"
    filter = Q(challenge__isnull=False, enrolment__isnull=True)
    label = _("Challenge ratings")
    # default_display_modes = {None: constants.DISPLAY_MODE_HTML}
    default_display_modes = {None: constants.DISPLAY_MODE_GRID}
    column_names = "challenge__exam_or_section score *"

    @classmethod
    def setup_request(self, ar):
        super().setup_request(ar)
        mi = ar.master_instance
        ar.known_values.update(master=mi.master, skill=mi.skill)

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     mi = ar.master_instance
    #     assert isinstance(mi, rt.models.ratings.RatingsSummary)
    #     qs = super().get_request_queryset(ar, **filter)
    #     qs = qs.filter(master=mi.master, skill=mi.skill)
    #     return qs


class EnrolmentsByGroupSkill(RatingsSummaries):
    required_roles = dd.login_required(PrimaTeacher)
    master = "ratings.RatingsSummary"
    # master = "school.Group"
    # master_key = "master"
    filter = Q(challenge__isnull=True, enrolment__isnull=False)
    label = _("Pupil ratings")
    default_display_modes = {None: constants.DISPLAY_MODE_GRID}
    column_names = "enrolment score *"

    @classmethod
    def setup_request(self, ar):
        super().setup_request(ar)
        mi = ar.master_instance
        ar.known_values.update(master=mi.master, skill=mi.skill)

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     mi = ar.master_instance
    #     assert isinstance(mi, rt.models.ratings.RatingsSummary)
    #     qs = super().get_request_queryset(ar, **filter)
    #     qs = qs.filter(master=mi.master, skill=mi.skill)
    #     return qs


class ExamDetail(dd.DetailLayout):
    main = "general #responses more"
    general = dd.Panel("""
    subject group date
    seqno heading
    ratings.ResponsesByExam
    """, _("General"))

    # responses = dd.Panel("""
    # ratings.PupilsAndRatingsByExam
    # """, _("Responses"))

    more = dd.Panel("""
    period id user
    ratings.ChallengesByExam #ratings.RatingsByExam
    """, _("More"))


class Exams(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'ratings.Exam'
    detail_layout = "ratings.ExamDetail"


class ExamsByGroup(Exams):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "group"
    column_names = "subject seqno date heading completion user period *"
    insert_layout = """
    subject
    heading
    """


class ExamsByCourse(Exams):
    required_roles = dd.login_required(PrimaTeacher)
    master = "school.Course"
    column_names = "heading date seqno completion user period *"
    start_at_bottom = True
    # default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}
    extra_display_modes = {constants.DISPLAY_MODE_LIST,
                           constants.DISPLAY_MODE_SUMMARY}
    # card_layout = """
    # seqno date id
    # """
    insert_layout = """
    heading
    date
    """

    @classmethod
    def setup_request(self, ar):
        super().setup_request(ar)
        mi = ar.master_instance
        ar.known_values.update(subject=mi.subject, group=mi.group)

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     mi = ar.master_instance
    #     assert isinstance(mi, rt.models.school.Course)
    #     qs = super().get_request_queryset(ar, **filter)
    #     return qs.filter(subject=mi.subject, group=mi.group)


# class ExamsByCast(Exams):
#     required_roles = dd.login_required(PrimaTeacher)
#     master = "school.Cast"
#     column_names = "seqno heading period *"
#
#     @classmethod
#     def setup_request(self, ar):
#         super().setup_request(ar)
#         mi = ar.master_instance
#         ar.known_values.update(subject=mi.subject, group=mi.group, user=mi.user)

    # @classmethod
    # def get_request_queryset(self, ar, **filter):
    #     mi = ar.master_instance
    #     assert isinstance(mi, rt.models.school.Cast)
    #     qs = super().get_request_queryset(ar, **filter)
    #     if True:
    #         qs = qs.filter(subject=mi.subject, group=mi.group, user=mi.user)
    #     else:
    #         # When there are two teachers for a same subject, they manage tests
    #         # together.
    #         qs = qs.filter(subject=mi.subject, group=mi.group)
    #     return qs

    # @classmethod
    # def get_master_instance(cls, ar, model, pk):
    #     # the master instance of ExamsByGroup must be a group, but since
    #     # we use this on an cast, we get the pk of a cast
    #     assert model is rt.models.school.Cast
    #     cast = rt.models.school.Cast.objects.get(pk=pk)
    #     return cast.group

class PupilsAndRatingsByExam(dd.VirtualTable):
    required_roles = dd.login_required(PrimaTeacher)
    master = "ratings.Exam"
    label = _("Pupils and ratings")
    default_display_modes = {None: constants.DISPLAY_MODE_HTML}

    @classmethod
    def table_as_html(cls, ar):
        Enrolment = rt.models.school.Enrolment
        ExamResponse = rt.models.ratings.ExamResponse
        Challenge = rt.models.ratings.Challenge
        ChallengeRating = rt.models.ratings.ChallengeRating
        exam = ar.master_instance
        # print(f"20241017 cellattrs {ar.renderer.cellattrs}")
        challenges = Challenge.objects.filter(exam=exam)
        if not challenges.exists():
            return _("There are no {challenges} configured for {exam}.").format(
                challenges=Challenge._meta.verbose_name_plural, exam=exam)

        insert_button_attrs = dict(style="text-align: center;")

        def challenge_cell(sar, challenge):
            try:
                rating = ChallengeRating.objects.get(
                    enrolment=sar.master_instance.enrolment, challenge=challenge)
            except ChallengeRating.DoesNotExist:
                btn = sar.gen_insert_button(None, insert_button_attrs,
                                            challenge=str(challenge), challengeHidden=challenge.pk)
                if btn is None:
                    return ""
                return btn

            # elems = list(rating.get_rating_buttons(sar))
            # elems.append(sar.obj2html(rating, "🖉"))  # #1f589
            # return E.span(*join_elems(elems, sep=" | "))
            return E.span(*join_elems(rating.get_rating_buttons(sar), sep=" | "))

            # txt = f"{rating.score or NOT_RATED}"
            # kw = dict(action_param_values=dict(score=rating.score))
            # return sar.instance_action_button(
            #     rating.set_rating_action, label=txt, request_kwargs=kw)

        table = xghtml.Table()
        table.attrib.update(ar.renderer.tableattrs)
        headers = [E.td(gettext("Pupil"))]
        cellstyle = "padding:2pt; margin:0pt; text-align:center;"
        # cellstyle = "text-align:center;"
        for chl in challenges:
            # print(f"20241017 {prj.display_color}")
            headers.append(E.td(
                ar.obj2html(chl, str(chl.skill)), style=cellstyle))
        headers.append(E.td(gettext("Remark")))
        table.head.append(E.tr(*headers))
        # for enr in Enrolment.objects.filter(group=exam.cast.group):
        for resp in ExamResponse.objects.filter(exam=exam).order_by("enrolment__pupil__last_name"):
            # sar = ChallengeRatingsByEnrolment.create_request(parent=ar, master_instance=enr)
            # resp  = rt.models.ratings.ExamResponse.objects.get(exam=exam, enrolment=resp.enrolment)
            sar = RatingsByResponse.create_request(parent=ar, master_instance=resp)
            # sar._insert_sar = None
            cells = [E.td(ar.obj2html(resp, str(resp.enrolment.pupil)))]
            for chl in challenges:
                cells.append(E.td(challenge_cell(sar, chl), style=cellstyle))
            cells.append(E.td(resp.remark, style=cellstyle))
            table.body.append(E.tr(*cells))

        el = table.as_element()
        # if len(toolbar := ar.plain_toolbar_buttons()):
        #     el = E.div(el, E.p(*toolbar))
        return el


class ExamResponses(dd.Table):
    model = "ratings.ExamResponse"
    detail_layout = """
    exam enrolment
    remark
    ratings.RatingsByResponse
    """


class ResponsesByExam(ExamResponses):
    master_key = "exam"
    # default_display_modes = {None: constants.DISPLAY_MODE_HTML}
    column_names = "enrolment score1 score2 ratings remark *"

    @classmethod
    def get_column_names(cls, ar):
        # Builds columns dynamically by request. Called once per UI handle.
        scores = ' '.join(dd.plugins.ratings.get_score_column_names())
        return f"enrolment {scores} ratings remark *"

    @classmethod
    def override_column_headers(self, ar, **headers):
        Challenge = rt.models.ratings.Challenge
        mi = ar.master_instance
        # d = {n: "" for n in dd.plugins.ratings.get_score_column_names()}
        if mi is not None:
            qs = Challenge.objects.filter(exam=mi).order_by('seqno')
            for chl in qs:
                max_score = format_score(chl.max_score)
                headers['score' + str(chl.seqno)
                        ] = f"{chl.skill} ({max_score})"
        return headers


class ExamResponsesByEnrolment(ExamResponses):
    master_key = "enrolment"
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}
    column_names = "exam ratings remark *"
    insert_layout = """
    exam
    remark
    """


class Challenges(dd.Table):
    required_roles = dd.login_required(PrimaTeacher)
    model = 'ratings.Challenge'
    detail_layout = dd.DetailLayout("""
    exam project_section id
    seqno skill max_score
    ratings.RatingsByChallenge
    """, window_size=(60, 'auto'))


class AllChallenges(Challenges):
    required_roles = dd.login_required(PrimaStaff)


class ChallengesBySkill(Challenges):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "skill"
    row_template = "{row.max_score} in {row.exam_or_section}"


class ChallengesByExam(Challenges):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "exam"
    column_names = "skill max_score seqno *"
    stay_in_grid = True
    # detail_layout = dd.DetailLayout("""
    # exam project_sectionid
    # seqno skill max_score
    # ratings.RatingsByChallenge
    # """, window_size=(60, 'auto'))
    insert_layout = """
    skill
    max_score
    """


class ChallengeRatings(dd.Table):
    required_roles = dd.login_required(PrimaTeacher)
    model = 'ratings.ChallengeRating'
    order_by = ['challenge__exam',
                'challenge__project_section', 'challenge__skill']
    # parameters = dict()
    # params_layout = """challenge challenge__exam enrolment"""
    detail_layout = dd.DetailLayout("""
    challenge max_score
    enrolment
    score rating_buttons
    period teacher date_done
    """, window_size=(60, "auto"))


class AllChallengeRatings(ChallengeRatings):
    required_roles = dd.login_required(PrimaStaff)


class ChallengeRatingsByEnrolment(ChallengeRatings):
    master_key = "enrolment"
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}
    insert_layout = """
    challenge
    max_score
    enrolment
    score rating_buttons
    period teacher date_done
    """

    def as_summary_item(self, ar, text=None, **kwargs):
        # must return an ET element
        if text is None:
            exam = self.challenge.exam or self.challenge.project_section
            text = f'{exam}: {self.score} {self.challenge.skill}'
        return super().as_summary_item(ar, text, **kwargs)


class RatingsByResponse(ChallengeRatings):
    master = "ratings.ExamResponse"
    # default_display_modes = { None: constants.DISPLAY_MODE_SUMMARY}
    # column_names = "challenge rating"
    # column_names = "challenge__skill challenge__max_score *"
    column_names = "challenge__skill challenge__max_score score *"
    # column_names = "score *"
    label = _("Ratings by response")
    row_template = '{row.score}/{row.challenge.max_score} {row.challenge.skill}'

    # @classmethod
    # def row_as_summary(cls, ar, obj, text=None, **kwargs):
    #     if text is None:
    #         text = f'{obj.score} {obj.challenge.skill}'
    #     return super().row_as_summary(ar, obj, text, **kwargs)

    # @classmethod
    # def setup_request(self, ar):
    #     super().setup_request(ar)
    #     mi = ar.master_instance
    #     ar.known_values.update(enrolment=resp.enrolment, challenge__exam=resp.exam)

    @classmethod
    def get_request_queryset(cls, ar):
        qs = super().get_request_queryset(ar)
        resp = ar.master_instance
        if resp is None:
            return qs.none()
        qs = qs.filter(enrolment=resp.enrolment, challenge__exam=resp.exam)
        return qs


class RatingsByChallenge(ChallengeRatings):
    master_key = "challenge"
    label = _("Ratings")
    # default_display_modes = { None: constants.DISPLAY_MODE_LIST}
    column_names = "enrolment score *"

# class RatingsByExam(ChallengeRatings):
#     master_key = "challenge__exam"
#     label = _("Ratings")
#     default_display_modes = { None: constants.DISPLAY_MODE_LIST}
#     column_names = "enrolment challenge__max_score score challenge challenge__skill *"

# class RatingsByCourse(ChallengeRatings):
#     master = "school.Course"
#     @classmethod
#     def get_request_queryset(self, ar, **filter):
#         mi = ar.master_instance
#         assert isinstance(mi, rt.models.school.Course)
#         qs = super().get_request_queryset(ar, **filter)
#         return qs.filter(enrolment__group=mi.group, challenge__skill__subject=mi.subject)


class FinalExams(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'ratings.FinalExam'
    column_names = "designation skill max_score *"


class FinalExamRatings(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'ratings.FinalExamRating'
    column_names = "enrolment exam score *"
    detail_layout = """
    exam
    enrolment
    score max_score
    teacher period date_done
    """


class FinalRatingsByEnrolment(FinalExamRatings):
    master_key = "enrolment"
    required_roles = dd.login_required(PrimaTeacher)
    column_names = "exam score teacher date_done *"

# class FinalRatingsByCast(FinalExamRatings):
#     master_key = "enrolment"
#     required_roles = dd.login_required(PrimaTeacher)
#     column_names = "exam enrolment score date_done *"


if dd.is_installed("projects"):

    class ChallengesByProjectSection(Challenges):
        required_roles = dd.login_required(PrimaTeacher)
        master_key = "project_section"
        column_names = "seqno skill max_score id *"
        insert_layout = """
        skill
        max_score
        """

    class ChallengeRatingsByProject(ChallengeRatings):
        master = "ratings.Project"
        label = _("Challenge ratings")
        default_display_modes = {
            70: constants.DISPLAY_MODE_HTML,
            None: constants.DISPLAY_MODE_LIST}
        column_names = "max_score score rating_buttons challenge__skill period *"
        group_by = [lambda obj: obj.challenge.project_section]
        obvious_fields = set(['enrolment'])

        @classmethod
        def get_request_queryset(cls, ar):
            qs = super().get_request_queryset(ar)
            prj = ar.master_instance
            if prj is None:
                return qs.none()
            project_challenges = rt.models.ratings.Challenge.objects.filter(
                project_section__project_template=prj.template)
            qs = qs.filter(challenge__in=project_challenges,
                           enrolment=prj.enrolment)
            # if (pv := ar.param_values) is None: return qs
            return qs

        @classmethod
        def before_group_change(cls, gh, obj):
            return format_html("<h2>{}</h2>", obj.challenge.project_section)
