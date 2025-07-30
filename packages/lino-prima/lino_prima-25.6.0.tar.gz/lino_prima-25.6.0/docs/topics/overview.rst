.. doctest docs/topics/overview.rst
.. _prima.topics.overview:

========
Overview
========

This document should give an overview over Lino Prima.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *


>>> print(analyzer.show_complexity_factors())
... #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- 26 plugins
- 36 models
- 6 user types
- 122 views
- 12 dialog actions
<BLANKLINE>
