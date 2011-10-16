# -*- coding: utf-8 -*-

"""
AutotestDaemon class definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'


import re
import os
from models import *


class AutotestDaemon(object):
    def __init__(self):
        pass

    def find_classes(self, curdir, regexp):
        """Recursive search for class-files
        regexp - class definition line regular expression:
            re.compile(r'class ([A-Za-z]+)')
        """
        classes = []
        for f in os.listdir(curdir):
            f = os.path.join(curdir, f)
            if os.path.isdir(f):
                classes.extend(self.find_classes(f, regexp))
            else:
                for line in open(f).xreadlines():
                    m = regexp.match(line)
                    if m:
                        classes.append((f, m.group(1)))
                        break
        return classes

    def search_code(self, search_dir):
        """Search all code-files starting from search_dir"""
        regexp = re.compile(r'class (\w+)\b')
        for f in self.find_classes(search_dir, regexp):
            print '>', f

    def search_tests(self, search_dir):
        """Search all tests-files starting from search_dir"""
        regexp = re.compile(r'class (\w+)Test\b')
        for f in self.find_classes(search_dir, regexp):
            print '?', f

    def add_project(self, project_name, code_dir, tests_dir):
        """Add new project"""
        pass


if __name__ == '__main__':
    d = AutotestDaemon()
    d.search_code('/home/hdg700/work/spravka/application/modules')
    d.search_tests('/home/hdg700/work/spravka/tests')
