# -*- coding: utf-8 -*-

"""
AutotestDaemon class definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'


from models import *
import sqlalchemy.orm.exc


class AutotestDaemon(object):
    def __init__(self):
        pass

    def add_project(self, project_name, code_dir, tests_dir):
        """Add new project"""
        try:
            session = Session()
            pr = ADProject(project_name, code_dir, tests_dir)
            session.add(pr)
            session.commit()
        except sqlalchemy.exc.IntegrityError:
            pass


if __name__ == '__main__':
    d = AutotestDaemon()
    d.add_project('spravka', '/home/hdg700/work/spravka/application/modules', '/home/hdg700/work/spravka/tests')
