# -*- coding: utf-* -*-

"""
Autotestd models definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'

import re
import os
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import *


engine = create_engine('sqlite:///autotestd.db')
#engine.echo = True
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)


class ADCode(Base):
    """Autotest daemon code model"""
    __tablename__ = 'ad_code'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('ad_project.id'))
    classname = Column(Unicode(50), nullable=False)
    filename = Column(Unicode(200), nullable=False)

    project = relation('ADProject', backref='codes')

    def __init__(self, project, classname, filename):
        """Autotest daemon code model class initialization"""
        self.project = project
        self.classname = classname
        self.filename = filename


class ADTest(Base):
    """Autotest daemon Test model"""
    __tablename__ = 'ad_test'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('ad_project.id'))
    classname = Column(Unicode(50), nullable=False)
    filename = Column(Unicode(200), nullable=False)

    project = relation('ADProject', backref='tests')

    def __init__(self, project, classname, filename):
        """Autotest daemon test model class initialization"""
        self.project = project
        self.classname = classname
        self.filename = filename


class ADProject(Base):
    """Autotest daemon project model"""
    __tablename__ = 'ad_project'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True, nullable=False)
    code_dir = Column(Unicode(200), nullable=False)
    test_dir = Column(Unicode(200), nullable=False)
    active = Column(Boolean)

    def __init__(self, name, code_dir, test_dir):
        """Autotest daemon project class initialization"""
        self.name = name
        self.code_dir = code_dir
        self.test_dir = test_dir
        self.active = True

        self.search_code()
        self.search_tests()

    def __repr__(self):
        return u'<ADProject: {0}>'.format(self.name)

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

    def search_code(self):
        """Search all code-files starting from search_dir"""
        session = Session()
        regexp = re.compile(r'class (\w+)\b')
        for f, c in self.find_classes(self.code_dir, regexp):
            session.add(ADCode(self, c, f))

    def search_tests(self):
        """Search all tests-files starting from search_dir"""
        session = Session()
        regexp = re.compile(r'class (\w+)Test\b')
        for f, c in self.find_classes(self.test_dir, regexp):
            session.add(ADTest(self, c, f))

    # Database queries methods
    @staticmethod
    def get_all():
        session = Session()
        try:
            return session.query(ADProject)\
                    .filter(ADProject.active == True).all()
        except NoResultFound:
            return False


Base.metadata.create_all()
