.. doctest docs/plugins/cert.rst
.. _prima.plugins.cert:

======================================
``cert`` (Certificates)
======================================

.. currentmodule:: lino_prima.plugins.cert

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *

Plain-text representation
=========================

The plain-text representation methods of the :class:`Certificate` model are
defined as follows::

    def __str__(self):
        return f"{self.enrolment.pupil} {self.period.nickname}"

    def get_str_words(self, ar):
        if not ar.is_obvious_field("enrolment"):
            yield str(self.enrolment)
        if not ar.is_obvious_field("period"):
            yield str(self.period)

The following snippets test whether they work as expected.

>>> # obj = cert.Certificate.objects.get(id=73, enrolment__group__ref="5A")
>>> qs = cert.Certificate.objects.filter(enrolment__group__designation="5A")

>>> current_year = periods.StoredYear.get_or_create_from_date(dd.today())
>>> obj = qs.exclude(enrolment__group__year=current_year).first()
>>> print(obj)
Léopold Brouck 2023/24-1


>>> obj = qs.filter(enrolment__group__year=current_year).first()
>>> print(obj.enrolment)
Guillaume Borsu (5A)
>>> print(obj)
Guillaume Borsu 1


>>> print(repr(obj))
Certificate #147 ('Guillaume Borsu 1')


>>> res = AttrDict(get_json_dict("robin", f"cert/Certificates/{obj.pk}"))
>>> print(res['title'])  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a ...>Certificates</a> » Guillaume Borsu (5A) 1

When the certificate is an :term:`obvious field`, Lino does not show it:

>>> mt = contenttypes.ContentType.objects.get_for_model(school.Enrolment).id
>>> res = get_json_dict("robin", f"cert/CertificatesByEnrolment/{obj.pk}", mk=obj.enrolment.id, mt=mt)
>>> print(res['title'])  #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
<a ...>Certificates of Guillaume Borsu (5A)</a> » 1


The :attr:`Certificate.enrolment` field in the detail view

>>> print(res['data']['enrolment'])
Guillaume Borsu in 5A



API reference
===============

.. class:: Certificate

  .. attribute:: enrolment

    The pupil for whom this certificate has been issued.

    Note that this labelled "Pupil" but actually points to an :term:`enrolment`,
    not to a pupil.

  .. attribute:: absences_m

    The number of absences for medical reasons.

  .. attribute:: absences_p

    The number of excused absences with parental proof.

  .. attribute:: absences_u

    The number of unexcused absences.
