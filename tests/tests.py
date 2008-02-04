import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from FSA import *

class TestFSA(unittest.TestCase):
    def setUp(self):
        pass
    
    def testshuffle(self):
        fsa = compileRE('a*')
        #self.assertEqual(self.seq, range(10))

if __name__ == '__main__':
    unittest.main()
