import unittest
import core
from core import (find_file, File, find_includes, find_related_sources, 
                   dependencies)
import multicore

class CoreTest(unittest.TestCase):

    def setUp(self):
        core.PATH = []
    
    def test_File(self):
        """ Test File class """
        f = File('../test/../test/main.cpp')
        self.assertEqual(str(f), '../test/main.cpp')
        self.assertEqual(f.full, '../test/main.cpp')
        self.assertEqual(f.path, '../test')
        self.assertEqual(f.name, 'main')
        self.assertEqual(f.ext, '.cpp')
        self.assertEqual(f.path_name, '../test/main')
        self.assertEqual(f.name_ext, 'main.cpp')

    def test_find_file(self):
        core.PATH.append('test')
        core.PATH.append('test/sub')
        self.assertEqual(find_file(File('a.txt')).full, 'test/a.txt')
        self.assertEqual(find_file(File('b.txt')).full, 'test/sub/b.txt')

    def test_find_file_path(self):
        self.assertEqual(find_file(File('a.txt'), 'test').full, 'test/a.txt')
        self.assertRaises(IOError, find_file, File('notfound.txt'))

    def test_find_includes(self):
        actual = File('test/main.cpp')
        includes = find_includes(actual)
        inc = includes[0]
        self.assertEqual(inc.name_ext, 'pepe.h')

    def test_find_related_sources(self):
        includes = [File(f) for f in ['test/pepe.h', 'test/otro.h']]
        sources = find_related_sources(includes)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].full, 'test/pepe.cpp')
        
    def test_dependencies(self):
        f = File('test/main.cpp')
        dependencies(f)
        print f
        print f.includes
        print f.sources
        self.assertEqual(len(f.includes), 2)
        self.assertEqual(len(f.sources), 1)
        self.assertEqual(f.includes[0].full, 'test/pepe.h')
        self.assertEqual(f.includes[1].full, 'test/otro.h')
        self.assertEqual(f.sources[0].full, 'test/pepe.cpp')


class MulticoreTest(unittest.TestCase):

    def test_one_process(self):
        m = multicore.Multicore()
        print len(m)
        #m.shell('ls', stdout='pepe.stdout')
        #m.wait_all()


if __name__ == '__main__':
    unittest.main()
