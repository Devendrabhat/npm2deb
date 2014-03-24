#!/usr/bin/python

from npm2deb import templates
import os

DEBUG_LEVEL = 0

def debug(level, msg):
    if level <= DEBUG_LEVEL:
        print(" debug [%s] - %s" % (level, msg))

def get_template(filename):
    result = None
    if filename is 'control':
        result = templates.CONTROL
    elif filename is 'copyright':
        result = templates.COPYRIGHT
    elif filename is 'rules':
        result = templates.RULES
    return result

def get_license(license):
    result = None
    name = license.lower().replace('-', '')
    if name.startswith('gpl2'):
        result = templates.LICENSES['GPL-2']
    elif name.startswith('gpl3'):
        result = templates.LICENSES['GPL-3']
    elif name.startswith('lgpl2'):
        result = templates.LICENSES['LGPL-2']
    elif name.startswith('lgpl3'):
        result = templates.LICENSES['LGPL-3']
    elif name.startswith('mit'):
        result = templates.LICENSES['MIT']
    elif name.startswith('expat'):
        result = templates.LICENSES['Expat']
    elif name.startswith('bsd'):
        result = templates.LICENSES['BSD']
    elif name.startswith('artistic'):
        result = templates.LICENSES['Artistic']
    elif name.startswith('apache'):
        result = templates.LICENSES['Apache']
    else:
        result = 'FIX_ME: please specify a license description'
    return result

def change_dir(dir):
    debug(2, "moving to directory %s" % dir)
    try:
        os.chdir(dir)
    except OSError as oserror:
        print ("OSError [%d]: %s at %s" % \
          (oserror.errno, oserror.strerror, oserror.filename))
        exit(1)

def create_debian_file(filename, content):
    create_file("debian/%s" % filename, content)

def create_file(filename, content):
    debug(2, "creating file %s" % filename)
    with open(filename, 'w') as writer:
        writer.write(content)

def create_dir(dir):
    debug(2, "creating directory %s" % dir)
    try:
        os.mkdir(dir)
    except OSError as oserror:
        print ("Error: directory %s already exists." % (oserror.filename))
        exit(1)
