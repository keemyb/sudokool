from sudoku import Sudoku
from solver import puzzleSummary, solver
from math import sqrt

def fromTextPuzzleSummary(textfile, seperator, maxLevel, n, specific, showModified, showSolved, printPuzzle, printGhostValues, printHistory):
    
    fileToRead = open(textfile, "r")
    currentPuzzle = ""
    puzzles = []
    
    for line in fileToRead:
        if len(puzzles) <= n:
            if line == seperator:
                puzzles.append(currentPuzzle)
                currentPuzzle = ""
            else:
                currentPuzzle += line.strip()
    if len(currentPuzzle) == len(puzzles[0]):
        puzzles.append(currentPuzzle)

    if specific:
        puzzles = [puzzles[n - 1]]
        no = n
    else:
        no = 1

    results = ""

    for puzzleString in puzzles:
        puzzle = Sudoku(puzzleString, True)
        results += puzzleSummary(puzzle, maxLevel, printPuzzle, printGhostValues, printHistory, no)
        no += 1

    return results

def fromTextToPuzzle(textfile, seperator, n):
    fileToRead = open(textfile, "r")
    currentPuzzle = ""
    puzzles = []
    
    for line in fileToRead:
        if len(puzzles) <= n:
            if line == seperator:
                puzzles.append(currentPuzzle)
                currentPuzzle = ""
            else:
                currentPuzzle += line.strip()
    if len(currentPuzzle) == len(puzzles[0]):
        puzzles.append(currentPuzzle)

    puzzle = puzzles[n - 1]
    return Sudoku(puzzle, True)

def visualizer(puzzle, group):
    gridSize = puzzle.gridSize
    subGridsX = puzzle.subGridsX
    subGridsY = puzzle.subGridsY
    string = ""
    vPipe = "="
    hPipe = "="
    # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
    # second line for numbers (and following spaces)
    hPipeString = hPipe * ((len(vPipe) + 1) * (subGridsX + 1) - 1) + \
    hPipe * (gridSize * 2) + \
    "\n"

    for position in xrange(1, gridSize ** 2 + 1):

        if (position - 1) % (gridSize * subGridsX) == 0:
            string += hPipeString

        if (position - 1) % subGridsY == 0 :
            string += vPipe + " "

        if position not in group:
            string += "  "
        else:
            string += "0 "

        if position % gridSize == 0:
            string += vPipe + "\n"

        if position == gridSize ** 2:
            string += hPipeString

    return string

hiddenTripleTestString = "370408100\
000903704\
940100083\
420000005\
000504000\
800000046\
010049000\
509600400\
004200931"

# hiddenTripleTest = Sudoku(hiddenTripleTestString)
# hiddenTripleTest.hiddenTriplet()
# print hiddenTripleTest.intersectionTypes

# puzzle8 = Sudoku("1004200006000705005008006800100000060052004006008060007000073006")

# for puzzleNo in [6,7,42,47,48,49,50]:
for puzzleNo in xrange(1,51):
    print fromTextPuzzleSummary("easy50.txt", "========\n", 0, puzzleNo, True, True, True, True, True, True)

# xWingTest = Sudoku("100000569492056108056109240009640801064010000218035604040500016905061402621000005")
# # xWingTest.generateSubGridGroups()
# print puzzleSummary(xWingTest, 0, True, True, True)
# print xWingTest.values

# string16 = "B07805E0300AD0CG\
# 004007000C0FA002\
# A000000000043700\
# 0050009F00000008\
# 0400B8000E079300\
# 00E37C0000FDB004\
# 9F07005D03000080\
# 500D0F3024A8C0G0\
# 08000000B0000GD5\
# 00D000000800F0E0\
# 00A090F0067000BC\
# 000C0AB0000E7240\
# 7A090B1000500630\
# D0CEF070A0000800\
# 0000E0A00D005000\
# 0635G9C00B00E000"

# puzzle16 = Sudoku(string16)
# print puzzleSummary(puzzle16, 0, True, True, True)

# puz = Sudoku("017903600000080000900000507072010430000402070064370250701000065000030000005601720")
# puz.initialiseIntersections()
# puz.ghostValues[67] = set([5, 7, 8])
# print puz.ghostValues[56]
# print puzzleSummary(puz, 0, True, True, True)
# print puz.ghostValues[56]