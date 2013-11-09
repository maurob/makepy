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


def noempty(it):
    """ Return a list with only the elements from *it* with a len > 0 """
    return [e for e in it if len(e) > 0]


def sjoin(*args):
    """ Join with a space the no empty elements in *args* """
    return ' '.join(noempty(args))


def compile_cmd(path_name, extra=''):
    """ Return the command line for creating a `.o` from a `.cpp` """
    return sjoin(CXX, compile_extra, extra, '-c', path_name)


def link_cmd(name, objs=[], path='', extra=''):
    """
    Return the command line for creating a executable from the `.o` file list
    """
    path_name = os.path.join(path, name)
    return sjoin(CXX, link_extra, extra, '-o', path_name, *objs)

class Include(object):
    """ Container for the included file name and in which line it was """
    def __init__(self, file_name='', line_number=0):
        self.file_name = file_name
        self.line_number = line_number
    
    def __repr__(self):
        return '<"{file_name}" included in line {line_number}>'.format(
            **self.__dict__)


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



def find_includes(file):
    """
    Return the list of included files in *file* and the line number where finded 
    *file* must be a readable Python file object
    """
    includes = []
    text = comment_remover(file.read())
    for n, line in enumerate(text.splitlines()):
        
        if '#include' in line:
            i = line.index('#include') + len('#include')
            part = line[i:].strip()
            try:
                include_file_name = part.split('"')[1]
                includes.append(Include(include_file_name, n+1))
            except IndexError:
                pass
    return includes


def find_related_sources(includes, source, path, exts=source_exts):
    """
    Check wheather the includes files exist
    otherwise raise an IOError exception
    """
    sources = []
    for include in includes:
        path_include = os.path.join(path, include.file_name)
        if not os.path.isfile(path_include):
            path_source = os.path.join(path, source)
            raise IOError(
                '[Error] File not found: {0} included from {1}:{2}'.format(
                    include.file_name, path_source, include.line_number))
        else:
            name, ext = os.path.splitext(include.file_name)
            for ext in exts:
                path_name = os.path.join(path, name+ext)
                if os.path.isfile(path_name):
                    sources.append(path_name)
    return sources
            
                                  

def dependencies(source_name):
    path, filename = os.path.split(source_name)
    name, ext = os.path.splitext(filename)

    try:
        file = open(source_name)
    except IOError:
        raise IOError('[Error] File not found: {0}'.format(source_name))

    includes = find_includes(open(filename))
    sources = set(find_related_sources(includes, filename, path))
    if len(sources) > 0:
        for source in list(sources)+[inc.file_name for inc in includes]:
            inc, src = dependencies(source)
            [sources.add(s) for s in src]
    
    return includes, sources

def compile(source_name):
    """
    Automatic compile de *source_name* file and its dependencies
    *source_name* is a .cpp/.cc source file name
    """
    path, filename = os.path.split(source_name)
    name, ext = os.path.splitext(filename)

    includes, sources = dependencies(source_name)

    if len(sources) > 0: # Compile and link
        sources.add(source_name)
        objs = [os.path.splitext(s)[0]+'.o' for s in sources]
        for source in sources:
            print compile_cmd(source)
            if source != source_name:
                pass#compile_obj(source)
        print link_cmd(name, objs, path)

    else: # Compile into the executable
        print link_cmd(name, [source_name], path)

    print includes
    
    
