#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""
AutotestDaemon class definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'


import sqlalchemy.orm.exc
import pyinotify
import pynotify

import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from datetime import datetime

from models import *


class FoundException(Exception):
    """Raised to stop searching loop"""
    def __init__(self, project):
        self.project = project


class ADProcessEvent(pyinotify.ProcessEvent):
    """Inotify process event class"""
    def __init__(self):
        self.projects = {}

    def process_IN_MODIFY(self, event):
        try:
            for p, wdct in self.projects.items():
                if event.wd in wdct:
                    raise(FoundException(p))
        except FoundException as e:
            self.run_test(e.project, event.pathname)

    def get_project_by_name(self, name):
        """Returns project with specified name"""
        try:
            for p, wdct in self.projects.items():
                if p.name == name:
                    raise(FoundException(p))
        except FoundException as e:
            return p, wdct

        return False


    def run_test(self, project, filename):
        """Runs test for speciefed class from project"""
        rec = project.get_record_for_filename(filename)
        if rec is False:
            rec = project.add_file(filename)
            if not rec:
                return False

        if rec is None:
            return False

        if type(rec) is ADCode:
            test = rec.get_test()
        else:
            test = rec

        if not test:
            return False

        test_status = test.get_status()
        if pynotify.init('AutotestDaemon'):
            if test_status == 0:
                pynotify.Notification('Test  \"{0}\"'.format(test.classname), 'Success!', 'face-smile').show()
            else:
                pynotify.Notification('Test  \"{0}\"'.format(test.classname), 'Failed!', 'face-angry').show()

        return test_status


class AutotestDaemon(dbus.service.Object):
    """
    Autotest Daemon class
    Monitors files modify state, handles dbus events
    """
    def __init__(self):
        """Init dbus listener, inotifier, projects"""
        bus_name = dbus.service.BusName('hdg700.autotestd', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/hdg700/autotestd/AutotestDaemon')

        self.watch_manager = pyinotify.WatchManager()
        self.watch_mask = pyinotify.IN_MODIFY | pyinotify.IN_CREATE
        self.notify_process = ADProcessEvent()
        self.notifier = pyinotify.ThreadedNotifier(self.watch_manager, self.notify_process)

        self.init_notifier_from_db()
        self.notifier.start()

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client',
            in_signature='s')
    def dbus_hello(self, s):
        return [repr(i) for i in self.notify_process.projects.keys()]

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client',
            in_signature='sss')
    def dbus_add(self, project, code_dir, tests_dir):
        """Add method called via dbus"""
        if self.new_project(project, code_dir, tests_dir):
            if pynotify.init('AutotestDaemon'):
                pynotify.Notification('New project  \"{0}\"'.format(project), 'Success!', 'face-smile').show()
            return 'New project accepted'
        return False

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client',
            in_signature='ssss')
    def dbus_edit(self, project, name, code_dir, tests_dir):
        """Edit method called via dbus"""
        res = self.notify_process.get_project_by_name(project)
        if not res:
            return 'No such project!'

        if self.delete_project(*res):
            if self.new_project(name, code_dir, tests_dir):
                if pynotify.init('AutotestDaemon'):
                    pynotify.Notification('Project edited  \"{0}\"'.format(name), 'Success!', 'face-smile').show()
                return 'Project edited'
            else:
                return 'Project deleted'

        return False

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client',
            in_signature='s')
    def dbus_delete(self, project):
        """Delete method called via dbus
        'project' is a name of project to be delted"""
        res = self.notify_process.get_project_by_name(project)
        if not res:
            return 'No such project!'

        if self.delete_project(*res):
            if pynotify.init('AutotestDaemon'):
                pynotify.Notification('Project deleted  \"{0}\"'.format(project), 'Success!', 'face-smile').show()
            return 'Project deleted'
        else:
            return False

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client',
            in_signature='s')
    def dbus_info(self, project):
        """Info method called via dbus"""
        res = self.notify_process.get_project_by_name(project)
        if not res:
            return False

        project = res[0]
        return {'name': project.name,
                'code_dir': project.code_dir,
                'test_dir': project.test_dir,
                'code_count': str(project.code_count()),
                'test_count': str(project.test_count())}

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client')
    def dbus_list(self):
        """List method called via dbus"""
        l = [(i.name, i.code_dir, i.test_dir) for i in self.notify_process.projects.keys()]
        if not l:
            return False
        return l

    def watch_project(self, project):
        """Add project to notify watcher"""
        self.notify_process.projects[project] = []
        try:
            self.notify_process.projects[project].extend(
                    self.watch_manager.add_watch(
                            project.code_dir, self.watch_mask, rec=True).values())

            self.notify_process.projects[project].extend(
                    self.watch_manager.add_watch(
                            project.test_dir, self.watch_mask, rec=True).values())
        except AttributeError:
            pass

    def init_notifier_from_db(self):
        """Get all projects from db and init notifier for it"""
        projects = ADProject.get_all()
        if not projects:
            return False

        for p in projects:
            self.watch_project(p)

    def delete_project(self, project, wdct):
        """Deletes project, remove wdct from inotify wather"""
        res = self.watch_manager.rm_watch(wdct)
        if not all(res.values()):
            return False

        del self.notify_process.projects[project]
        session = get_session()
        session.query(ADCode).filter(ADCode.project == project).delete()
        session.query(ADTest).filter(ADTest.project == project).delete()
        session.delete(project)
        session.commit()

        return True

    def new_project(self, project_name, code_dir, tests_dir):
        """Add new project"""
        session = get_session()
        try:
            p = ADProject(project_name, code_dir, tests_dir)
            session.add(p)
            session.commit()

            self.watch_project(p)

            return p

        except sqlalchemy.exc.IntegrityError:
            session.rollback()
            return False

    def notify_loop(self):
        while True:
            self.notifier.process_events()
            if self.notifier.check_events():
                self.notifier.read_events()


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    gtk.gdk.threads_init()
    d = AutotestDaemon()
    try:
        gtk.main()
    except KeyboardInterrupt:
        d.notifier.stop()
        exit(1)

