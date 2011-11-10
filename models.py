# -*- coding: utf-* -*-

"""
Autotestd models definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'

#import commands
import re
import os
from syslog import syslog
from config import *
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.exc import *
from subprocess import Popen, PIPE


engine = create_engine('sqlite:////etc/autotestd/projects.db',
        connect_args={'check_same_thread':False})
#engine.echo = True
Session = scoped_session(sessionmaker(bind=engine))
#Session = sessionmaker(bind=engine)
#Session.extension = Session.extension.configure(save_on_init=False)
Base = declarative_base(bind=engine)

session = None
def get_session():
    global session
    if not session:
        session = Session()

    return session

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
        self.classname = unicode(classname)
        self.filename = unicode(filename)

    def __repr__(self):
        return u'<ADCode ({0})>'.format(self.classname)

    def get_test(self):
        """Return test for self code"""
        session = get_session()
        return session.query(ADTest)\
                .filter(ADTest.classname == self.classname)\
                .first()


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
        self.classname = unicode(classname)
        self.filename = unicode(filename)

    def __repr__(self):
        return u'<ADTest ({0})>'.format(self.classname)

    def get_status(self):
        """Run self test file"""
        try:
            p = Popen(CONF_TEST_COMMAND.split() + [self.filename], shell=False, stdout=PIPE, stdin=PIPE, stderr=PIPE)
            p.wait()
            return p.returncode
        except OSError:
            syslog(u'Test command not valid! See /etc/autotestd/config.ini')
        return 2


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
        self.name = unicode(name)
        self.code_dir = unicode(code_dir)
        self.test_dir = unicode(test_dir)

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

                    if 'class' in line:
                        break
        return classes

    def search_code(self):
        """Search all code-files starting from search_dir"""
        session = get_session()
        regexp = re.compile(CONF_CLASS_REGEXP)
        for f, c in self.find_classes(self.code_dir, regexp):
            session.add(ADCode(self, c, f))

    def search_tests(self):
        """Search all tests-files starting from search_dir"""
        session = get_session()
        regexp = re.compile(CONF_TEST_REGEXP)
        for f, c in self.find_classes(self.test_dir, regexp):
            session.add(ADTest(self, c, f))

    def rescan_filename(self, record):
        """Rescan file name, update or delete record
        Return False, when record is already None"""
        if not record:
            return False

        if type(record) is ADCode:
            regexp = re.compile(CONF_CLASS_REGEXP)
        else:
            regexp = re.compile(CONF_TEST_REGEXP)

        for line in open(record.filename).xreadlines():
            m = regexp.match(line)
            if m:
                if m.group(1) == record.classname:
                    # имя класса осталось прежним
                    return record
                else:
                    # имя класса изменилось
                    session = get_session()
                    record.classname = unicode(m.group(1))
                    session.add(record)
                    session.commit()
                    return record

            if line.startswith('class'):
                break

        session = get_session()
        session.delete(record)
        session.commit()
        return None

    def get_record_for_filename(self, filename):
        """Search ADCode of ADTest with specified filename"""
        session = get_session()
        try:
            code = session.query(ADCode)\
                    .filter(ADCode.filename == unicode(filename)).first()
            if code:
                return self.rescan_filename(code)

            test = session.query(ADTest)\
                    .filter(ADTest.filename == unicode(filename)).first()

            return self.rescan_filename(test)

        except NoResultFound:
            return False

    def add_file(self, filename):
        """Add new file in project"""
        if self.code_dir in filename:
            file_class = ADCode
            regexp = re.compile(CONF_CLASS_REGEXP)
        elif self.test_dir in filename:
            file_class = ADTest
            regexp = re.compile(CONF_TEST_REGEXP)
        else:
            return False

        for line in open(filename).xreadlines():
            m = regexp.match(line)
            if m:
                obj = file_class(self, m.group(1), filename)
                session = get_session()
                session.add(obj)
                session.commit()

                return obj

            if 'class' in line:
                break

        return False

    def code_count(self):
        """Returns code classes count"""
        session = get_session()
        try:
            return session.query(func.count(ADCode.id)).filter(ADCode.project == self).first()[0]
        except NoResultFound:
            return 0

    def test_count(self):
        """Returns test classes count"""
        session = get_session()
        try:
            return session.query(func.count(ADTest.id)).filter(ADTest.project == self).first()[0]
        except NoResultFound:
            return 0

    # Database queries methods
    @staticmethod
    def get_all():
        session = get_session()
        try:
            return session.query(ADProject).all()
        except NoResultFound:
            return False

Base.metadata.create_all()
