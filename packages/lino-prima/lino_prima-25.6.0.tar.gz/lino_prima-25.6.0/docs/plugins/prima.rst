.. _prima.plugins.prima:
.. doctest docs/plugins/prima.rst

======================================
``prima`` : main plugin for Lino Prima
======================================

In Lino Prima this plugin defines the :xfile:`locale` directory for all
translations.

.. contents::
  :local:

.. include:: /../docs/shared/include/tested.rst

>>> import lino
>>> lino.startup('lino_prima.projects.prima1.settings')
>>> from lino.api.doctest import *

Window fields
=============

The following snippet verifies whether all window fields are visible.

>>> print(analyzer.show_window_fields()) #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE +REPORT_UDIFF
- about.About.reset_password : email, username, new1, new2
- about.About.show : about_html
- about.About.sign_in : username, password
- about.About.verify_user : email, verification_code
- cert.CertSections.detail : cert_template, seqno, subject, id, remark, remark_de, cert.ElementsBySection, cert.ElementsBySection
- cert.CertTemplates.detail : designation, designation_de, cert.SectionsByTemplate, cert.SectionsByTemplate, cert.SectionsByTemplate
- cert.Certificates.detail : enrolment, period, state, id, cert.SectionResponsesByCertificate, SectionResponsesByCertificate, social_skills_comment, final_verdict, absences_p, absences_m, absences_u
- cert.Certificates.insert : enrolment, period
- cert.ElementResponses.detail : section_response, section_response__certificate__enrolment, section_response__certificate__period, cert_element, cert_element__skill, max_score, computed_rating, score, rating_buttons, ratings_report
- cert.SectionResponses.detail : certificate, section, rating_type, max_score, score, smiley, predicate, remark, cert.RatingsByResponse
- checkdata.Checkers.detail : value, text, checkdata.MessagesByChecker, checkdata.MessagesByChecker
- checkdata.Messages.detail : checker, owner, message, user, id
- gfks.ContentTypes.detail : id, app_label, model, base_classes, gfks.BrokenGFKsByModel, BrokenGFKsByModel
- linod.SystemTasks.detail : seqno, procedure, name, every, every_unit, log_level, disabled, status, requested_at, last_start_time, last_end_time, message
- linod.SystemTasks.insert : procedure, every, every_unit
- periods.StoredPeriods.merge_row : merge_to, reason
- periods.StoredYears.merge_row : merge_to, reason
- projects.ProjectSections.detail : seqno, designation, designation_de, project_template, id, ratings.ChallengesByProjectSection, ratings.ChallengesByProjectSection
- projects.ProjectTemplates.detail : designation, designation_de, short_header, display_color, id, main_skill, grade, projects.SectionsByProject
- projects.Projects.detail : enrolment, date_started, remark, gr_1, gr_2, gr_3, gr_4, ratings.ChallengeRatingsByProject, ratings.ChallengeRatingsByProject, ratings.ChallengeRatingsByProject, template, id, ratings_done, total_score, total_max_score
- projects.ProjectsByEnrolment.insert : enrolment, template, remark
- ratings.ChallengeRatings.detail : challenge, max_score, enrolment, score, rating_buttons, period, teacher, date_done
- ratings.ChallengeRatings.set_score_action : score
- ratings.ChallengeRatingsByEnrolment.insert : challenge, max_score, enrolment, score, rating_buttons, period, teacher, date_done
- ratings.Challenges.detail : exam, project_section, id, seqno, skill, max_score, ratings.RatingsByChallenge, ratings.RatingsByChallenge, ratings.RatingsByChallenge
- ratings.ChallengesByExam.insert : skill, max_score
- ratings.ChallengesByProjectSection.insert : skill, max_score
- ratings.ExamResponses.detail : exam, enrolment, remark, ratings.RatingsByResponse, ratings.RatingsByResponse, ratings.RatingsByResponse
- ratings.ExamResponsesByEnrolment.insert : exam, remark
- ratings.Exams.detail : subject, group, date, seqno, heading, ratings.ResponsesByExam, ratings.ResponsesByExam, period, id, user, ratings.ChallengesByExam, ratings.ChallengesByExam
- ratings.ExamsByCourse.insert : heading, date
- ratings.ExamsByGroup.insert : subject, heading
- ratings.FinalExamRatings.detail : exam, enrolment, score, max_score, teacher, period, date_done
- ratings.RatingsSummaries.detail : id, master, skill, enrolment, challenge
- school.Casts.detail : group, role, user
- school.CastsByGroup.insert : role, user
- school.CastsByUser.insert : group, role
- school.Courses.detail : ratings.ExamsByCourse, ratings.ExamsByCourse, ratings.SummariesByCourse, ratings.SummariesByCourse, group, subject, remark, remark_de
- school.Courses.insert : group, subject
- school.Enrolments.detail : pupil, group, projects.ProjectsByEnrolment, cert.CertificatesByEnrolment, ratings.ChallengeRatingsByEnrolment, ratings.FinalRatingsByEnrolment, ratings.FinalRatingsByEnrolment
- school.Grades.detail : id, ref, designation, designation_de, rating_conditions, rating_conditions_de, projects.ProjectTemplatesByGrade, projects.ProjectTemplatesByGrade, school.GroupsByGrade, school.GroupsByGrade, GroupsByGrade
- school.Grades.merge_row : merge_to, reason
- school.Groups.detail : designation, designation_de, school.CoursesByGroup, projects.PupilsAndProjectsByGroup, ratings.ExamsByGroup, ratings.ExamsByGroup, ratings.SkillsByGroup, ratings.SkillsByGroup, ratings.SkillsByGroup, year, grade, id, remark, remark_de, school.EnrolmentsByGroup, school.CastsByGroup
- school.Skills.detail : designation, designation_de, id, subject, with_exams, projects.ProjectTemplatesBySkill, projects.ProjectTemplatesBySkill, ratings.ChallengesBySkill, ratings.ChallengesBySkill, cert.RatingsBySkill
- school.Subjects.detail : designation, designation_de, id, advanced, icon_text, image_file, rating_type, school.CoursesBySubject
- system.SiteConfigs.detail : default_build_method, simulate_today
- uploads.UploadTypes.detail : id, upload_area, wanted, max_number, shortcut, name, name_de, uploads.UploadsByType, uploads.UploadsByType, uploads.UploadsByType
- uploads.UploadTypes.insert : name, name_de, upload_area
- uploads.Uploads.camera_stream : type, description
- uploads.Uploads.detail : file, volume, library_file, user, owner, upload_area, type, description, preview
- uploads.Uploads.insert : type, description, file, volume, library_file, user
- uploads.UploadsByController.insert : file, volume, library_file, type, description
- uploads.Volumes.detail : ref, root_dir, description, overview, uploads.UploadsByVolume, uploads.UploadsByVolume, UploadsByVolume
- uploads.Volumes.insert : ref, root_dir, description
- uploads.Volumes.merge_row : merge_to, reason
- users.AllUsers.change_password : current, new1, new2
- users.AllUsers.detail : username, user_type, language, id, created, modified, school.EnrolmentsByPupil, school.CastsByUser, first_name, last_name, nickname, initials, users.AuthoritiesGiven, users.AuthoritiesGiven, users.AuthoritiesTaken, users.AuthoritiesTaken
- users.AllUsers.insert : username, email, first_name, last_name, language, user_type
- users.AllUsers.merge_row : merge_to, reason
- users.AllUsers.verify_me : verification_code
<BLANKLINE>
