# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# from pathlib import Path
import datetime

from commondata.demonames.bel import NameFactory
from lino.modlib.system.choicelists import DisplayColors
from lino.modlib.users.utils import create_user
from lino.utils.mldbc import babel_named as named
from lino.utils.quantities import Duration
from lino.modlib.system.choicelists import DurationUnits
from lino.core.roles import SiteAdmin
from lino.utils import AttrDict
from lino.utils import Cycler, i2d, ONE_DAY
from lino.api import rt, dd, _
from django.conf import settings
from django.utils.text import format_lazy

combine = datetime.datetime.combine


# from lino_xl.lib.tickets.choicelists import SiteStates

try:
    from lino_book import DEMO_DATA
except ImportError:
    DEMO_DATA = None

LAST = AttrDict()
MAX_RATINGS = Cycler(5, 10, 20, 12, 6, 8, 15, 20, 30)
ADJECTIVES = Cycler(_("cool"), _("weird"), _("obsolete"), _("great"))

User = rt.models.users.User
UserTypes = rt.models.users.UserTypes
StoredPeriod = rt.models.periods.StoredPeriod
StoredYear = rt.models.periods.StoredYear
Group = rt.models.school.Group
Subject = rt.models.school.Subject
Role = rt.models.school.Role
Cast = rt.models.school.Cast
Grade = rt.models.school.Grade
ProjectSection = rt.models.projects.ProjectSection
Skill = rt.models.school.Skill
Course = rt.models.school.Course
Challenge = rt.models.ratings.Challenge
Enrolment = rt.models.school.Enrolment
Exam = rt.models.ratings.Exam
CertTemplate = rt.models.cert.CertTemplate
CertSection = rt.models.cert.CertSection
CertElement = rt.models.cert.CertElement
Certificate = rt.models.cert.Certificate


def certtpl(desig, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    return CertTemplate(**kwargs)


def grade(ref, desig, ctpl=None, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    kwargs.update(ref=str(ref))
    if ctpl:
        kwargs.update(cert_template=ctpl)
    return Grade(**kwargs)


def create_role(desig, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    return rt.models.school.Role(**kwargs)


def create_subject(desig, **kwargs):
    kwargs = dd.str2kw('designation', desig, **kwargs)
    # print(f"20250115 {kwargs}")
    LAST.define('subject', rt.models.school.Subject(**kwargs))
    return LAST.subject

# def prjskill(desig, max_score=3, **kwargs):
#     kwargs = dd.babelkw('designation', desig, **kwargs)
#     kwargs.update(max_score=max_score)
#     return rt.models.ratings.ProjectSkill(**kwargs)


def create_skill(desig, with_exams=False, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    kwargs.update(subject=LAST.subject, with_exams=with_exams)
    LAST.define('skill', Skill(**kwargs))
    return LAST.skill


def prjtemplate(desig, ref, color, grade, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    kwargs.update(main_skill=LAST.skill)
    kwargs.update(short_header=ref,
                  display_color=DisplayColors.get_by_name(color),
                  grade=Grade.get_by_ref(grade))
    LAST.define('prjtemplate', rt.models.projects.ProjectTemplate(**kwargs))
    return LAST.prjtemplate


def prjsection(desig, **kwargs):
    kwargs = dd.babelkw('designation', desig, **kwargs)
    kwargs.update(project_template=LAST.prjtemplate)
    LAST.define('prjsection', ProjectSection(**kwargs))
    return LAST.prjsection


def pupil(first, last):
    return User(
        first_name=first, last_name=last,
        # user_type=UserTypes.pupil,
        username=f"{first}.{last}".lower())


def teacher(first, last):
    return User(first_name=first, last_name=last,
                user_type=UserTypes.teacher,
                username=f"{first}.{last}".lower())


def objects():

    yield (ct1 := certtpl("Junior"))
    yield (ct2 := certtpl("Senior"))

    yield grade(1, _("First grade"), ct1)
    yield grade(2, _("Second grade"), ct1)
    yield grade(3, _("Third grade"), ct2)
    yield grade(4, _("Fourth grade"), ct2)
    yield grade(5, _("Fifth grade"), ct2)
    yield grade("6", _("Sixth grade"), ct2)
    yield grade("X", _("Alumni"))

    # yield prjskill(_("Work behaviour"), 3)  # Arbeitsverhalten
    # yield prjskill(_("Time managment"), 3)  # Zeitmanagement
    # yield prjskill(_("Correction"), 3)  # Korrektur
    # yield prjskill(_("Cleanliness"), 3)  # Sauberkeit

    yield (class_teacher := create_role(_("Class teacher")))
    yield create_role(_("Catholic religion"))
    yield create_role(_("Protestant religion"))
    # yield create_role(_("Geography"))
    # yield create_role(_("History"))
    # yield create_role(_("Natural science"))
    # yield create_role(_("Art"))
    yield create_role(_("Music"))
    yield create_role(_("Sport"))
    yield create_role(_("Projects"))

    # Unicode pictograms: https://www.compart.com/en/unicode/block/U+1F300
    sports_options = dict(icon_text="⛹")  # 🏊 🏈 ⚽
    french_options = dict(icon_text="🥐")  # 🗼🥖 🍇
    german_options = dict(icon_text="🥨")
    if dd.is_installed("uploads"):
        Upload = rt.models.uploads.Upload
        # icons_dir = Path(rt.models.prima.__file__).parent / "flaticon"
        if DEMO_DATA:
            icons_dir = DEMO_DATA / "pictograms"
            if not icons_dir.exists():
                raise Exception(f"Oops, {icons_dir} doesn't exist!")
            vol = rt.models.uploads.Volume(root_dir=icons_dir, ref="pictograms")
            yield vol
            for fn in icons_dir.iterdir():
                if fn.suffix == ".png":
                    yield Upload(volume=vol, library_file=fn.name)
            sports_options.update(image_file=Upload.objects.get(
                library_file="26bd_soccer.png"))
            french_options.update(image_file=Upload.objects.get(
                library_file="1f347_grapes.png"))
            german_options.update(image_file=Upload.objects.get(
                library_file="1f34e_apple.png"))

    yield create_subject(_("Science"), advanced=True, icon_text="🔬")  # 🧲 🦠
    yield create_skill(_("Geography"))
    yield create_skill(_("History"))
    yield create_skill(_("Natural science"))
    yield create_subject(_("French"), advanced=True, **french_options)
    yield create_skill(_("Reading"))  # Lesen
    yield create_skill(_("Writing"), True)  # Schreiben
    yield create_skill(_("Speaking"), True)  # Sprechen
    yield create_skill(_("Listening"), True)  # Zuhören
    # Umgang mit Texten und Medien
    yield create_skill(_("Dealing with texts and media"), True)
    yield create_subject(_("Mathematics"), advanced=True, icon_text="🖩")  # π
    yield create_skill(_("Arithmetics"), True)
    yield create_skill(_("Stochastics"), True)
    yield create_subject(_("German"), advanced=True, **german_options)
    yield create_skill(_("Reading"))  # Lesen
    yield create_skill(_("Reading comprehension"))  # Leseverständnis
    yield create_skill(_("Writing"), True)  # Schreiben
    yield create_skill(_("Speaking"), True)  # Sprechen
    yield create_skill(_("Listening"), True)  # Zuhören
    # Umgang mit Texten und Medien
    yield create_skill(_("Dealing with texts and media"), True)
    yield create_skill(_("Linguistical thinking"), True)  # Über Sprache reflektieren

    yield create_subject(_("Religion"), advanced=True, icon_text="🕊")
    yield create_skill(_("Knowledge"), True)
    yield create_skill(_("Caring"), True)
    yield create_skill(_("Trusting"), True)

    yield create_subject(_("Music"), rating_type='predicate', icon_text="🎜")  # 🎼
    yield create_skill(_("Choir"))
    yield create_skill(_("Flute"))
    yield create_subject(_("Sport"), rating_type='predicate', **sports_options)
    yield create_skill(_("Jogging"))
    yield create_skill(_("Swimming"))
    yield create_subject(_("Art"), rating_type='smiley', icon_text="🎨")  # 🖌
    # yield create_skill(_("Painting"))
    # yield create_skill(_("Textile"))

    # Erlebnisse spannend erzählen
    yield prjtemplate(_("Telling experiences in an exciting way"), "Erle", "red", "6")
    yield prjsection(_("Presentation"))
    yield prjtemplate(_("About animals"), "Tier", "red", "6")  # Rund um Tiere
    yield prjsection(_("Presentation"))
    yield prjsection(_("Video"))
    yield prjtemplate(_("Reporting"), "Ber", "red", "6")  # Berichten
    yield prjtemplate(_("Describing"), "Bes", "red", "6")  # Beschreiben
    # Geschichten aus dem Leben erzählen
    yield prjtemplate(_("Tell real-life stories "), "Leb", "red", "6")
    yield prjsection(_("Read silently: The storm"))  # Stilles Lesen: Der Schneesturm

    def add_remark(obj):
        kw = dd.str2kw('remark', format_lazy(
            _("This {model} is {adjective}."),
            model=obj._meta.verbose_name, adjective=ADJECTIVES.pop()))
        for k, v in kw.items():
            setattr(obj, k, v)
        return obj

    for ct in CertTemplate.objects.all():
        for subj in Subject.objects.all():
            cs = CertSection(cert_template=ct, subject=subj)
            yield add_remark(cs)
            for skl in Skill.objects.filter(subject=subj):
                yield CertElement(cert_section=cs, skill=skl, max_score=MAX_RATINGS.pop())

    nf = NameFactory()

    MALE_FIRST_NAMES = Cycler(nf.get_male_first_names())
    FEMALE_FIRST_NAMES = Cycler(nf.get_female_first_names())
    LAST_NAMES = Cycler(nf.get_last_names())
    PUPILS_PER_GROUP = 12

    for i in range(11):
        yield teacher(MALE_FIRST_NAMES.pop(), LAST_NAMES.pop())
        yield teacher(FEMALE_FIRST_NAMES.pop(), LAST_NAMES.pop())

    for i in range(6*PUPILS_PER_GROUP):
        yield pupil(MALE_FIRST_NAMES.pop(), LAST_NAMES.pop())
        yield pupil(FEMALE_FIRST_NAMES.pop(), LAST_NAMES.pop())

    StoredPeriod.get_or_create_from_date(dd.today(-420))
    StoredPeriod.get_or_create_from_date(dd.today(-120))
    StoredPeriod.get_or_create_from_date(dd.today())
    PRJSECTIONS = Cycler(ProjectSection.objects.all())
    SKILLS = Cycler(Skill.objects.all())
    SUBJECTS = Cycler(Subject.objects.all())
    ROLES = Cycler(Role.objects.exclude(id=class_teacher.id))
    # PUPILS = Cycler(User.objects.filter(user_type=UserTypes.pupil))
    PUPILS = Cycler(User.objects.filter(user_type=None))
    TEACHERS = Cycler(User.objects.filter(user_type=UserTypes.teacher))

    # raise Exception(f"{TEACHERS.items}")

    # SUBTEA = dict()

    # for i, subj in enumerate(Subject.objects.all()):
    #     SUBTEA[subj] = [TEACHERS.pop() for j in range(1 + i % 3)]

    current_year = StoredYear.objects.first()
    # PERIODS = Cycler(StoredPeriod.objects.filter(year=current_year))
    for a in ("A", "B"):
        for g in Grade.objects.filter(cert_template__isnull=False):
            yield add_remark(grp := Group(
                grade=g, designation=g.ref + a, year=current_year))
            for i in range(PUPILS_PER_GROUP):
                yield Enrolment(pupil=PUPILS.pop(), group=grp)
            for i in range(4):
                yield add_remark(Course(subject=SUBJECTS.pop(), group=grp))

            # Every group has at least a class_teacher, the other roles are
            # optional:
            yield Cast(role=class_teacher, group=grp, user=TEACHERS.pop())
            for i in range(2):
                yield Cast(role=ROLES.pop(), group=grp, user=TEACHERS.pop())
            # for i, r in enumerate(Role.objects.all()):
            #     if i % 4:
            # for subj, teachers in SUBTEA.items():
            #     yield Course(subject=subj, group=grp)
            #     for tea in teachers:
            #         # yield Cast(user=tea, subject=subj, group=grp)
            #         yield Cast(user=tea, group=grp, role=ROLES.pop())

    ar = rt.login("robin")
    while (current_year := current_year.get_next_row()) is not None:
        if dd.today() > current_year.start_date:
            # print(f"20250514 {current_year}")
            for grp in Group.objects.all():
                grp.duplicate.run_from_code(ar)

    for i in range(30):
        yield Challenge(project_section=PRJSECTIONS.pop(), skill=SKILLS.pop(), max_score=MAX_RATINGS.pop())

    CASTS = Cycler(Cast.objects.all())
    for i in range(30):
        cast = CASTS.pop()
        sub = SUBJECTS.pop()
        yield (o := Exam(heading="Test", subject=sub, user=cast.user, group=cast.group))
        SKILLS = Cycler(Skill.objects.filter(subject=sub))
        if len(SKILLS) > 0:
            for j in range(i % 3):
                yield Challenge(exam=o, skill=SKILLS.pop(), max_score=MAX_RATINGS.pop())

    for enr in Enrolment.objects.all():
        for p in StoredPeriod.objects.filter(year=enr.group.year):
            yield Certificate(enrolment=enr, period=p)
