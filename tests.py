import unittest
import compile

class CompileTest(unittest.TestCase):

    def setUp(self):
        compile.PATH = ['.']
    
    def test_File(self):
        """ Test File class """
        f = compile.File('../test/../test/main.cpp')
        self.assertEqual(str(f), '../test/main.cpp')
        self.assertEqual(f.full, '../test/main.cpp')
        self.assertEqual(f.path, '../test')
        self.assertEqual(f.name, 'main')
        self.assertEqual(f.ext, '.cpp')
        self.assertEqual(f.path_name, '../test/main')
        self.assertEqual(f.name_ext, 'main.cpp')

    def test_find_file(self):
        from compile import PATH, find_file, File
        PATH.append('test')
        PATH.append('test/sub')
        self.assertEqual(find_file(File('a.txt')).full, 'test/a.txt')
        self.assertEqual(find_file(File('b.txt')).full, 'test/sub/b.txt')

    def test_find_file_path(self):
        from compile import find_file, File
        self.assertEqual(find_file(File('a.txt'), 'test').full, 'test/a.txt')
        self.assertRaises(IOError, find_file, File('notfound.txt'))

    #def test_Include(self):
    #    from compile import Include, File
    #    i = Include(File('a.txt'), 4)
    #    self.assertEqual(str(i), '<"a.txt" included in line 4>')

    def test_find_includes(self):
        from compile import find_includes, File
        actual = File('test/main.cpp')
        includes = find_includes(actual)
        inc = includes[0]
        self.assertEqual(inc.name_ext, 'pepe.h')

    def test_find_related_sources(self):
        from compile import find_related_sources, File
        includes = [File(f) for f in ['test/pepe.h', 'test/otro.h']]
        sources = find_related_sources(includes)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].full, 'test/pepe.cpp')
        
    def test_dependencies(self):
        from compile import dependencies, File
        print dependencies(File('test/main.cpp'))

if __name__ == '__main__':
    unittest.main()
