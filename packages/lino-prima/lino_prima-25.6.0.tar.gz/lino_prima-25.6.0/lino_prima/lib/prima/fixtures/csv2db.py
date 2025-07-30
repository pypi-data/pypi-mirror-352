# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# Import a set of csv files that have been created using db2csv.py:
# https://gitlab.com/synodalsoft/zeugnisse/-/blob/main/db2csv.py

# Usage:
# go prima1
# pm initdb std csv2db demo_users demo2 checkdata checksummaries

import csv
from pathlib import Path
import datetime

from django.conf import settings
from django.utils.text import format_lazy
from lino.modlib.system.choicelists import DisplayColors
from lino.modlib.users.utils import create_user
from lino.utils.mldbc import babel_named as named
from lino.utils.instantiator import make_if_needed
from lino.utils.quantities import Duration
from lino.core.roles import SiteAdmin
from lino.utils import AttrDict
from lino.utils import Cycler, i2d, ONE_DAY
from lino.api import rt, dd, _

combine = datetime.datetime.combine

LAST = AttrDict()

UserTypes = rt.models.users.UserTypes
User = rt.models.users.User
Grade = rt.models.school.Grade
Course = rt.models.school.Course
Enrolment = rt.models.school.Enrolment
Challenge = rt.models.ratings.Challenge
Project = rt.models.projects.Project
GeneralRatings = rt.models.projects.GeneralRatings
# ProjectSkill = rt.models.projects.ProjectSkill
FinalExam = rt.models.ratings.FinalExam
Skill = rt.models.school.Skill
Subject = rt.models.school.Subject
ProjectSection = rt.models.projects.ProjectSection
StoredPeriod = rt.models.periods.StoredPeriod
PeriodStates = rt.models.periods.PeriodStates
Cast = rt.models.school.Cast
Role = rt.models.school.Role
Certificate = rt.models.cert.Certificate
CertSection = rt.models.cert.CertSection
CertElement = rt.models.cert.CertElement
ElementResponse = rt.models.cert.ElementResponse
SectionResponse = rt.models.cert.SectionResponse

FARBE2COLOR = {
    1: "red",  # Red#ff6d6d,0
    2: "blue",  # Blau,#9797ff,1
    3: "green",  # Grün,#72ff72,2
    4: "yellow",  # Gelb,#ffff70,3
    5: "violet",  # Violett,#fc6cfc,4
}

ICON_TEXTS = {
    "Musik": "🎜",
    "Kunst": "🎨",
    "Sport": "⛹",
    "Religion": "🕊",
    "Wissenschaften": "🔬",
    "Deutsch": "🕮",
    "Französisch": "🥐",
    "Mathematik": "🖩",
}


def datedone(s):
    parts = s.split()
    return parts[0]


def uid(old):
    # convert id in Schüler.csv to id in users.User
    return int(old) + 100


def sk2skill(skid):
    return int(skid) + 500


def grade(ref, desig, ct=None):
    kwargs = dd.babelkw('designation', desig)
    kwargs.update(ref=str(ref))
    kwargs.update(cert_template_id=ct)
    return Grade(**kwargs)


def update_or_create(m, **kwargs):
    if (obj := m.objects.filter(id=kwargs['id']).first()) is not None:
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj
    return m(**kwargs)


def get_or_create(model, **kwargs):
    # similar to Djanop's QuerySet.get_or_create() but calls full_clean
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:
        obj = model(**kwargs)
        obj.full_clean()
        obj.save()
    return obj


def find_teachers(s):
    s = s.lower()
    names = {s}
    for sep in (",", " und "):
        if sep in s:
            names = set([i.strip() for i in s.split(sep)])
    for u in User.objects.all():
        if f"{u.first_name} {u.last_name}".lower() in names:
            yield u
        elif f"{u.last_name} {u.first_name}".lower() in names:
            yield u


class Loader:
    def __init__(self):
        self.max_exam_id = 0
        self.max_group_id = 0

    def common_objects(self):

        STUFEN = (
            (1, 'Erste Klasse'),
            (3, 'Zweite Klasse'),
            (4, 'Mittelstufe'),
            (2, 'Oberstufe'))
        for k, v in STUFEN:
            yield rt.models.cert.CertTemplate(id=k, designation=v)

        yield grade(1, _("First grade"), 1)
        yield grade(2, _("Second grade"), 3)
        yield grade(3, _("Third grade"), 4)
        yield grade(4, _("Fourth grade"), 4)
        yield grade(5, _("Fifth grade"), 2)
        yield grade("6", _("Sixth grade"), 2)
        yield grade("X", _("Alumni"))

        self.SOZIALVERHALTEN = Subject(
            id=20, designation="Sozialverhalten", rating_type="smiley",
            icon_text="☯")
        yield self.SOZIALVERHALTEN
        self.ARBEITSVERHALTEN = Subject(
            id=21, designation="Arbeitsverhalten", rating_type="smiley",
            icon_text="💪")
        yield self.ARBEITSVERHALTEN

        self.ska2section = dict()
        # SozialKompetenzAbschnitt.csv
        for (id, vorlage, titel, ord_outer) in [
            (2, 2, self.SOZIALVERHALTEN, 0),
            (15, 3, self.SOZIALVERHALTEN, 0),
            (17, 4, self.SOZIALVERHALTEN, 0),
            (13, 1, self.SOZIALVERHALTEN, 0),
            (18, 4, self.ARBEITSVERHALTEN, 1),
            (1, 2, self.ARBEITSVERHALTEN, 1),
            (14, 1, self.ARBEITSVERHALTEN, 1),
            (16, 3, self.ARBEITSVERHALTEN, 1)
        ]:
            yield (obj := CertSection(
                id=id+100, cert_template_id=vorlage, subject=titel,
                seqno=ord_outer+100))
            self.ska2section[id] = obj

        self.klassenleiter = Role(designation="Klassenleiter")
        yield self.klassenleiter
        self.geographielehrerin = Role(designation="Geographielehrerin")
        yield self.geographielehrerin
        self.geschichtslehrerin = Role(designation="Geschichtslehrerin")
        yield self.geschichtslehrerin
        self.techniklehrerin = Role(designation="Techniklehrerin")
        yield self.techniklehrerin
        self.ev_religionslehrerin = Role(designation="Evangelisch")
        yield self.ev_religionslehrerin
        self.ka_religionslehrerin = Role(designation="Katholisch")
        yield self.ka_religionslehrerin
        self.bausteine = Role(designation="Bausteine")
        yield self.bausteine

    def make_cast_if_needed(self, subject, teacher, group, role):
        yield make_if_needed(Course, subject=subject, group=group)

        # Make sure that there is at least one cast for this teacher and this
        # group. Don't create more than one cast per teacher and group. Let it
        # be if there is already another cast, anyway we are just guessing the
        # casts:
        qs = Cast.objects.filter(user=teacher, group=group)
        if not qs.exists():
            yield make_if_needed(Cast, role=role, user=teacher, group=group)


def csv2db(loader, import_dir, start_year, closed):

    import_dir = Path(import_dir).expanduser()

    def csv2dicts(filename):
        filename = import_dir / filename
        print(f"Reading {filename}")
        with open(filename) as csvfile:
            for r in csv.DictReader(csvfile):
                yield r

    # unknown_teacher = User.objects.order_by("id").first()
    # # unknown_teacher = User.objects.get(username="robin")
    # print(f"The unknown teacher is {unknown_teacher}")

    periode1 = StoredPeriod.get_or_create_from_date(datetime.date(start_year, 9, 1))
    periode2 = StoredPeriod.get_or_create_from_date(datetime.date(start_year+1, 3, 1))

    if periode1.year != periode2.year:
        raise Exception(f"{periode1.year} is not {periode2.year}")

    if closed:
        for p in (periode1, periode2):
            p.state = PeriodStates.closed
            yield p
        periode1.year.state = PeriodStates.closed
        yield periode1.year

    print(f"Importing {periode1.year}")

    def p2p(s):
        if s == "1":
            return periode1
        elif s == "2":
            return periode2
        else:
            raise Exception(f"20241023 Unknown period {repr(s)}")
        # periode
        # return StoredPeriod.objects.get(id=int(old))

    def klasse2group(i):
        i = int(i)
        if periode1.year.ref == "2024/25":
            i += 1000
        loader.max_group_id = max(loader.max_group_id, i)
        return i

    def examid(i):
        i = int(i)
        if periode1.year.ref == "2024/25":
            i += 10000  # 20241022 2023/24 max exam id was 9162
        loader.max_exam_id = max(loader.max_exam_id, i)
        return i

    def sectionresponse_id(i):
        i = int(i)
        if periode1.year.ref == "2024/25":
            i += 55000  # 20241128 2023/24 max SectionResponse id was 52066
        return i

    def get_certificate(r):
        p = p2p(r['periode'])
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']),
                group__year=p.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! Enrolment does not exist: {r}")
            # continue
        try:
            return Certificate.objects.get(
                enrolment=enr,
                period=p)
        except Certificate.DoesNotExist:
            raise Exception(f"Oops! Certificate does not exist: {enr} {p}")
            # continue

    main_subjects = []
    science_subject = None
    sport_subject = None
    religion_subject = None
    for r in csv2dicts("Fach.csv"):
        # id,name,advanced
        kwargs = dict(id=r['id'], designation=r['name'], advanced=r['advanced'])
        if r['name'] in {"Musik", "Kunst", "Sport"}:
            kwargs.update(rating_type="predicate")
        if r['name'] in ICON_TEXTS:
            kwargs.update(icon_text=ICON_TEXTS[r['name']])
        yield (obj := update_or_create(Subject, **kwargs))
        if obj.designation == ("Sport"):
            sport_subject = obj
        if obj.designation == ("Religion"):
            religion_subject = obj
        if obj.designation == ("Wissenschaften"):
            science_subject = obj
        if obj.designation in {"Deutsch", "Französisch", "Mathematik"}:
            main_subjects.append(obj)

    for r in csv2dicts("Kompetenz.csv"):
        # id,beschreibung,fach,mit_abschlusstests
        subject = Subject.objects.get(id=r['fach'])
        if subject == science_subject:
            try:
                subject = Subject.objects.get(designation=r['beschreibung'])
            except Subject.DoesNotExist:
                subject = Subject(designation=r['beschreibung'])
                yield subject
                # print(f"20241121 Created science subject {subject}")
        kwargs = dict(
            id=r['id'],
            designation=r['beschreibung'],
            subject=subject,
            with_exams=r['mit_abschlusstests']
        )
        yield update_or_create(Skill, **kwargs)

    for r in csv2dicts("Baustein.csv"):
        # id,name,kürzel,farbe,jahrgang,hauptkompetenz
        kwargs = dict(
            id=r['id'], designation=r['name'],
            short_header=r['kürzel'],
            display_color=FARBE2COLOR[int(r['farbe'])],
            main_skill_id=r['hauptkompetenz'],
            grade=Grade.objects.get(id=r['jahrgang'])
        )
        yield update_or_create(rt.models.projects.ProjectTemplate, **kwargs)

    for r in csv2dicts("BausteinAbschnitt.csv"):
        # id,name,leistungsblock_ptr,baustein,ord_outer
        kwargs = dict(
            id=r['id'], designation=r['name'],
            project_template_id=r['baustein'],
            seqno=int(r['ord_outer'])+1
        )
        yield update_or_create(ProjectSection, **kwargs)

    # for r in csv2dicts("BausteinArbeit.csv"):
    #     # id,name,max_punkte
    #     kwargs = dict(
    #         id=r['id'], designation=r['name'],
    #         max_score=r['max_punkte']
    #     )
    #     yield update_or_create(rt.models.projects.ProjectSkill, **kwargs)

    for r in csv2dicts("ZeugnisAbschnitt.csv"):
        # id,vorlage,fach,fixtext,ord_outer
        # subject = Subject.objects.get(id=r['fach'])
        kwargs = dict(
            id=r['id'],
            cert_template_id=r['vorlage'],
            # subject=subject,
            subject_id=r['fach'],
            remark=r['fixtext'],
            # advanced=subject.advanced,
            seqno=int(r['ord_outer'])+1,
        )
        yield update_or_create(CertSection, **kwargs)

    for r in csv2dicts("SozialKompetenz.csv"):
        # id,abschnitt,name,ord_inner
        cs = loader.ska2section[int(r['abschnitt'])]
        kwargs = dict(
            id=sk2skill(r['id']),
            subject=cs.subject,
            designation=r['name'],
            with_exams=False,
            # with_smilies=True,
        )
        # seqno=r['ord_inner']
        yield update_or_create(Skill, **kwargs)

    for r in csv2dicts("ZeugnisElement.csv"):
        # id,abschnitt,kompetenz,max_punkte,ord_inner
        kwargs = dict(
            id=r['id'],
            cert_section_id=r['abschnitt'],
            skill_id=r['kompetenz'],
            max_score=r['max_punkte'],
            seqno=int(r['ord_inner'])+1,
        )
        yield update_or_create(CertElement, **kwargs)

    for r in csv2dicts("Teacher.csv"):
        # id,password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined
        kwargs = dict(
            id=r['id'],
            username=r['username'],
            first_name=r['first_name'],
            last_name=r['last_name'],
            email=r['email'],
            password=r['password'],
        )
        if r['is_superuser'] == "True":
            kwargs.update(user_type=UserTypes.admin)
        else:
            kwargs.update(user_type=UserTypes.teacher)
        yield update_or_create(User, **kwargs)

    for r in csv2dicts("Klasse.csv"):
        # id, name, jahrgang, klassenleiterinnen, ev_religionslehrerin,
        # ka_religionslehrerin, sportlehrerin, geographielehrerin,
        # geschichtslehrerin, techniklehrerin
        kwargs = dict(
            id=klasse2group(r['id']),
            designation="{jahrgang}{name}".format(**r),
            year=periode1.year,
            grade=Grade.objects.get(id=r['jahrgang']),
            remark=f"KlassenleiterInnen: {r['klassenleiterinnen']}",
        )
        yield (grp := rt.models.school.Group(**kwargs))

        if r['ev_religionslehrerin'] or r['ka_religionslehrerin']:
            remark = "LehrerInnen:"
            if r['ka_religionslehrerin']:
                remark += f" {r['ka_religionslehrerin']} (Katholische Religion)"
            if r['ev_religionslehrerin']:
                remark += f", {r['ev_religionslehrerin']} (Evangelische Religion)"
            yield Course(group=grp, subject=religion_subject, remark=remark)

        if r['sportlehrerin']:
            remark = f"LehrerInnen: {r['sportlehrerin']}"
            yield Course(group=grp, subject=sport_subject, remark=remark)

        if r['geographielehrerin'] or r['geschichtslehrerin'] or r['techniklehrerin']:
            remark = "LehrerInnen:"
            if r['geographielehrerin']:
                remark += f" {r['geographielehrerin']} (Geographie)"
            if r['geschichtslehrerin']:
                remark += f" {r['geschichtslehrerin']} (Geschichte)"
            if r['techniklehrerin']:
                remark += f" {r['techniklehrerin']} (Technik)"
            yield Course(group=grp, subject=science_subject, remark=remark)

        if False:
            for t in find_teachers(r['klassenleiterinnen']):
                for s in main_subjects:
                    yield Cast(user=t, group=grp, subject=s, role=loader.klassenleiter)
            if religion_subject is not None:
                for t in find_teachers(r['ev_religionslehrerin']):
                    yield Cast(user=t, group=grp, subject=religion_subject,
                               role=loader.ev_religionslehrerin)
                for t in find_teachers(r['ka_religionslehrerin']):
                    yield Cast(user=t, group=grp, subject=religion_subject,
                               role=loader.ka_religionslehrerin)
            if sport_subject is not None:
                for t in find_teachers(r['sportlehrerin']):
                    yield Cast(user=t, group=grp, subject=sport_subject)
            if science_subject is not None:
                for t in find_teachers(r['geographielehrerin']):
                    yield Cast(user=t, group=grp, subject=science_subject,
                               role=loader.geographielehrerin)
                for t in find_teachers(r['geschichtslehrerin']):
                    yield Cast(user=t, group=grp, subject=science_subject,
                               role=loader.geschichtslehrerin)
                for t in find_teachers(r['techniklehrerin']):
                    yield Cast(user=t, group=grp, subject=science_subject,
                               role=loader.techniklehrerin)

    print(f"20241022 {periode1.year.ref} max group id was {loader.max_group_id}")

    # Seems that this model isn't used anywhere
    # for r in csv2dicts("LehrerRolle.csv"):
    #     # id,lehrer,klasse,fach
    #     kwargs = dict(
    #         # id=r['id'],
    #         user_id=r['lehrer'],
    #         group_id=klasse2group(r['klasse']),
    #         subject_id=r['fach']
    #     )
    #     yield Cast(**kwargs)

    for r in csv2dicts("Schüler.csv"):
        # id,name,vorname,klasse
        yield update_or_create(User,
                               id=uid(r['id']),
                               username="Schüler#" + r['id'],
                               last_name=r['name'],
                               first_name=r['vorname'],
                               # nickname=r['vorname'],
                               )
        pupil_id = uid(r['id'])
        obj = Enrolment(
            # id=r['id'],
            pupil_id=pupil_id,
            group_id=klasse2group(r['klasse'])
        )
        yield obj
        # if pupil_id == 426:
        #     print(f"20241020 created enrolment for {pupil_id} in {obj.group.year}")

    for r in csv2dicts("VersetzungsBedingung.csv"):
        # id,text,jahr
        grade = Grade.objects.get(ref=r['jahr'])
        grade.rating_conditions = r['text']
        yield grade

    for r in csv2dicts("AbschlussTest.csv"):
        # id,name,kompetenz,max_punkte
        kwargs = dict(
            id=r['id'],
            designation=r['name'],
            skill_id=r['kompetenz'],
            max_score=r['max_punkte'])
        yield update_or_create(FinalExam, **kwargs)

    for r in csv2dicts("AbschlussTestBewertung.csv"):
        # id,polymorphic_ctype,datum,periode,lehrer,schüler,bewertung_ptr,test,punkte
        p = p2p(r['periode'])
        # if p != periode1:
        #     print(f"20241107 {p} is not {periode1} in AbschlussTestBewertung {r}")
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']),
                group__year=p.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! Enrolment does not exist: {r}")
            # print(f"Oops! Enrolment does not exist: {r}")
            continue

        exam = FinalExam.objects.get(id=r['test'])
        teacher = User.objects.get(id=r['lehrer'])
        kwargs = dict(
            id=r['id'],
            enrolment=enr,
            date_done=datedone(r['datum']),
            teacher=teacher,
            exam=exam,
            period=p,
            score=r['punkte'])
        yield update_or_create(rt.models.ratings.FinalExamRating, **kwargs)
        yield loader.make_cast_if_needed(exam.skill.subject, teacher, enr.group, loader.klassenleiter)

    for r in csv2dicts("Test.csv"):
        # id,name,leistungsblock_ptr,klasse,periode,fach
        kwargs = dict(
                group_id=klasse2group(r['klasse']),
                # user=unknown_teacher,
                subject_id=r['fach'])
        # qs = Cast.objects.filter(**kwargs)
        # if qs.count() == 0:
        #     cast = Cast(user=unknown_teacher, **kwargs)
        #     yield cast
        # elif qs.count() == 1:
        #     cast = qs.first()
        # else:
        #     cast = qs.first()
        #     # no way to know which teacher did this test, so we take the first
        #     # raise Exception(f"Multiple casts for {kwargs}!")
        kwargs.update(
            id=examid(r['id']), heading=r['name'],
            period=p2p(r['periode']),
            # cast=cast
        )
        yield rt.models.ratings.Exam(**kwargs)
    print(f"20241022 {periode1.year.ref} max exam id was {loader.max_exam_id}")

    dup_block = []
    no_block = []
    mult_block = []
    for r in csv2dicts("Leistung.csv"):
        # id,block,kompetenz,max_punkte,ord_inner
        # block points to either an Exam or a ProjectSection
        kwargs = dict(
            id=r['id'],
            # exam_type='test',
            skill_id=r['kompetenz'],
            seqno=int(r['ord_inner']) + 1,
            # seqno=f"{r['block']}{int(r['ord_inner']):03d}",
            max_score=r['max_punkte']
        )
        block = examid(r['block'])
        if rt.models.ratings.Exam.objects.filter(id=block).exists():
            kwargs.update(exam_id=block)
            yield update_or_create(Challenge, **kwargs)
            # if rt.models.ratings.ProjectSection.objects.filter(pk=block).exists():
            #     dup_block.append(r['id'])
            #     raise Exception(f"Found both a Exam and a ProjectSection for {r}")
            # else:
            #     kwargs.update(exam_id=block)
            #     yield Challenge(**kwargs)
        else:
            block = int(r['block'])
            qs = ProjectSection.objects.filter(pk=block)
            n = qs.count()
            if n == 1:
                # print(f"Ignore {r}")
                kwargs.update(project_section=qs.first())
                yield update_or_create(Challenge, **kwargs)
            elif n == 0:
                no_block.append(r['id'])
            else:
                raise Exception(f"20241022 multiple project sections for {r}")
                mult_block.append(r['id'])
            # prjskills = rt.models.ratings.ProjectSkill.objects.all()
            # kwargs.update(project_section_id=block)
            # for i in prjskills:
            #     kwargs.update(project_skill=i)
            #     yield rt.models.ratings.Challenge(**kwargs)
    # print(f"{len(dup_block)} challenges having both an Exam and a ProjectSection: {dup_block}")
    print(f"Ignored {len(no_block)} challenges having neither Exam nor ProjectSection")
    # print(f"{len(mult_block)} challenges having multiple ProjectSection: {mult_block}")

    # No need to import LeistungsBlock.csv because that data is in Test.csv and
    # BlockAbschnitt.csv:
    # for r in csv2dicts("BlockAbschnitt.csv"):

    for r in csv2dicts("LeistungsBewertung.csv"):
        # id,polymorphic_ctype,datum,periode,lehrer,schüler,bewertung_ptr,leistung,punkte
        p = p2p(r['periode'])
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']),
                group__year=p.year)
        except Enrolment.DoesNotExist:
            raise
            # print(f"Oops! Enrolment does not exist: {r}")
            # continue
        challenge = Challenge.objects.get(id=r['leistung'])
        teacher = User.objects.get(id=r['lehrer'])
        kwargs = dict(
            id=r['id'],
            enrolment=enr,
            date_done=datedone(r['datum']),
            teacher=teacher,
            challenge=challenge,
            period=p,
            score=r['punkte'])
        yield update_or_create(rt.models.ratings.ChallengeRating, **kwargs)
        if challenge.exam_id is None:
            trole = loader.bausteine
        else:
            trole = loader.klassenleiter
            if challenge.exam.user_id is None:
                challenge.exam.user = teacher
                challenge.exam.full_clean()
                challenge.exam.save()
        yield loader.make_cast_if_needed(challenge.skill.subject, teacher, enr.group, trole)

    for r in csv2dicts("BausteinArbeitBewertung.csv"):
        # id,polymorphic_ctype,datum,periode,lehrer,schüler,bewertung_ptr,arbeit,baustein,punkte
        p = p2p(r['periode'])
        pupil_id = uid(r['schüler'])
        try:
            enr = Enrolment.objects.get(
                pupil_id=pupil_id,
                group__year=p.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No enrolment for {pupil_id} in {p.year}") from None
            continue
        prj, created = Project.objects.get_or_create(
            enrolment=enr, template_id=r['baustein'])

        gr = GeneralRatings.get_by_value(r['arbeit'])
        setattr(prj, gr.field_name, r['punkte'])
        yield prj

    for r in csv2dicts("BausteinKommentar.csv"):
        if not r['kommentar'].strip():
            continue
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']), group__year=periode1.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No enrolment for BausteinKommentar {r}")
            continue
        prj, created = Project.objects.get_or_create(
            enrolment=enr, template_id=r['baustein'])
        prj.remark = r['kommentar']
        yield prj

    for r in csv2dicts("Zeugnis.csv"):
        # id,schüler,periode,status,katholische_religion,sozialverhalten_kommentar,versetzungsentscheidung,abwesenheiten_mit_entschuldigung,abwesenheiten_mit_attest,abwesenheiten_ohne,förderziele
        p = p2p(r['periode'])
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']), group__year=periode1.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No enrolment for Zeugnis {r}")
            continue
        kwargs = dict(
            id=r['id'],
            enrolment=enr,
            period=p,
            social_skills_comment=r['sozialverhalten_kommentar'],
            final_verdict=r['versetzungsentscheidung'],
            absences_p=r['abwesenheiten_mit_entschuldigung'],
            absences_m=r['abwesenheiten_mit_attest'],
            absences_u=r['abwesenheiten_ohne'],
        )
        yield Certificate(**kwargs)

    for r in csv2dicts("TestKommentar.csv"):
        # id,schüler,test,kommentar
        try:
            enr = Enrolment.objects.get(
                pupil_id=uid(r['schüler']), group__year=periode1.year)
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No enrolment for Zeugnis {r}")
            continue
        kwargs = dict(
            id=r['id'],
            enrolment=enr,
            exam_id=examid(r['test']),
            remark=r['kommentar'],
        )
        yield rt.models.ratings.ExamResponse(**kwargs)

    max_response_id = 0
    for r in csv2dicts("ZeugnisFachKommentar.csv"):
        # id,schüler,periode,abschnitt,kommentar
        cert = get_certificate(r)
        # p = p2p(r['periode'])
        # try:
        #     enr = Enrolment.objects.get(
        #         pupil_id=uid(r['schüler']), group__year=periode1.year)
        # except Enrolment.DoesNotExist:
        #     raise Exception(f"Oops! No enrolment for Zeugnis {r}")
        try:
            cs = CertSection.objects.get(id=r['abschnitt'])
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No enrolment for Zeugnis {r}")
        kwargs = dict(
            # id=sectionresponse_id(r['id']),
            certificate=cert,
            section=cs,
            # enrolment=enr,
            # period=p,
            # subject=cs.subject,
            remark=r['kommentar'],
        )
        response = SectionResponse(**kwargs)
        yield response
        max_response_id = max(response.id, max_response_id)

    print(f"20241128 {periode1.year.ref} max SectionResponse id was {max_response_id}")

    for r in csv2dicts("ZeugnisPrädikatNote.csv"):
        # id,schüler,periode,abschnitt,note
        cert = get_certificate(r)
        try:
            cs = CertSection.objects.get(id=r['abschnitt'])
        except Enrolment.DoesNotExist:
            raise Exception(f"Oops! No CertSection for {r}")
        resp, created = SectionResponse.objects.get_or_create(
            certificate=cert, section=cs)
        resp.score = r['note']
        yield resp
        # kwargs = dict(
        #     id=r['id'],  # the id isn't used anywhere, so we can safely let Lino assign new id's
        #     response=resp,
        #     score=r['note'],
        # )
        # yield SectionResponse(**kwargs)

    for r in csv2dicts("ZeugnisKompetenzNote.csv"):
        # id,schüler,periode,element,note
        cert = get_certificate(r)
        elem = CertElement.objects.get(id=r['element'])
        resp, created = SectionResponse.objects.get_or_create(
            certificate=cert, section=elem.cert_section)
        kwargs = dict(
            # id=r['id'],  # the id isn't used anywhere, so we can safely let Lino assign new id's
            section_response=resp,
            cert_element=elem,
            # certificate=cert,
            # enrolment=enr,
            # period=p,
            score=r['note'],
        )
        yield ElementResponse(**kwargs)

    # ignored = []
    for r in csv2dicts("ZeugnisSozialNote.csv"):
        # id,schüler,periode,sozialkompetenz,note
        cert = get_certificate(r)
        tpl = cert.enrolment.group.grade.cert_template
        try:
            skill = Skill.objects.get(pk=sk2skill(r['sozialkompetenz']))
        except Skill.DoesNotExist:
            raise Exception(f"Oops! Skill does not exist: {r}")
        cs, created = CertSection.objects.get_or_create(
            cert_template=tpl, subject=skill.subject)
        resp = get_or_create(SectionResponse, certificate=cert, section=cs)
        elem = get_or_create(CertElement, skill=skill, cert_section=cs)
        kwargs = dict(
            # id=r['id'],  # the id isn't used anywhere, so we can safely let Lino assign new id's
            # certificate=cert,
            section_response=resp,
            cert_element=elem,
            score=r['note'],
        )
        yield ElementResponse(**kwargs)

    # if len(ignored) > 0:
    #     print(f"Ignored {len(ignored)} ratings because CertElement does not exist.")


def objects():

    if False:
        settings.SITE.site_config.update(simulate_today=i2d(20240601))

    loader = Loader()
    yield loader.common_objects()
    # yield csv2db("~/work/zeugnisse/export", 2023)
    yield csv2db(loader, "~/Downloads/export/2023", 2023, True)
    yield csv2db(loader, "~/Downloads/export/2024", 2024, False)

    # print("compute_project_sums()")
    # rt.models.ratings.compute_project_sums()
