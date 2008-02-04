import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from FSA import *

class TestFSA(unittest.TestCase):
    def setUp(self):
        pass
    
    def testsRejects(self):
        fsa = compileRE('a(b|c*)')
        self.assertFalse(fsa.accepts("abbb"))

    def testDeterminization(self):
        states = [0, 1, 2, 3]
        alphabet = ['a']
        transitions = [(0, 1, 'a'),
                       (0, 2, 'a'),
                       (1, 0, 'b'),
                       (1, 3, 'a'),
                       (2, 0, 'a'),
                       (2, 2, 'b'),
                       (2, 3, 'a')]
        initialState = 0
        finalStates = [3]
        fsa = FSA(states, alphabet, transitions, initialState, finalStates)
        self.assertTrue(fsa.accepts('aba'))
        dfa = fsa.determinized()
        self.assertTrue(dfa.accepts('aba'))

    def testMinimization(self):
        fsa = concatenation(singleton("a"),minimize(closure(singleton("b"))))
        self.assertFalse(fsa.accepts("b"))
        fsa = concatenation(singleton("a"),closure(singleton("b")))
        self.assertFalse(fsa.accepts("b"))

if __name__ == '__main__':
    unittest.main()
