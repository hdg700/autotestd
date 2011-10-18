# -*- coding: utf-8 -*-

"""
AutotestDaemon class definition module
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'


from models import *
import sqlalchemy.orm.exc
import pyinotify


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

        print test.run()

class AutotestDaemon(object):
    """
    Autotest Daemon class
    Monitors files modify state, handles dbus events
    """
    def __init__(self):
        self.watch_manager = pyinotify.WatchManager()
        self.watch_mask = pyinotify.IN_MODIFY
        self.notify_process = ADProcessEvent()
        self.notifier = pyinotify.Notifier(self.watch_manager, self.notify_process)

        self.init_notifier_from_db()

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
                self.notifier.process_events()
                if self.notifier.check_events():
                    self.notifier.read_events()
            except KeyboardInterrupt:
                self.notifier.stop()
                break


if __name__ == '__main__':
    d = AutotestDaemon()
    #d.new_project('spravka', '/home/hdg700/work/spravka/application/modules', '/home/hdg700/work/spravka/tests')
    d.notify_loop()
