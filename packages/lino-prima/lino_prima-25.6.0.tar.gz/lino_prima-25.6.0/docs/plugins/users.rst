.. doctest docs/plugins/users.rst
.. _prima.plugins.users:

==================================
``users`` in Lino Prima
==================================

The :mod:`lino_prima.lib.users` plugin extends :mod:`lino.modlib.users`.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *


Available user types
====================

Lino Prima knows the following :term:`user types <user type>`:

>>> rt.show(rt.models.users.UserTypes, language="en")
======= =========== ===============
 value   name        text
------- ----------- ---------------
 000     anonymous   Anonymous
 100     user        User
 200     teacher     Teacher
 300     pupil       Pupil
 500     staff       Staff
 900     admin       Administrator
======= =========== ===============
<BLANKLINE>

A :term:`demo site` has the following users:

>>> rt.show(rt.models.users.UsersOverview, language="en")
... #doctest: +NORMALIZE_WHITESPACE +REPORT_UDIFF
====================== ===================== ==========
 Username               User type             Language
---------------------- --------------------- ----------
 abel.adam              200 (Teacher)         en
 achille.adriaen        200 (Teacher)         en
 adèle.adami            200 (Teacher)         en
 adélaïde.adriaensen    200 (Teacher)         en
 aglaé.adriaenssens     200 (Teacher)         en
 agnès.adriensence      200 (Teacher)         en
 aimé.adriaenssen       200 (Teacher)         en
 aimée.aelter           200 (Teacher)         en
 albanie.aelters        200 (Teacher)         en
 alexine.aerts          200 (Teacher)         en
 alfred.adriencense     200 (Teacher)         en
 alice.albumazard       200 (Teacher)         en
 alina.alsteen          200 (Teacher)         en
 alix.andries           200 (Teacher)         en
 alma.andré             200 (Teacher)         en
 alphonse.adrienssens   200 (Teacher)         en
 ambroise.aelterman     200 (Teacher)         en
 amédée.aerens          200 (Teacher)         en
 anastase.aertsens      200 (Teacher)         en
 anatole.alloo          200 (Teacher)         en
 anthime.andersson      200 (Teacher)         en
 aristide.andriessen    200 (Teacher)         en
 robin                  900 (Administrator)   en
 rolf                   900 (Administrator)   de
====================== ===================== ==========
<BLANKLINE>


The site manager
================

Robin is a :term:`site manager`, he has a complete menu.

>>> show_menu('robin')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- School : My groups
- Office : My Upload files
- Configure :
  - System : Site configuration, Users, System tasks
  - School : Groups, Subjects, Roles, Grades, Academic years, Periods
  - Ratings : Final exams
  - Projects : Project templates
  - Certificates : Certificate templates
  - Office : Library volumes, Upload types
- Explorer :
  - System : Authorities, User types, User roles, Data checkers, Data problem messages, content types, Background procedures
  - School : Skills, Enrolments, Casts, Courses
  - Ratings : Exams, Challenges, Challenge ratings, Final exam ratings, Rating summaries
  - Projects : Project sections, General ratings
  - Certificates : Certificate section templates, Certificate element templates, Certificates, Certificate sections, Certificate elements
  - Office : Upload files, Upload areas
- Site : User sessions, About

Our pilot customer uses Lino Prima mainly in German:

>>> show_menu('rolf')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- Schule : Meine Klassen
- Büro : Meine Upload-Dateien
- Konfigurierung :
  - System : Site-Konfiguration, Benutzer, Systemaufgaben
  - Schule : Klassen, Fächer, Rollen, Jahrgänge, Schuljahre, Perioden
  - Bewertungen : Abschlusstests
  - Bausteine : Bausteinvorlagen
  - Zeugnisse : Zeugnisvorlagen
  - Büro : Dateibibliotheken, Upload-Arten
- Explorer :
  - System : Vollmachten, Benutzerarten, Benutzerrollen, Datentests, Datenproblemmeldungen, Datenbankmodelle, Background procedures
  - Schule : Kompetenzen, Einschreibungen, Lehrerrollen, Kurse
  - Bewertungen : Tests, Leistungen, Leistungsbewertungen, Abschlusstestbewertungen, Bewertungsübersichten
  - Bausteine : Bausteinabschnitte, Allgemeinbewertungen
  - Zeugnisse : Zeugnisabschnittvorlagen, Zeugniselementvorlagen, Zeugnisse, Zeugnisabschnitte, Zeugniselemente
  - Büro : Upload-Dateien, Upload-Bereiche
- Site : Benutzersitzungen, Info

Normal teachers have a reduced menu:

>>> rt.login('abel.adam').get_user().user_type
<users.UserTypes.teacher:200>

>>> show_menu('abel.adam')
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- School : My groups
- Site : About
