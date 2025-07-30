.. _prima.plugins.school:

======================================
``school`` (School management)
======================================

.. module:: lino_prima.lib.school


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *

Glossary
========

.. glossary::

  enrolment

    When a given pupil is member of a given group in a given school year.


Class reference
===============

.. class:: Group

  Django model to represent a group of pupils working together during an
  academic year (a class).

.. class:: Enrolment

  Django model to represent an enrolment of a given pupil in a given group.

Subjects, groups and courses
============================

>>> rt.show(school.Grades)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== ============== ================== =========== ====================== =================== ========================
 ID   Designation    Designation (de)   Reference   Certificate template   Rating conditions   Rating conditions (de)
---- -------------- ------------------ ----------- ---------------------- ------------------- ------------------------
 1    First grade    First grade        1           Junior
 2    Second grade   Second grade       2           Junior
 3    Third grade    Third grade        3           Senior
 4    Fourth grade   Fourth grade       4           Senior
 5    Fifth grade    Fifth grade        5           Senior
 6    Sixth grade    Sixth grade        6           Senior
 7    Alumni         Alumni             X
==== ============== ================== =========== ====================== =================== ========================
<BLANKLINE>

The :meth:`lino.mixins.ref.Referrable.get_next_row` method returns the "next"
row:

>>> for obj in school.Grade.objects.all():
...     print(f"{obj} --> {obj.get_next_row()}")
First grade --> Second grade
Second grade --> Third grade
Third grade --> Fourth grade
Fourth grade --> Fifth grade
Fifth grade --> Sixth grade
Sixth grade --> None
Alumni --> None


The :class:`lino.modlib.periods.StoredYear` model has an overridden
:meth:`lino.mixins.ref.Referrable.get_next_row` method:

>>> for obj in periods.StoredYear.objects.all():
...     print(f"{obj} --> {obj.get_next_row()}")
2023/24 --> 2024/25
2024/25 --> 2025/26
2025/26 --> 2026/27
2026/27 --> 2027/28
2027/28 --> 2028/29
2028/29 --> 2029/30
2029/30 --> None



>>> rt.show(school.Subjects)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
==== ============= ================== ===== ========== ====== ============= ==================
 ID   Designation   Designation (de)   No.   Advanced   Icon   Rating type   Image
---- ------------- ------------------ ----- ---------- ------ ------------- ------------------
 1    Science       Wissenschaften     1     Yes        🔬
 2    Art           Kunst              2     No         🎨     Smilies
 3    Music         Musik              3     No         🎜      Predicates
 4    Sport         Sport              4     No         ⛹      Predicates    26bd_soccer.png
 5    French        Französisch        5     Yes        🥐                   1f347_grapes.png
 6    Religion      Religion           6     Yes        🕊
 7    Mathematics   Mathematik         7     Yes        🖩
 8    German        Deutsch            8     Yes        🥨                   1f34e_apple.png
==== ============= ================== ===== ========== ====== ============= ==================
<BLANKLINE>


The :class:`MyGroups` table shows only groups of the currently opened school
year while :class:`Groups` shows them all:

>>> rt.show(school.MyGroups, display_mode="grid")
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============= ================== ============== =============== ====
 Designation   Designation (de)   Grade          Academic year   ID
------------- ------------------ -------------- --------------- ----
 2A                               Second grade   2024/25         13
 2B                               Second grade   2024/25         14
 3A                               Third grade    2024/25         15
 3B                               Third grade    2024/25         16
 4A                               Fourth grade   2024/25         17
 4B                               Fourth grade   2024/25         18
 5A                               Fifth grade    2024/25         19
 5B                               Fifth grade    2024/25         20
 6A                               Sixth grade    2024/25         21
 6B                               Sixth grade    2024/25         22
 7A                               Sixth grade    2024/25         23
 7B                               Sixth grade    2024/25         24
============= ================== ============== =============== ====
<BLANKLINE>

>>> rt.show(school.Groups)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
============= ================== ============== =============== ====
 Designation   Designation (de)   Grade          Academic year   ID
------------- ------------------ -------------- --------------- ----
 1A                               First grade    2023/24         1
 1B                               First grade    2023/24         7
 2A                               Second grade   2023/24         2
 2A                               Second grade   2024/25         13
 2B                               Second grade   2023/24         8
 2B                               Second grade   2024/25         14
 3A                               Third grade    2023/24         3
 3A                               Third grade    2024/25         15
 3B                               Third grade    2023/24         9
 3B                               Third grade    2024/25         16
 4A                               Fourth grade   2023/24         4
 4A                               Fourth grade   2024/25         17
 4B                               Fourth grade   2023/24         10
 4B                               Fourth grade   2024/25         18
 5A                               Fifth grade    2023/24         5
 5A                               Fifth grade    2024/25         19
 5B                               Fifth grade    2023/24         11
 5B                               Fifth grade    2024/25         20
 6A                               Sixth grade    2023/24         6
 6A                               Sixth grade    2024/25         21
 6B                               Sixth grade    2023/24         12
 6B                               Sixth grade    2024/25         22
 7A                               Sixth grade    2024/25         23
 7B                               Sixth grade    2024/25         24
============= ================== ============== =============== ====
<BLANKLINE>


Lino automatically creates a course for every subject that has "advanced"
checked and for which there is a section in the certificate template.

>>> grp = school.Group.objects.filter(designation="5B").last()
>>> rt.show(school.CoursesByGroup, grp)
`Science <…>`__, `Art <…>`__, `Music <…>`__, `Sport <…>`__, `French <…>`__, `Religion <…>`__, `Mathematics <…>`__, `German <…>`__

>>> grp = school.Group.objects.filter(designation="6A").last()
>>> rt.show(school.CoursesByGroup, grp)
`Science <…>`__, `French <…>`__, `Religion <…>`__, `Mathematics <…>`__, `German <…>`__


Working with scores
===================

>>> settings.SITE.site_locale
'de_BE.UTF-8'

>>> from lino_prima.lib.ratings.utils import ScoreValue, RatingCollector, format_score

>>> v1 = ScoreValue(8, 10)
>>> print(v1)
8/10
>>> print(v1.absolute)
8/10
>>> print(v1.relative)
80 %

>>> print(v1.rebase(20))
16/20

>>> v2 = ScoreValue(5, 20)
>>> print(f"{v1} + {v2} = {v1+v2}")
8/10 + 5/20 = 13/30

>>> tot = v1 + v2
>>> print(tot.relative)
43,3 %
>>> round(100*13/30, 1)
43.3
>>> import locale
>>> locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
'en_US.UTF-8'
>>> print(tot.relative)
43.3 %
>>> print(tot)
13/30

>>> print(ScoreValue(5.29, 8))
5.3/8

>>> v3 = ScoreValue(5.24, 8)
>>> print(v3)
5.2/8

>>> print(v3*3)
15.7/24


>>> tot = RatingCollector()
>>> tot.collect(8, 10)
>>> tot.collect(5, 20)
>>> print(tot)
13/30

>>> tot.ratings
[<ScoreValue(8, 10)>, <ScoreValue(5, 20)>]

>>> " + ".join(map(str, tot.ratings))
'8/10 + 5/20'


Don't read this
===============

Exploring #5835 (Link to detail of an enrolment fails for normal teachers)

This issue was fixed 20250107. Here is how to reproduce it:

- Sign in as madeleine.carbonez on ``prima1``.
- Click on "6A" in the "My groups" dashboard item.
- In the "Projects" panel of 6A, click on the first pupil (Philémon Burton).
  Lino opens prima/EnrolmentsByGroup/61, which causes a BadRequest.
- There is no error when you do the same as robin.

Explanation:

When madeleine (a simple teacher) calls :meth:`obj2html` on an enrolment, Lino
uses another actor than when robin calls it because a simple teacher cannot see
all enrolments. That's normal.  Robin has access to Enrolments, Madeleine only
to EnrolmentsByGroup. But Madeleine's link then failed because EnrolmentsByGroup
requires a master instance (the group), which Lino didn't specify. Until
20250107 Lino added `mk` and `mt` for specifying the master instance only when
the target link was on the same actor as the incoming request.


>>> renderer = settings.SITE.kernel.default_renderer
>>> grp = school.Group.objects.get(designation="6A", year__ref="2023/24")
>>> enr = school.Enrolment.objects.filter(group=grp).first()
>>> grp
Group #6 ('6A (2023/24)')
>>> enr
Enrolment #61 ('Philémon Burton (6A (2023/24))')
>>> ses = rt.login("robin", show_urls=True, renderer=settings.SITE.kernel.default_renderer)
>>> print(ses.permalink_uris)
None
>>> print(ses.obj2htmls(enr).replace("&quot;", "'"))
<a href="javascript:window.App.runAction({ 'actorId': 'school.Enrolments', 'an': 'detail', 'rp': null, 'status': { 'record_id': 61 } })" style="text-decoration:none">Philémon Burton (6A (2023/24))</a>

>>> ses = rt.login("abel.adam", show_urls=True, renderer=settings.SITE.kernel.default_renderer)
>>> ar = projects.PupilsAndProjectsByGroup.create_request(master_instance=grp, renderer=renderer, user=ses.get_user())
>>> print(ar.obj2url(enr))  #doctest: +NORMALIZE_WHITESPACE
javascript:window.App.runAction({ "actorId":
"projects.PupilsAndProjectsByGroup", "an": "detail", "rp": null, "status": {
"base_params": { "mk": 6, "mt": 9 }, "record_id": 61 } })

Note: After fixing the bug, I changed PupilsAndProjectsByGroup to inherit from
EnrolmentsByGroup rather than VirtualTable.
