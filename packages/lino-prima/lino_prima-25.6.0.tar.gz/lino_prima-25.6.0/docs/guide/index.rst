.. _prima.guide:

=======================
Lino Prima User's Guide
=======================

Lino Prima is a Lino application for primary schools used to manage evaluation
results and to print certificates.

Design considerations
=====================

Lino Prima is the first real-world Lino application that does not use the
Extension Library.

It uses only the following plugins, which are part of the Lino core: users,
periods

Concepts and database models:

- Teacher and Pupil are just user types

- School year (Schuljahr): A concrete period of time, usually lasting
  from September to June. Examples: 23-24, 24-25, ...

- Period (Periode): A subdivision of a year into smaller slices of time.
  Examples: P1 (first semester) and P2 (second semester).

- Grade (Jahrgangsstufe): A subdivision of a ↗subject into consecutive years.
  1, 2, ... 6
  Examples: 1. Schuljahr, 2. Schuljahr, ...

- Subject (Unterrichtsfach).
  An area of knowledge that is being taught at this school.

  Fields: designation, ☑complex.
  Examples: Wissenschaften, Kunst, Musik, Sport, Schriftbild, Heimatkunde/Sachkunde,
  Französisch, Mathematik, Religion, Deutsch

  Every subject can have a set of ↗skills. "complex" means a complex schema for
  evaluations using ↗skills, ↗blocks and ↗tests

  Every subject can have a set of ↗groups.

- Skill (Kompetenz): A subdivision of a ↗subject into different learning goals or topics.
  Fields: designation, ↗subject.
  Examples: Deutsch:Schreiben, Deutsch:Lesen, Mathematik:Arithmetik

- ProjectTemplate (Baustein): a set of tasks and tests about a given subject
  that can be individually by a pupil.

  Fields: designation, ref, ↗subject, ↗main_skill, ↗color, ↗grade

  Examples: Erlebnisse spannend erzählen (Erle), Rund um Tiere (Tier), Berichten
  (Ber), Geschichten aus dem Leben erzählen (Leb)

- ProjectSection (Bausteinabschnitt): a subdivision of a ↗projecttemplate.
  Fields: designation, seqno, ↗block, ↗main_skill, max_rating

- Group (Klasse): A group of ↗pupils who work together for a given ↗year,
  following a given ↗course.
  Examples: 1A, 1B, 2A, 2B, 2C, ...
  Fields: designation, ↗grade

- Enrolment (Einschreibung): when a given ↗pupil is member of a given ↗group.
  Fields: ↗pupil, ↗group.

- Role (Lehrerrolle): a specific role to be assumed by a given ↗teacher in a given ↗group.
  Examples: Klassenleiter, Sportlehrer,...

- Cast (Rollenbelegung) : the fact that a given ↗teacher assumes a given ↗role in a given
  ↗group for a given ↗subject.

  Fields: ↗teacher, ↗group, ↗role, ↗subject

- Exam (Test): A test that has been made in a given group of pupils.
  Fields: designation, ↗group, ↗period, ↗subject, ↗teacher.
  Each exam has a list of "items".

- Challenge (Leistung): when a given ↗skill is being measured during a given ↗exam or ↗project section.
  Fields: ↗probe, ↗skill, ↗exam, ↗project_section, max_rating (Höchstpunktzahl)

- Rating (Bewertung): The rating given to a given ↗pupil for a given ↗challenge .
  Fields: ↗probeitem, ↗pupil, rating, ↗teacher, ↗period

- Certificate (Zeugnis)
  Fields: ↗enrolment

  Difference between "Certificate" an "School report":
  https://forum.wordreference.com/threads/school-report-or-certificate.2901105


- GroupBlock:
  A ↗block to be taught to a given ↗group.
  Fields : ↗block, ↗group.



Data migration
==============

- `BausteinArbeitsBewertung` and `LeistungsBewertung` become `Rating`
- `Leistung` becomes `Expectation`, `BausteinArbeit` merges into `Expectation`
- `Kompetenz` becomes `Skill`

- `Baustein` merges into `Exam`.

Tests, Bausteine und Abschlusstests werden in Lino drei Arten von "Prüfungen".
Eine Prüfung kann mehrere Abschnitte haben (nur Bausteine nutzen dies momentan).
Existierende Tests werden importiert als Prüfungen ohne Abschnitt, d.h.
alle Leistungen stehen untereinander.
existierende Abschlusstests werden importiert als Prüfungen ohne Abschnitt und mit nur einer einzigen Leistung.
Existierende Abschlusstests werden importiert als Prüfungen ohne Abschnitt und mit nur .
