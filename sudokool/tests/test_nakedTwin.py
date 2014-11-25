from unittest import TestCase
from sudoku import Sudoku
from plugins.nakedN import nakedTwin

class NakedTwin(TestCase):
    def test_nakedTwin(self):
        nakedTwinPuzzle = Sudoku("000456789"+"0"*72)
        nakedTwinPuzzle.initialiseIntersections()
        nakedTwinPuzzle.solvingCandidatesDict[1] = set([1,2])
        nakedTwinPuzzle.solvingCandidatesDict[2] = set([1,2])
        nakedTwin().solve(nakedTwinPuzzle)

        self.assertEquals(nakedTwinPuzzle.allSolvingCandidates(1), set([1,2]))
        self.assertEquals(nakedTwinPuzzle.allSolvingCandidates(2), set([1,2]))
        self.assertEquals(nakedTwinPuzzle.allSolvingCandidates(3), set([3]))