from unittest import TestCase
from sudoku import Sudoku
from plugins.nakedN import nakedTriple

class NakedTriple(TestCase):
    def test_nakedTriple(self):
        nakedTriplePuzzle = Sudoku("000056789"+"0"*72)
        nakedTriplePuzzle.initialiseIntersections()
        nakedTriplePuzzle.solvingCandidatesDict[1] = set([1,2,3])
        nakedTriplePuzzle.solvingCandidatesDict[2] = set([1,2,3])
        nakedTriplePuzzle.solvingCandidatesDict[3] = set([1,2,3])
        nakedTriple().solve(nakedTriplePuzzle)

        self.assertEquals(nakedTriplePuzzle.allSolvingCandidates(1), set([1,2,3]))
        self.assertEquals(nakedTriplePuzzle.allSolvingCandidates(2), set([1,2,3]))
        self.assertEquals(nakedTriplePuzzle.allSolvingCandidates(3), set([1,2,3]))
        self.assertEquals(nakedTriplePuzzle.allSolvingCandidates(4), set([4]))