from lino_prima.lib.prima.settings import *


class Site(Site):
    title = "Our Lino Prima site"


SITE = Site(globals())
DEBUG = True
