#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""
Daemon start script
Inits standard unix daemon environment

Usage: autotestd [key]

-h, --help      show this message
"""

__author__ = 'Danilenko Alexander'
__email__ = 'hdg700@gmail.com'


import sys
import getopt
import autotestd
import daemon
import lockfile
from syslog import syslog

import config

exit(0)

class UsageError(Exception):
    """Exception raised for printing help message"""
    def __init__(self, msg='', help_only=False):
        self.msg = msg
        self.help_only = help_only


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    try:
        try:
            opts, args = getopt.getopt(argv, 'h', ['help'])

            for o, a in opts:
                if o in ['-h', '--help']:
                    raise UsageError(help_only=True)

        except getopt.error as e:
            raise UsageError(e)

    except UsageError as e:
        if e.help_only:
            print __doc__
        else:
            print e.msg
            print 'Use --help for more information'

    #context = autotestd.DaemonContext('/var/run/autotestd.pid')
    #context.start()

    #d = autotestd.AutotestDaemon()

    context = daemon.DaemonContext(
            #pidfile=lockfile.FileLock('/var/run/autotestd.pid')
            #detach_process=False
            )

    #f = open('/tmp/1', 'a')
    #context.files_preserve = [f]
    #f.write('before context\n')
    with context:
        autotestd.main()
#        f.write('context\n')
#        DBusGMainLoop(set_as_default=True)
#        d = autotestd.AutotestDaemon()
#        f.write('after daemon\n')
#        gtk.main()


if __name__ == '__main__':
    #sys.exit(main())
    main()
