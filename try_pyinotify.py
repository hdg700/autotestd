#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""TRYING TO USE PYINOTIFY"""

import os
import pyinotify
from pyinotify import WatchManager, Notifier, ThreadedNotifier, ProcessEvent


wm = WatchManager()

mask = pyinotify.IN_MODIFY

prjs = {}

# по идее, не надо разделять дескрипторы на тесты и код:
# всегда сразу искать тест по имени класса и пытаться его запустить

# либо отдельные обработчики для кода и тестов!!!
class PTmp(ProcessEvent):
    def process_IN_MODIFY(self, event):
        class FoundException(Exception):
            def __init__(self, project):
                self.project = project

        try:
            for p, wdct in prjs.items():
                if event.wd in wdct:
                    raise(FoundException(p))

        except FoundException as e:
            print 'Found code:', e.project, ' -> ', event.pathname

notifier = Notifier(wm, PTmp())

prjs['spravka'] = []
prjs['spravka'].extend(wm.add_watch('./application/modules', mask, rec=True).values())
prjs['spravka'].extend(wm.add_watch('./tests', mask, rec=True).values())

while True:
    try:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
