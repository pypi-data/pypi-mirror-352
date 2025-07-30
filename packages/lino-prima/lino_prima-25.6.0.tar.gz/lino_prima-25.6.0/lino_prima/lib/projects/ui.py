# -*- coding: UTF-8 -*-
# Copyright 2024 Rumma & Ko Ltd
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

from lino_prima.lib.school.ui import EnrolmentsByGroup
from lino_prima.lib.school.roles import PrimaStaff, PrimaTeacher, PrimaPupil
from lino_prima.lib.ratings.utils import NOT_RATED, format_score

from .choicelists import GeneralRatings


# class ProjectSkills(dd.Table):
#     required_roles = dd.login_required(PrimaStaff)
#     model = 'projects.ProjectSkill'
#

class ProjectTemplates(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'projects.ProjectTemplate'
    # column_names = "grade short_header designation *"
    column_names = "grade display_color short_header designation *"
    detail_layout = """
    designation short_header
    display_color id
    main_skill grade
    SectionsByProject
    """


class ProjectTemplatesBySkill(ProjectTemplates):
    master_key = "main_skill"


class ProjectTemplatesByGrade(ProjectTemplates):
    master_key = "grade"


class ProjectSections(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'projects.ProjectSection'
    detail_layout = """
    seqno designation
    project_template id
    ratings.ChallengesByProjectSection
    """
    default_display_modes = {None: constants.DISPLAY_MODE_LIST}


class SectionsByProject(ProjectSections):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "project_template"


class ProjectDetail(dd.DetailLayout):
    main = "general more"

    general = dd.Panel("""
    enrolment date_started
    remark
    general_ratings:30 ratings.ChallengeRatingsByProject:40
    """, _("General"))

    more = dd.Panel("""
    template id
    ratings_done total_score total_max_score
    # ratings.RatingsByProject
    """, _("More"))

    general_ratings = "\n".join(
        [pf.field_name for pf in GeneralRatings.get_list_items()])


class Projects(dd.Table):
    required_roles = dd.login_required(PrimaStaff)
    model = 'projects.Project'
    detail_layout = "projects.ProjectDetail"


class ProjectsByTemplate(Projects):
    master_key = "template"


class ProjectsByEnrolment(Projects):
    required_roles = dd.login_required(PrimaTeacher)
    master_key = "enrolment"
    default_display_modes = {None: constants.DISPLAY_MODE_SUMMARY}
    insert_layout = dd.InsertLayout("""
    enrolment
    template
    remark
    """, window_size=(40, 15))  # , hidden_elements="template")


# class ProjectRatings(dd.Table):
#     required_roles = dd.login_required(PrimaTeacher)
#     model = 'ratings.ProjectRating'
#     detail_layout = dd.DetailLayout("""
#     project_skill score project_skill__max_score
#     project
#     teacher period date_done
#     """, window_size=(60, "auto"))
#
# class AllProjectRatings(ProjectRatings):
#     required_roles = dd.login_required(PrimaStaff)

# class RatingsByProject(ProjectRatings):
#     master_key = "project"
#     label = _("Project ratings")
#     default_display_modes = { None: constants.DISPLAY_MODE_LIST}


# class PupilsAndProjectsByGroup(dd.VirtualTable):

class PupilsAndProjectsByGroup(EnrolmentsByGroup):
    required_roles = dd.login_required(PrimaTeacher)
    master = "school.Group"
    label = _("Projects")
    # label = _("Projects by group")
    default_display_modes = {None: constants.DISPLAY_MODE_HTML}

    @classmethod
    def table_as_html(cls, ar):
        ProjectTemplate = rt.models.projects.ProjectTemplate
        Enrolment = rt.models.school.Enrolment
        Project = rt.models.projects.Project
        grp = ar.master_instance
        # print(f"20241017 cellattrs {ar.renderer.cellattrs}")
        templates = ProjectTemplate.objects.filter(
            grade=grp.grade).order_by("display_color")
        if not templates.exists():
            return _("There are no {projects} configured for grade {grade}.").format(
                projects=Project._meta.verbose_name_plural, grade=grp.grade)

        cellstyle = "padding:2pt; margin:0pt; text-align:center;"
        insert_button_attrs = dict(style="text-align:center;")

        def makecell(sar, tpl):
            try:
                prj = Project.objects.get(
                    enrolment=sar.master_instance, template=tpl)
            except Project.DoesNotExist:
                btn = sar.gen_insert_button(None, insert_button_attrs,
                                            template=str(tpl), templateHidden=tpl.pk)
                if btn is None:
                    return ""
                return E.td(btn, style=cellstyle)
                # return E.p(txt, btn, align="center")
                # return str("+")
            if prj.ratings_done == 100:
                color = "#48c78e"
                txt = "☑"  # U+2611
            else:
                color = "#ffe08a"
                txt = "⚒"  # U+2692
            if False:
                if prj.total_max_score:
                    score = format_score(100 * prj.total_score /
                                         prj.total_max_score) + "%"
                else:
                    score = NOT_RATED
                if prj.ratings_done is None:
                    cv = 0
                else:
                    cv = int(prj.ratings_done / 20)  # a value 0..5
                # completion = "▇" * cv + "▁" * (5-cv)
                # completion = "|" * cv + "." * (5-cv)
                completion = "▮" * cv + "▯" * (5-cv)
                txt = f"{completion} {score}"
            return E.td(sar.obj2html(prj, txt),
                        style=cellstyle + "background-color:" + color)

        table = xghtml.Table()
        table.attrib.update(ar.renderer.tableattrs)
        headers = [E.td(gettext("Pupil"))]
        # cellstyle = "text-align:center;"
        for prj in templates:
            # print(f"20241017 {prj.display_color}")
            # headers.append(E.td(
            #     ar.obj2html(prj, prj.short_header,
            #         style=f"color:{prj.display_color.font_color};"),
            #     style=cellstyle + f"background-color:{prj.display_color.name};"))
            # headers.append(E.td(
            #     ar.obj2html(prj, prj.short_header),
            #     style=cellstyle + f"background-color:{prj.display_color.name};color:{prj.display_color.font_color};"))
            headers.append(E.td(prj.short_header,
                                style=cellstyle + f"background-color:{prj.display_color.name};color:{prj.display_color.font_color};"))
        table.head.append(E.tr(*headers))
        for enr in Enrolment.objects.filter(group=grp):
            sar = ProjectsByEnrolment.create_request(parent=ar, master_instance=enr)
            cells = [E.td(ar.obj2html(enr, str(enr.pupil)))]
            for prj in templates:
                cells.append(makecell(sar, prj))
            table.body.append(E.tr(*cells))

        el = table.as_element()
        # if len(toolbar := ar.plain_toolbar_buttons()):
        #     el = E.div(el, E.p(*toolbar))
        return el
