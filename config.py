# -*- coding: utf-8 -*-

import os

__all__ = ['CONF_CLASS_REGEXP', 'CONF_TEST_REGEXP', 'CONF_TEST_COMMAND']

CONF_CLASS_REGEXP = r'class (\w+)\b'
CONF_TEST_REGEXP = r'class (\w+)Test\b'
CONF_TEST_COMMAND = u'phpunit'

try:
    import ConfigParser
    #cfilename = '/etc/autotestd/config.ini'
    cfilename = 'config.ini'
    conf = ConfigParser.ConfigParser()
    if os.path.exists(cfilename) and os.path.isfile(cfilename) or True:
        conf.read(cfilename)
        try:
            CONF_CLASS_REGEXP = conf.get('General', 'class_regexp', CONF_CLASS_REGEXP)
            CONF_TEST_REGEXP = conf.get('General', 'test_regexp', CONF_TEST_REGEXP)
            CONF_TEST_COMMAND = conf.get('General', 'test_command', CONF_TEST_COMMAND)
        except ConfigParser.NoSectionError:
            pass
finally:
    del cfilename
    del conf


