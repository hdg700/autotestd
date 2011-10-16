# -*- coding: utf-* -*-

"""
Autotestd models definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import *


engine = create_engine('sqlite:///autotestd.db')
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base(bind=engine)


class ADProject(Base):
    """Autotest daemon project model"""
    __tablename__ = 'ad_project'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True, nullable=False)
    code_dir = Column(Unicode(200), nullable=False)
    test_dir = Column(Unicode(200), nullable=False)

    def __init__(self, name, code_dir, test_dir):
        """Autotest daemon project class initialization"""
        self.name = name
        self.code_dir = code_dir
        self.test_dir = test_dir

    def __repr__(self):
        return u'<ADProject: {0}>'.format(self.name)


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
