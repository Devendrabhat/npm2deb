#!/usr/bin/python

from argparse import ArgumentParser
from npm2deb import Npm2Deb, utils, templates, helper, \
    DEBHELPER, STANDARDS_VERSION
from subprocess import call
import os

def main():
    parser = ArgumentParser(prog='npm2deb')
    parser.add_argument('-D', '--debug', type=int, help='set debug level')

    subparsers = parser.add_subparsers(title='commands')

    parser_create = subparsers.add_parser('create', \
        help='create the debian files')
    parser_create.add_argument('-n', '--noclean', action="store_true", \
        default=False, help='do not remove files downloaded with npm')
    parser_create.add_argument('-d', '--debhelper', default=DEBHELPER, \
        help='specify debhelper version [default: %(default)s]')
    parser_create.add_argument('-l', '--license', default=None, \
        help='license used for debian files [default: the same for upstream]')
    parser_create.add_argument('-s', '--standards', default=STANDARDS_VERSION, \
        help='set standards-version [default: %(default)s]')
    parser_create.add_argument('node_module', \
        help='node module available via npm')
    parser_create.set_defaults(func=create)

    parser_depends = subparsers.add_parser('depends', \
        help='show module dependencies in npm and debian')
    parser_depends.add_argument('-r', '--recursive', action="store_true", \
        default=False, help='look for binary dependencies recursively')
    parser_depends.add_argument('-f', '--force', action="store_true", \
        default=False, help='force inspection for modules already in debian')
    parser_depends.add_argument('-b', '--binary', action="store_true", \
        default=False, help='show binary dependencies')
    parser_depends.add_argument('-B', '--builddeb', action="store_true", \
        default=False, help='show show build dependencies')
    parser_depends.add_argument('node_module', \
        help='node module available via npm')
    parser_depends.set_defaults(func=show_dependencies)

    parser_rdepends = subparsers.add_parser('rdepends', \
        help='show the reverse dependencies for module')
    parser_rdepends.add_argument('node_module', \
        help='node module available via npm')
    parser_rdepends.set_defaults(func=show_reverse_dependencies)

    parser_search = subparsers.add_parser('search', \
        help="look if module is already in debian")
    parser_search.add_argument('-b', '--bug', action="store_true", \
        default=False, help='search for existing bug in wnpp')
    parser_search.add_argument('-d', '--debian', action="store_true", \
        default=False, help='search for existing package in debian')
    parser_search.add_argument('-r', '--repository', action="store_true", \
        default=False, help='search for existing repository in alioth')
    parser_search.add_argument('node_module', \
        help='node module available via npm')
    parser_search.set_defaults(func=search_for_module)

    parser_itp = subparsers.add_parser('itp', \
        help="print a itp bug template")
    parser_itp.add_argument('node_module', \
        help='node module available via npm')
    parser_itp.set_defaults(func=print_itp)

    parser_license = subparsers.add_parser('license', \
        help='print license template and exit')
    parser_license.add_argument('-l', '--list', action="store_true", \
        default=False, help='show the available licenses')
    parser_license.add_argument('name', nargs='?', \
        help='the license name to show')
    parser_license.set_defaults(func=print_license)

    args = parser.parse_args()

    if args.debug:
        utils.DEBUG_LEVEL = args.debug

    args.func(args)

def search_for_module(args):
    # enable all by default
    if not args.bug and not args.debian and not args.repository:
        args.bug = True
        args.debian = True
        args.repository = True
    node_module = get_npm2deb_instance(args).name
    if args.debian:
        print("\nLooking for similiar package:")
        print("  %s" % utils.get_debian_package(node_module))
    if args.repository:
        print("")
        helper.search_for_repository(node_module)
    if args.bug:
        print("")
        helper.search_for_bug(node_module)
    print("")

def print_itp(args):
    get_npm2deb_instance(args).show_itp()

def print_license(args, prefix=""):
    if args.list:
        print("%s Available licenses are: %s." % \
                (prefix, ', '.join(sorted(templates.LICENSES.keys())).lower()))
    else:
        if args.name is None:
            print("You have to specify a license name")
            args.list = True
            print_license(args)
        else:
            template_license = utils.get_license(args.name)
            if not template_license.startswith('FIX_ME'):
                print(template_license)
            else:
                print("Wrong license name.")
                args.list = True
                print_license(args)

def show_dependencies(args):
    # enable all by default
    if not args.binary and not args.builddeb:
        args.binary = True
        args.builddeb = True

    module_name = get_npm2deb_instance(args).name

    if args.builddeb:
        print "Build dependencies:"
        helper.print_formatted_dependency("NPM", "Debian")
        dep = helper.search_for_builddep(module_name)
        if not dep:
            print("Module %s has no build dependencies." % module_name)
        print("")

    if args.binary:
        print "Dependencies:"
        helper.print_formatted_dependency("NPM", "Debian")
        dep = helper.search_for_dependencies(module_name,
            args.recursive, args.force)
        if not dep:
            print("Module %s has no dependencies." % module_name)
        print("")

def show_reverse_dependencies(args):
    node_module = get_npm2deb_instance(args).name
    helper.search_for_reverse_dependencies(node_module)

def create(args):
    npm2deb = get_npm2deb_instance(args)
    saved_path = os.getcwd()
    utils.create_dir(npm2deb.name)
    utils.change_dir(npm2deb.name)
    npm2deb.start()

    utils.change_dir(saved_path)

    debian_path = "%s/%s/debian" % (npm2deb.name, npm2deb.debian_name)

    print("""
This is not a crystal ball, so please take a look at auto-generated files.\n
You may want fix first these issues:\n""")
    call('/bin/grep --color=auto FIX_ME -r %s/*' % debian_path, shell=True)
    print ("\nUse uscan to get orig source files. Fix debian/watch and then run\
            \n\n$ uscan --download-current-version\n")


def check_module_name(args):
    if not args.node_module or len(args.node_module) is 0:
        print('please specify a node_module.')
        exit(1)
    return args.node_module

def get_npm2deb_instance(args):
    node_module = check_module_name(args)
    return Npm2Deb(node_module, vars(args))


if __name__ == '__main__':
    main()
