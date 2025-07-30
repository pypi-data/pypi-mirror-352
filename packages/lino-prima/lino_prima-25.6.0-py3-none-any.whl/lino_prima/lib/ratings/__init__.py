# -*- coding: UTF-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.ad import Plugin, _


class Plugin(Plugin):

    verbose_name = _("Ratings")
    # menu_group = "ratings"
    max_skills_per_exam = 3

    def get_score_column_names(self):
        # names of the dynamic columns in ResponsesByExam
        for i in range(1, self.max_skills_per_exam + 1):
            yield "score" + str(i)

    def setup_config_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        # m.add_action('ratings.ProjectSkills')
        m.add_action('ratings.FinalExams')

    def setup_explorer_menu(self, site, user_type, m, ar=None):
        mg = self.get_menu_group()
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('ratings.Exams')
        m.add_action('ratings.AllChallenges')
        m.add_action('ratings.AllChallengeRatings')
        m.add_action('ratings.FinalExamRatings')
        # m.add_action('ratings.AllProjectRatings')
        m.add_action('ratings.RatingsSummaries')
