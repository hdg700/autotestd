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
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from models import *

# Inits gtk threads to use inotify and dbus together
gobject.threads_init()

class ADProcessEvent(pyinotify.ProcessEvent):
    """
    Inotify process event class
    """
    def __init__(self):
        self.projects = {}

    def process_IN_MODIFY(self, event):
        class FoundException(Exception):
            """Raised to stop searching loop"""
            def __init__(self, project):
                self.project = project

        try:
            for p, wdct in self.projects.items():
                if event.wd in wdct:
                    raise(FoundException(p))
        except FoundException as e:
            self.run_test(e.project, event.pathname)

    def run_test(self, project, filename):
        """Runs test for speciefed class from project"""
        test = project.get_test_for_code(filename)
        if not test:
            return False

        test_status = test.get_status()
        if pynotify.init('AutotestDaemon'):
            if test_status == 0:
                pynotify.Notification('Test  \"{0}\"'.format(test.classname), 'Success!', 'face-smile').show()
            else:
                pynotify.Notification('Test  \"{0}\"'.format(test.classname), 'An error ocured...', 'face-sad').show()

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
        self.watch_mask = pyinotify.IN_MODIFY
        self.notify_process = ADProcessEvent()
        self.notifier = pyinotify.ThreadedNotifier(self.watch_manager, self.notify_process)

        self.init_notifier_from_db()
        self.notifier.start()

    @dbus.service.method(dbus_interface='hdg700.autotestd.AutotestDaemon.client', in_signature='s')
    def dbus_hello(self, s):
        print s
        return [repr(i) for i in self.notify_process.projects.keys()]

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

    def new_project(self, project_name, code_dir, tests_dir):
        """Add new project"""
        try:
            session = Session()
            p = ADProject(project_name, code_dir, tests_dir)
            session.add(p)
            session.commit()

            self.watch_project(p)
        except sqlalchemy.exc.IntegrityError:
            pass

    def notify_loop(self):
        while True:
            try:
#                self.notifier.process_events()
#                if self.notifier.check_events():
#                    self.notifier.read_events()
                pass
            except KeyboardInterrupt:
                self.notifier.stop()
                break


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    d = AutotestDaemon()
    try:
        gtk.main()
    except KeyboardInterrupt:
        d.notifier.stop()
        exit(1)
