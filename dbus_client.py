#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import dbus

bus = dbus.SessionBus()
pr = bus.get_object('hdg700.autotestd', '/hdg700/autotestd/AutotestDaemon')
ar = pr.dbus_hello('asdf', dbus_interface='hdg700.autotestd.AutotestDaemon.client')
for i in ar:
    print i
