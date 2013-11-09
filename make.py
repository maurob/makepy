# -*- coding: utf-8 -*-

"""
Command line for a C++ automatic compiler
"""

from compile import compile

def main():
    from sys import argv
    if len(argv) >= 2:
        try:
            compile(argv[1])
        except IOError, e:
            print e
    else:
        print 'usage: {0} file.cpp'.format(*argv)

if __name__ == '__main__':
    main()
