# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from django.utils.html import format_html, mark_safe
from django.utils.text import format_lazy
from lino.utils.html import E, join_elems
from lino.utils import nextref
from lino.utils.mldbc.mixins import BabelDesignated
from lino.modlib.checkdata.choicelists import Checker
from lino.modlib.users.mixins import UserAuthored
from lino.mixins.duplicable import Duplicable
# from lino.modlib.checkdata.models import FixMessagesByController
from lino.modlib.summaries.mixins import Summarized
from lino.mixins import Referrable, Sequenced
from lino_prima.lib.ratings.choicelists import RatingTypes
from lino.api import dd, rt, pgettext, _
from .ui import *


class Grade(BabelDesignated, Referrable):  # hard-coded list in zeugnisse
    class Meta:
        verbose_name = _("Grade")  # Jahrgangsstufe, Schulstufe
        verbose_name_plural = _("Grades")
        abstract = dd.is_abstract_model(__name__, 'Grade')

    cert_template = dd.ForeignKey(
        'cert.CertTemplate', blank=True, null=True)
    rating_conditions = dd.BabelTextField(_("Rating conditions"), blank=True)


class Subject(BabelDesignated, Sequenced):
    class Meta:
        verbose_name = pgettext("in school", "Subject")
        verbose_name_plural = _("Subjects")
        abstract = dd.is_abstract_model(__name__, 'Subject')
        ordering = ['seqno']
    advanced = dd.BooleanField(_("Advanced"), default=False)
    icon_text = dd.CharField(_("Icon"), max_length=5, blank=True, null=True)
    rating_type = RatingTypes.field(blank=True, null=True)
    image_file = dd.ForeignKey('uploads.Upload',
                               verbose_name=_("Image"), blank=True, null=True)


class Skill(BabelDesignated, Sequenced):
    class Meta:
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")
        abstract = dd.is_abstract_model(__name__, 'Skill')
    subject = dd.ForeignKey('school.Subject')
    with_exams = dd.BooleanField(_("With final exams"))  # Mit Abschlusstests

    # def __str__(self):
    #     return f"{self.subject}:{super().__str__()}"

    def get_siblings(self):
        return self.__class__.objects.filter(subject=self.subject)


class Group(BabelDesignated, Duplicable):  # zeugnisse.Klasse
    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        abstract = dd.is_abstract_model(__name__, 'Group')
        ordering = ['designation']

    quickfix_checkdata_label = _("Fill missing courses and certificates")
    extra_display_modes = {constants.DISPLAY_MODE_GALLERY}

    grade = dd.ForeignKey('school.Grade')
    year = dd.ForeignKey('periods.StoredYear', blank=True)
    remark = dd.BabelTextField(_("Remark"), blank=True, format="plain")

    def on_duplicate(self, ar, master):
        if (next := self.year.get_next_row()):
            self.year = next
        if (next := self.grade.get_next_row()):
            self.grade = next
        if (next := nextref(self.designation)) is not None:
            self.designation = next
        else:
            self.designation += " (copy)"
        super().on_duplicate(ar, master)
        # ar.param_values['year'] = None

    # def on_create(self, ar):
    #     print(f"20250514 {ar} {ar.selected_rows}")
    #     pass

    @classmethod
    def get_simple_parameters(cls):
        yield super().get_simple_parameters()
        yield 'year'

    # @classmethod
    # def param_defaults(cls, ar, **kw):
    #     kw = super().param_defaults(ar, **kw)
    #     kw.update(year=rt.models.periods.StoredYear.get_or_create_from_date(
    #         dd.today()))
    #     return kw

    def full_clean(self, *args, **kwargs):
        if self.year_id is None:
            self.year = rt.models.periods.StoredYear.get_or_create_from_date(dd.today())
        super().full_clean(*args, **kwargs)

    def as_tile(self, ar, **kwargs):
        s = f"""<span style="font-size:2rem; float:left; padding-right:1rem;">{
            ar.obj2htmls(self)}</span> """
        s += _("{} pupils").format(Enrolment.objects.filter(group=self).count())
        s += "<br>"
        s += " ".join([
            ar.obj2htmls(
                obj, obj.subject.icon_text or str(obj.subject), title=str(obj.subject))
            for obj in Course.objects.filter(group=self)])
        return mark_safe(s)

    def as_paragraph(self, ar, **kwargs):
        s = ar.obj2htmls(self)
        if not ar.is_obvious_field("year"):
            s += format_html(_(" ({year})"), year=str(self.year))
        return mark_safe(s)

    def __str__(self):
        s = super().__str__()
        if not self.year.covers_date(dd.today()):
            s += format_html(_(" ({year})"), year=self.year)
        return mark_safe(s)


Group.duplicate.required_roles = {dd.SiteAdmin}


class Course(dd.Model):
    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        abstract = dd.is_abstract_model(__name__, 'Course')

    group = dd.ForeignKey('school.Group', related_name='courses')
    subject = dd.ForeignKey('school.Subject', related_name='courses')
    remark = dd.BabelTextField(_("Remark"), blank=True, format="plain")

    allow_cascaded_delete = ['group']

    def __str__(self):
        return _("{subject} in {group}").format(
            subject=self.subject, group=self.group)

    def get_str_words(self, ar):
        if not ar.is_obvious_field("subject"):
            yield str(self.subject)
        if not ar.is_obvious_field("group"):
            yield _("in {group}").format(group=self.group)


class Role(BabelDesignated):
    class Meta:
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        abstract = dd.is_abstract_model(__name__, 'Role')


class Cast(dd.Model):  # zeugnisse.LehrerRolle

    class Meta:
        verbose_name = _("Cast")
        verbose_name_plural = _("Casts")
        abstract = dd.is_abstract_model(__name__, 'Cast')
        # ordering = ['user', 'group__designation', 'subject', 'role']
        ordering = ['user', 'group__designation', 'role']
        # unique_together = ['user', 'group', 'role']

    user = dd.ForeignKey(
        "users.User",
        verbose_name=_("Teacher"),
        related_name="%(app_label)s_%(class)s_set_by_user",
        blank=True,
        null=True)
    group = dd.ForeignKey('school.Group')
    # subject = dd.ForeignKey('school.Subject')
    role = dd.ForeignKey('school.Role', blank=True, null=True)

    allow_cascaded_delete = ['group']

    def __str__(self):
        # text = str(self.subject)
        text = _("{teacher}").format(teacher=self.user)
        if self.role is not None:
            text += " " + _("as {role}").format(role=self.role)
        text += " " + _("in {group}").format(group=self.group)
        return text

    def get_str_words(self, ar):
        if self.user != ar.get_user() and not ar.is_obvious_field("user"):
            yield _("{teacher} as").format(teacher=self.user)
        yield str(self.role)
        if not ar.is_obvious_field("group"):
            yield _("in {group}").format(group=self.group)

    @classmethod
    def get_simple_parameters(cls):
        yield super().get_simple_parameters()
        yield "user"  # cls.author_field_name)
        yield 'group__year'

    # @classmethod
    # def param_defaults(cls, ar, **kw):
    #     kw = super().param_defaults(ar, **kw)
    #     kw.update(group__year=rt.models.periods.StoredYear.get_or_create_from_date(
    #         dd.today()))
    #     return kw


# dd.update_field(Cast, 'user', verbose_name=_("Teacher"))


class Enrolment(dd.Model):
    class Meta:
        verbose_name = _("Enrolment")
        verbose_name_plural = _("Enrolments")
        abstract = dd.is_abstract_model(__name__, 'Enrolment')
        ordering = ['pupil__last_name', 'pupil__first_name', 'group__year']

    group = dd.ForeignKey('school.Group')  # , related_name='enrolments')
    pupil = dd.ForeignKey('users.User', verbose_name=_("Pupil"))

    allow_cascaded_delete = ['group']
    # IOW When end user deletes a group, Lino removes all enrolments
    # automatically, but Lino will veto when user tries to delete a pupil for
    # which there is an enrolment.

    def __str__(self):
        return f"{self.pupil} ({self.group})"

    def get_str_words(self, ar):
        if not ar.is_obvious_field("pupil"):
            yield str(self.pupil)
        if not ar.is_obvious_field("group"):
            yield _("in {group}").format(group=self.group)

    # def as_summary_item(self, ar, text=None):
    #     if text is None:
    #         if ar.is_obvious_field("pupil"):
    #             text = f"{self.group}"
    #         elif ar.is_obvious_field("group"):
    #             text = f"{self.pupil}"
    #         else:
    #             text = str(self)
    #     return super().as_summary_item(ar, text)

    @dd.displayfield(_("Certificates"))
    def certificates(self, ar):
        if ar is None:
            return ''
        Certificate = rt.models.cert.Certificate
        elems = []
        insert_button_attrs = dict(style="text-align: center;")
        sar = rt.models.cert.CertificatesByEnrolment.create_request(
            parent=ar, master_instance=self)
        qs = rt.models.periods.StoredPeriod.objects.filter(year=self.group.year)
        for p in qs:
            try:
                crt = Certificate.objects.get(enrolment=self, period=p)
            except Certificate.DoesNotExist:
                btn = sar.gen_insert_button(None, insert_button_attrs,
                                            enrolment=str(self), enrolmentHidden=self.pk,
                                            period=str(p), periodHidden=p.pk)
                if btn is not None:
                    elems.append(btn)
                continue
            elems.append(sar.obj2html(crt, p.nickname))
        return E.p(*join_elems(elems, sep=", "))


class GroupChecker(Checker):
    verbose_name = _("Check for missing courses")
    model = Group
    msg_missing = _("No course for {subject} in {group}.")

    def get_checkdata_problems(self, ar, obj, fix=False):
        CertSection = rt.models.cert.CertSection
        tpl = obj.grade.cert_template
        for cs in CertSection.objects.filter(cert_template=tpl):
            if cs.subject_id and cs.subject.advanced:
                qs = Course.objects.filter(group=obj, subject=cs.subject)
                if not qs.exists():
                    yield (True, format_lazy(
                        self.msg_missing, subject=cs.subject, group=obj))
                    if fix:
                        course = Course(subject=cs.subject, group=obj)
                        course.full_clean()
                        course.save()


GroupChecker.activate()


@dd.receiver(dd.post_analyze)
def my_details(sender, **kw):
    sender.models.system.SiteConfigs.set_detail_layout("""
    default_build_method
    simulate_today
    """)
