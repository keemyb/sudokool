from unittest import TestCase
from sudoku import Sudoku
from plugins.nakedSingle import nakedSingle

class NakedSingle(TestCase):
    def test_nakedSingle(self):
        nakedSinglePuzzle = Sudoku("023456789"+"0"*72)
        nakedSinglePuzzle.initialiseIntersections()
        nakedSingle().solve(nakedSinglePuzzle)

        self.assertEquals(nakedSinglePuzzle.getValue(1), 1)