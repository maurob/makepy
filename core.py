# -*- coding: utf-8 -*-

"""
Core module for the automatic C++ builder

TODO:
* Comprobar que el compilador terminó correctamente
"""
__author__ = 'Mauro Bruni'

import os
from os import system
import re
import time

CXX = 'g++'
source_exts = ['.cpp', '.cc', '.c']
header_exts = ['.h', '.hpp']

compile_extra = ''
link_extra = ''

PATH = [
    ]


class File(object):
    """ File name and path helper """
    def __init__(self, full):
        """ *full* is the complete file name with optional path """
        self.full = os.path.normpath(full)
        self.path, self.filename = os.path.split(self.full)
        self.name, self.ext = os.path.splitext(self.filename)
        self.path_name = os.path.join(self.path, self.name)
        self.name_ext = self.name + self.ext

    def __repr__(self):
        return self.full

    def __eq__(self, other):
        return self.full == other.full

    def __len__(self):
        return len(self.full)

    def getmtime(self):
        return os.path.getmtime(self.full)

    def to_obj(self):
        """
        Return a `.o` version of this file
        """
        return File(self.path_name + '.o')

    def recursive_includes(self):
        """
        Recursively find the include files starting in this file
        """
        includes = find_includes(self)
        for include_file in includes:
            includes += include_file.recursive_includes()
        return includes

    def need_to_by_compiled(self):
        """
        Return True if this file or any included file from it has a newer
        modification time than its related obj file or if the latter
        doesn't exists
        """
        obj_file = self.to_obj()
        try:
            obj_file_mtime = obj_file.getmtime()
        except OSError:
            return True

        for file in [self] + self.recursive_includes():
            if file.getmtime() > obj_file_mtime:
                return True
        return False

    def related_sources(self):
        """
        Return a list of source files related to the included files
        """
        return find_related_sources(self.recursive_includes())


def noempty(it):
    """ Return a list with only the elements from *it* with a len > 0 """
    return [e for e in it if len(e) > 0]


def sjoin(*args):
    """ Join with a space the no empty elements in *args* """
    return ' '.join(noempty(args))


def compile_cmd(file, extra=''):
    """ Return the command line for creating a `.o` from a `.cpp` """
    return sjoin(CXX, compile_extra, extra, '-o', file.path_name+'.o', 
                 '-c', file.full)


def link_cmd(path_name, objs=[], extra=''):
    """
    Return the command line for creating a executable from the `.o` file
    list
    """
    return sjoin(CXX, link_extra, extra, '-o', path_name, *objs)


def comment_remover(text):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return ""
        else:
            return s
    pattern = re.compile(
        r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
        re.DOTALL | re.MULTILINE
    )
    return re.sub(pattern, replacer, text)


def find_file(file, path='.'):
    """
    Find the first ocurrence of *file* starting the search in path and
    then in each path in PATH list.
    Return the new path in a File instance
    *file* is also a File instance
    """
    for path in [path]+PATH:
        path_file = os.path.join(path, file.full)
        if os.path.isfile(path_file):
            return File(path_file)
    raise IOError('[Error] file not found in PATH: '+file.full)
    
def find_includes(actual):
    """
    Return the list of included files in *file* and the line number where
    finded 
    *file* must be a readable Python file object
    """
    includes = []
    text = comment_remover(open(actual.full).read())
    for n, line in enumerate(text.splitlines()):
        
        if '#include' in line:
            i = line.index('#include') + len('#include')
            part = line[i:].strip()
            try:
                include_file = File(part.split('"')[1])
                include_file = find_file(include_file, actual.path)
                includes.append(include_file)
            except IndexError:
                pass
            except IOError, e:
                print str(e) + ' included from {0}:{1}'.format(actual.full,
                                                               n+1)
    return includes


def find_related_sources(includes, exts=source_exts):
    """
    Return the related source to the includes, if exist.
    """
    sources = []
    for include in includes:
        for ext in exts:
            path_name = include.path_name + ext
            if os.path.isfile(path_name):
                src = File(path_name)
                sources.append(src)
                include.related_source = src
    return sources


def build(source_name):
    """
    Automatic build de *source_name* file and its dependencies
    *source_name* is a .cpp/.cc source file name
    """
    main_source = File(source_name)
    any_new_obj = False
    objs = []

    from process import MultiProcess
    compilation_process = MultiProcess()

    for source in [main_source] + main_source.related_sources():
        obj_file = source.to_obj()
        objs.append(obj_file.full)
        
        if source.need_to_by_compiled():
            compilation_process.add(compile_cmd(source))
            any_new_obj = True

    if any_new_obj:
        compilation_process.wait()
        link_process = MultiProcess()
        link_process.add(link_cmd(main_source.path_name, objs))
        link_process.wait()
    else:
        print 'No need for rebuild (no changes)'
    
    
