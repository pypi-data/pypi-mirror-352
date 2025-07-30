# how to run a single test:
# $ python -m unittest tests.test_demo.Main.test_prima1

from lino.utils.pythontest import TestCase


class Main(TestCase):

    demo_projects_root = "lino_prima/projects"

    def test_prima1(self):
        self.do_test_demo_project('prima1')
