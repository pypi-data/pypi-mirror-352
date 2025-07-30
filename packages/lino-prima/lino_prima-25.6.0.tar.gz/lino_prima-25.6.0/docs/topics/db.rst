.. doctest docs/topics/db.rst
.. _prima.topics.db:

================================
Database structure of Lino Prima
================================

This document describes the database structure.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *


>>> school.Groups.simple_parameters
('year',)


>>> from lino.utils.diag import analyzer
>>> analyzer.show_db_overview()
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
26 plugins: lino, bulma, printing, system, users, prima, periods, school, ratings, projects, cert, uploads, contenttypes, gfks, office, linod, checkdata, summaries, jinja, weasyprint, export_excel, help, about, react, staticfiles, sessions.
36 models:
========================== =========================== ========= =======
 Name                       Default table               #fields   #rows
-------------------------- --------------------------- --------- -------
 cert.CertElement           cert.CertElements           5         52
 cert.CertSection           cert.CertSections           8         16
 cert.CertTemplate          cert.CertTemplates          3         2
 cert.Certificate           cert.Certificates           11        576
 cert.ElementResponse       cert.ElementResponses       6         7488
 cert.SectionResponse       cert.SectionResponses       10        2304
 checkdata.Message          checkdata.Messages          6         0
 contenttypes.ContentType   gfks.ContentTypes           3         36
 linod.SystemTask           linod.SystemTasks           25        2
 periods.StoredPeriod       periods.StoredPeriods       7         4
 periods.StoredYear         periods.StoredYears         5         7
 projects.Project           projects.Projects           14        0
 projects.ProjectSection    projects.ProjectSections    5         4
 projects.ProjectTemplate   projects.ProjectTemplates   7         5
 ratings.Challenge          ratings.Challenges          6         60
 ratings.ChallengeRating    ratings.ChallengeRatings    9         1620
 ratings.Exam               ratings.Exams               8         30
 ratings.ExamResponse       ratings.ExamResponses       4         180
 ratings.FinalExam          ratings.FinalExams          4         0
 ratings.FinalExamRating    ratings.FinalExamRatings    9         0
 ratings.RatingsSummary     ratings.RatingsSummaries    7         0
 school.Cast                school.Casts                4         72
 school.Course              school.Courses              5         156
 school.Enrolment           school.Enrolments           3         288
 school.Grade               school.Grades               7         7
 school.Group               school.Groups               7         24
 school.Role                school.Roles                3         6
 school.Skill               school.Skills               6         26
 school.Subject             school.Subjects             8         8
 sessions.Session           users.Sessions              3         ...
 system.SiteConfig          system.SiteConfigs          3         1
 uploads.Upload             uploads.Uploads             12        7
 uploads.UploadType         uploads.UploadTypes         7         0
 uploads.Volume             uploads.Volumes             4         2
 users.Authority            users.Authorities           3         0
 users.User                 users.AllUsers              20        168
========================== =========================== ========= =======
<BLANKLINE>
