#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

"""
Daemon start script
Inits standard unix daemon environment

Usage: autotestd [key]

-h, --help      show this message
"""

import sys
import getopt


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


if __name__ == '__main__':
    sys.exit(main())
