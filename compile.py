# -*- coding: utf-8 -*-

"""
Compilation module

TODO:
* Comprobar que el compilador terminó correctamente
"""
__author__ = 'Mauro Bruni'

import os
from os import system
import re

CXX = 'g++'
source_exts = ['.cpp', '.cc', '.c']

compile_extra = ''
link_extra = ''

PATH = ['.']


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


def noempty(it):
    """ Return a list with only the elements from *it* with a len > 0 """
    return [e for e in it if len(e) > 0]


def sjoin(*args):
    """ Join with a space the no empty elements in *args* """
    return ' '.join(noempty(args))


def compile_cmd(path_name, extra=''):
    """ Return the command line for creating a `.o` from a `.cpp` """
    return sjoin(CXX, compile_extra, extra, '-c', path_name)


def link_cmd(path_name, objs=[], extra=''):
    """
    Return the command line for creating a executable from the `.o` file list
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
    Find the first ocurrence of *file* starting the search in path and then
    in each path in PATH list.
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
    Return the list of included files in *file* and the line number where finded 
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
                raise IOError(e + 'in {0}:{1}'.format(actual.full, n+1))
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


def dependencies(actual):
    try:
        file = open(actual.full)
    except IOError:
        raise IOError('[Error] File not found: {0}'.format(actual))

    actual.includes = find_includes(actual)
    actual.sources = find_related_sources(actual.includes)
    if len(actual.sources) > 0:
        for file in actual.sources + actual.includes:
            inc, src = dependencies(file)
            for s in src:
                if s not in actual.sources:
                    actual.sources.append(s)
            for i in inc: 
                if i not in actual.includes:
                    actual.includes.append(i)
    
    return actual.includes, actual.sources


def compile(source_name):
    """
    Automatic compile de *source_name* file and its dependencies
    *source_name* is a .cpp/.cc source file name
    """
    actual = File(source_name)
    includes, sources = dependencies(actual)

    print

    if len(sources) > 0: # Compile and link
        #sources.append(actual)
        objs = []
        for source in sources + [actual]:
            obj = source.path_name + '.o'
            objs.append(obj)
            print compile_cmd(obj)
            print 'Sensibility:', [source] + source.includes + source.sources
            print
        print link_cmd(source.path_name, objs)

    else: # Compile into the executable
        print link_cmd(actual.path_name, [actual.full])
        print 'Sensibility:', [actual] + actual.includes + actual.sources
        print
    
    
