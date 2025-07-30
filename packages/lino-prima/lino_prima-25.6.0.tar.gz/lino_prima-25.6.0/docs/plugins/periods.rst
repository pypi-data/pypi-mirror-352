.. _prima.plugins.periods:
.. doctest docs/plugins/periods.rst

======================================
``periods`` in Lino Prima
======================================


.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *

The prima1 project uses a demo date in **October 2024** for all its data, which
means that there is only one :term:`accounting period`: everything happens
during the **first semester** of academic year 2024/25, and this semester lasts
from **September 2024** to **February 2025**.

>>> dd.plugins.periods.year_name
'Academic year'
>>> dd.plugins.periods.period_name
'Period'

>>> print(dd.today())
2025-02-06

>>> print(dd.fdf(dd.today()))
Thursday, 6 February 2025

>>> rt.show(periods.StoredPeriods)
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
=========== ============ ============ =============== ======== ========
 Reference   Start date   End date     Academic year   State    Remark
----------- ------------ ------------ --------------- -------- --------
 2023/24-1   01/08/2023   31/01/2024   2023/24         Closed
 2023/24-2   01/02/2024   31/07/2024   2023/24         Closed
 2024/25-1   01/08/2024   31/01/2025   2024/25         Open
 2024/25-2   01/02/2025   31/07/2025   2024/25         Open
=========== ============ ============ =============== ======== ========
<BLANKLINE>


>>> rt.show(periods.StoredYears)  #doctest: +REPORT_UDIFF
=========== ============ ============ ========
 Reference   Start date   End date     State
----------- ------------ ------------ --------
 2023/24     01/08/2023   31/07/2024   Closed
 2024/25     01/08/2024   31/07/2025   Open
 2025/26     01/08/2025   31/07/2026   Open
 2026/27     01/08/2026   31/07/2027   Open
 2027/28     01/08/2027   31/07/2028   Open
 2028/29     01/08/2028   31/07/2029   Open
 2029/30     01/08/2029   31/07/2030   Open
=========== ============ ============ ========
<BLANKLINE>
