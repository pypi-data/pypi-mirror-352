# -*- coding: utf-8 -*-
# fmt: off

import datetime

from atelier.sphinxconf import configure; configure(globals())
from lino.sphinxcontrib import configure; configure(
    globals(), 'lino_prima.projects.prima1.settings')

extensions += ['lino.sphinxcontrib.help_texts_extractor']
help_texts_builder_targets = {'lino_prima.': 'lino_prima.lib.prima'}

project = html_title = "Lino Prima"
copyright = '2016-{} Rumma & Ko Ltd'.format(datetime.date.today().year)

# html_context.update(public_url='https://prima.lino-framework.org')
