# -*- coding: UTF-8 -*-
# Copyright 2024-2025 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import locale
from decimal import Decimal
from django.utils.html import format_html, mark_safe, escape
from lino.api import dd, rt, _

ZERO = Decimal()
# NOT_RATED = '▨'
# NOT_RATED = '◻' # 25fb white medium square
# NOT_RATED = '□' # 25a1 white square
# NOT_RATED = '▭' # 25ad white rectagle
NOT_RATED = '☐' # 2610 ballot box


def format_score(n):
    if n is None:
        return ""
    if n % 1:
        return locale.str(round(n, 1))
    return str(int(round(n, 0)))
    # return str(round(n, 0))

def format_percentage(done, todo, width=10):
    if not todo:
        return _("No data")
    if done:
        v = int((done / todo) * width) + 1
    else:
        v = 0
    # return "▪" * v + "▫" * (width - v) + " (" + format_score(100 * done / todo) + "%)"
    # return "■" * v + "▤" * (width - v) + " (" + format_score(100 * done / todo) + "%)"
    # return "▬" * v + "▭" * (width - v) + " (" + format_score(100 * done / todo) + "%)"
    return "▮" * v + "▯" * (width - v) + " (" + format_score(100 * done / todo) + "%)"

# from fractions import Fraction

class ScoreValue:

    def __init__(self, score=ZERO, max_score=ZERO, **kwargs):
        self._score = score
        self._max_score = max_score
        # if score > max_score:
        #     raise ValueError("Score greater than max_score")
        for k, v in kwargs.items():
            setattr(self, k, v)

    def rebase(self, max_score):
        if not self._max_score:
            return self
        return self.__class__(self._score * max_score / self._max_score, max_score)

    def __add__(self, other):
        return self.__class__(
            (self._score or ZERO) + (other._score or ZERO),
            (self._max_score or ZERO) + (other._max_score or ZERO))

    def __mul__(self, other):
        return self.__class__(
            (self._score or ZERO) * other,
            (self._max_score or ZERO) * other)

    def __truediv__(self, other):
        return self.__class__(
            (self._score or ZERO) / other,
            (self._max_score or ZERO) / other)

    def __repr__(self):
        return "<ScoreValue({}, {})>".format(self._score, self._max_score)

    def __str__(self):
        return self.absolute

    def __format__(self, fmt):
        if fmt == "%":
            return self.relative
        return self.absolute

    @property
    def absolute(self):
        return format_html("{}/{}", self.score, self.max_score)

    @property
    def relative(self):
        if self._score is not None and self._max_score:
            return format_score(100 * self._score / self._max_score) + " %"
        return mark_safe("&mdash;")

    @property
    def score(self):
        if self._score is None:
            return NOT_RATED
        if self._max_score:
            return format_score(self._score)
        return mark_safe("&mdash;")

    @property
    def max_score(self):
        if self._max_score:
            return format_score(self._max_score)
        return mark_safe("&mdash;")



class RatingCollector:
    def __init__(self, value=None, done=0, todo=0):
        if value is None:
            value = ScoreValue()
        self.value = value
        self.done = done
        self.todo = todo
        self.ratings = []

    def __str__(self):
        return str(self.value)

    @property
    def score(self):
        return self.value.score

    @property
    def max_score(self):
        return self.value.max_score

    def __add__(self, other):
        return self.__class__(
            self.value+other.value,
            self.done+other.done,
            self.todo+other.todo)

    def collect(self, score, max_score, **kwargs):
        v = ScoreValue(score, max_score, **kwargs)
        self.todo += 1
        self.ratings.append(v)
        if score is None:
            return
        self.value += v
        self.done += 1

    @property
    def percent_done(self):
        if self.todo == 0:
            return _("N/A")
        return format_score(round(100 * self.done / self.todo, 0)) + "%"
