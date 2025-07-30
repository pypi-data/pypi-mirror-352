# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from django.utils.html import format_html, mark_safe
# from lino.utils.html import E, tostring
from lino.core import constants
from lino.core.roles import Explorer
from lino.modlib.users.mixins import My
from lino.api import dd, rt, _

from lino_prima.lib.school.roles import PrimaStaff, PrimaTeacher, PrimaPupil

# NOT_RATED = '▨'
# NOT_RATED = '◻' # 25fb white medium square
# NOT_RATED = '□' # 25a1 white square
# NOT_RATED = '▭' # 25ad white rectagle
NOT_RATED = '☐'  # 2610 ballot box


class CertificateDetail(dd.DetailLayout):
    main = "ratings verdict"

    ratings = dd.Panel("""
    enrolment period state id
    SectionResponsesByCertificate
    # RatingsByCertificate
    """, _("Ratings"))

    verdict = dd.Panel("""
    social_skills_comment
    final_verdict
    absences_p absences_m absences_u
    """, _("Verdict"))


class Certificates(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'cert.Certificate'
    column_names = "enrolment period state *"
    detail_layout = "cert.CertificateDetail"
    insert_layout = """
    enrolment
    period
    """

# class MyCertificates(Certificates, My):
#     required_roles = dd.login_required(PrimaTeacher)


class CertificatesByEnrolment(Certificates):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "enrolment"
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}
    # row_template = "{row.period.nickname}"


class CertificatesByGroup(Certificates):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "enrolment__group"
    default_display_modes = {None: constants.DISPLAY_MODE_GRID}
    column_names = "enrolment period absences_m absences_p absences_u *"
    order_by = ['enrolment', 'period']

    @classmethod
    def param_defaults(self, ar, **kw):
        kw = super().param_defaults(ar, **kw)
        kw['period'] = rt.models.periods.StoredPeriod.get_or_create_from_date(
            dd.today())
        return kw


class CertTemplates(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'cert.CertTemplate'
    detail_layout = """
    designation
    cert.SectionsByTemplate
    """


class CertSections(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'cert.CertSection'
    column_names = "cert_template seqno subject remark *"
    detail_layout = """
    cert_template seqno subject id
    remark
    cert.ElementsBySection
    """


class SectionsByTemplate(CertSections):
    master_key = 'cert_template'
    column_names = "seqno subject remark *"


class CertElements(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'cert.CertElement'
    column_names = "cert_section seqno skill max_score *"
    # detail_layout = """
    # cert_section
    # seqno
    # skill max_score
    # id
    # """


class ElementsBySection(CertElements):
    master_key = 'cert_section'
    column_names = "seqno skill max_score *"


class ElementResponses(dd.Table):
    model = 'cert.ElementResponse'
    abstract = True
    detail_layout = """
    section_response section_response__certificate__enrolment section_response__certificate__period
    cert_element cert_element__skill max_score
    # ratings_done total_max_score total_score
    computed_rating score rating_buttons
    ratings_report
    """


class AllElementResponses(ElementResponses):
    required_roles = dd.login_required(PrimaStaff)


class RatingsBySkill(ElementResponses):
    # master = 'cert.Certificate'
    master_key = 'cert_element__skill'
    required_roles = dd.login_required(PrimaTeacher)
    column_names = "cert_element max_score score *"
    # order_by = ['cert_element__cert_section', 'cert_element']
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}
    row_template = "{row.section_response.certificate.enrolment}"


class RatingsByResponse(ElementResponses):
    master_key = 'section_response'
    required_roles = dd.login_required(PrimaTeacher)
    column_names = "cert_element #total_score rating_buttons #score max_score  *"
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}
    obvious_fields = {'certificate', 'section_response'}

# class RatingsByCertificate(ElementResponses):
#     # master = 'cert.Certificate'
#     master_key = 'response__certificate'
#     required_roles = dd.login_required(PrimaTeacher)
#     column_names = "cert_element total_score max_score score *"
#     order_by = ['cert_element__cert_section', 'cert_element']
#     group_by = [lambda obj: obj.cert_element.cert_section]
#     default_display_modes = { None: constants.DISPLAY_MODE_LIST}
#     # row_template = "{row.cert_element} {row.total_score} / {row.score or '☐'} ({row.ratings_done}% done)"
#
#     @classmethod
#     def before_group_change(cls, gh, obj):
#         return format_html("<h2>{}</h2>", obj.cert_element.cert_section)
#
#     @classmethod
#     def row_as_paragraph(cls, ar, self):
#         text = str(self.cert_element.skill) + " (" + _("computed") + " "
#         text += self.computed_text()
#         # text += " " + str(self.ratings_done) + "% done)"
#         text += "): "
#         # text += ar.obj2htmls(self, str(self.score or NOT_RATED))
#
#         elems = list(map(tostring, self.get_rating_buttons(ar)))
#         text += " | ".join(elems)
#         return mark_safe(text)


class SectionResponses(dd.Table):
    abstract = True
    model = "cert.SectionResponse"
    detail_layout = """
    certificate section rating_type max_score score smiley predicate
    remark
    cert.RatingsByResponse cert.ExamResponsesBySection
    """


class AllSectionResponses(SectionResponses):
    required_roles = dd.login_required(Explorer)

# ratings = dd.resolve_app('ratings')
# class ExamResponsesBySection(ratings.ExamResponses):


if dd.is_installed("ratings"):

    class ExamResponsesBySection(dd.Table):
        model = "ratings.ExamResponse"
        master = "cert.SectionResponse"
        detail_layout = """
        exam enrolment
        remark
        ratings.RatingsByResponse
        """
        default_display_modes = {None: constants.DISPLAY_MODE_HTML}
        column_names = "exam remark ratings *"

        # @classmethod
        # def get_master_instance(cls, ar, model, pk):
        #     sr = model.objects.get(pk=pk)

        @classmethod
        def get_filter_kw(cls, ar, **kwargs):
            sr = ar.master_instance
            if sr is None:
                return None
            kwargs.update(enrolment=sr.certificate.enrolment)
            kwargs.update(exam__period=sr.certificate.period)
            return super().get_filter_kw(ar, **kwargs)

else:
    ExamResponsesBySection = dd.DummyPanel


class SectionResponsesByCertificate(SectionResponses):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "certificate"
    column_names = "section total_score total_max_score rating_buttons remark *"
