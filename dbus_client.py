#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import dbus

bus = dbus.SessionBus()
pr = bus.get_object('hdg700.autotestd', '/hdg700/autotestd')
ar = pr.dbus_hello()
for i in ar:
    print i
