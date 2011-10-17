#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""TRYING TO USE PYINOTIFY"""

import os
import pyinotify
from pyinotify import WatchManager, Notifier, ThreadedNotifier, ProcessEvent


wm = WatchManager()

mask = pyinotify.IN_MODIFY

prjs = {}

class PTmp(ProcessEvent):
    def process_IN_MODIFY(self, event):
        class FoundException(Exception):
            def __init__(self, project):
                self.project = project

        class FoundCodeException(FoundException):
            pass

        class FoundTestException(FoundException):
            pass

        try:
            for p, wdct in prjs.items():
                if event.wd in wdct[0]:
                    raise(FoundCodeException(p))
                elif event.wd in wdct[1]:
                    raise(FoundTestException(p))

        except FoundCodeException as e:
            print 'Found code:', e.project, ' -> ', event.pathname
        except FoundTestException as e:
            print 'Found test:', e.project, ' -> ', event.pathname
        else:
            print 'Not found'
        #print [v for v,k in wdc.items() if event.wd == k], event.name
        #print [v for v,k in wdt.items() if event.wd == k], event.name

notifier = Notifier(wm, PTmp())

#wdc = wm.add_watch('./application/modules', mask, rec=True)
#wdt = wm.add_watch('./tests', mask, rec=True)
#prjs['spravka'] = (wm.add_watch('./application/modules', mask, rec=True), wm.add_watch('./tests', mask, rec=True))
prjs['spravka'] = ([], [])
prjs['spravka'][0].extend(wm.add_watch('./application/modules', mask, rec=True).values())
prjs['spravka'][1].extend(wm.add_watch('./tests', mask, rec=True).values())

#print wdc.values()
#print wdt.values()

while True:
    try:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
