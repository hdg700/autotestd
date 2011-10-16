#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""TRYING TO USE PYINOTIFY"""

import os
import pyinotify
from pyinotify import WatchManager, Notifier, ThreadedNotifier, ProcessEvent

wm = WatchManager()

mask = pyinotify.IN_MODIFY

class PTmp(ProcessEvent):
    def process_IN_MODIFY(self, event):
        print [v for v,k in wdc.items() if event.wd == k], event.name
        print [v for v,k in wdt.items() if event.wd == k], event.name

notifier = Notifier(wm, PTmp())

wdc = wm.add_watch('./application/modules', mask, rec=True)
wdt = wm.add_watch('./tests', mask, rec=True)

print wdc.values()
print wdt.values()

while True:
    try:
        notifier.process_events()
        if notifier.check_events():
            notifier.read_events()
    except KeyboardInterrupt:
        notifier.stop()
        break
