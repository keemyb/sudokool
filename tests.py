from sudoku import Sudoku
from solver import puzzleSummary

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

def visualizer(puzzle, *groups):
    wholeString = ""
    
    for group in groups:
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

        wholeString += string

    return wholeString

hiddenTripleTestString = "370408100\
000903704\
940100083\
420000005\
000504000\
800000046\
010049000\
509600400\
004200931"


conjugatePairString = "007003600039000800020010050040100300000367000003008060090070020004000130008600900"
conjugatePairPuzzle = Sudoku(conjugatePairString)
conjugatePairPuzzle.initialiseIntersections()

conjugatePairPuzzle.candidates[1] = set([1, 4, 5])
conjugatePairPuzzle.candidates[2] = set([1, 5])
conjugatePairPuzzle.candidates[4] = set([2, 5])
conjugatePairPuzzle.candidates[8] = set([1, 4, 9])
conjugatePairPuzzle.candidates[9] = set([1, 2, 4, 9])
conjugatePairPuzzle.candidates[10] = set([1, 4, 5])
conjugatePairPuzzle.candidates[14] = set([2, 5])
conjugatePairPuzzle.candidates[17] = set([1, 4])
conjugatePairPuzzle.candidates[18] = set([1, 2, 4])
conjugatePairPuzzle.candidates[30] = set([2, 5])
conjugatePairPuzzle.candidates[33] = set([2, 5])
conjugatePairPuzzle.candidates[37] = set([1, 5, 9])
conjugatePairPuzzle.candidates[39] = set([1, 2])
conjugatePairPuzzle.candidates[43] = set([2, 4, 5])
conjugatePairPuzzle.candidates[44] = set([1, 4, 9])
conjugatePairPuzzle.candidates[45] = set([1, 4, 5, 9])
conjugatePairPuzzle.candidates[46] = set([1, 9])
conjugatePairPuzzle.candidates[49] = set([2, 5])
conjugatePairPuzzle.candidates[52] = set([2, 5])
conjugatePairPuzzle.candidates[54] = set([1, 9])
conjugatePairPuzzle.candidates[57] = set([1, 5])
conjugatePairPuzzle.candidates[60] = set([1, 4])
conjugatePairPuzzle.candidates[61] = set([4, 5])
conjugatePairPuzzle.candidates[68] = set([2, 5])
conjugatePairPuzzle.candidates[69] = set([2, 5])
conjugatePairPuzzle.candidates[74] = set([1, 5])
conjugatePairPuzzle.candidates[78] = set([1, 4])
conjugatePairPuzzle.candidates[81] = set([4, 5])

print conjugatePairPuzzle.generateConjugatePairs()

# for chainGroup in conjugatePairPuzzle.generateChains():
#     print visualizer(conjugatePairPuzzle, chainGroup[0]), chainGroup[1]

# print puzzleSummary(conjugatePairPuzzle, 0, True, True, True)

# for puzzleNo in [6,7,42,47,48,49,50]:
# for puzzleNo in xrange(1,51):
#     print fromTextPuzzleSummary("easy50.txt", "========\n", 0, puzzleNo, True, True, True, True, True, True)

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

# fileToRead = open("top95.txt", "r")
# number = 1
# for line in fileToRead:
#     try:
#         puzzle = Sudoku(str(line)[:81])
#         print puzzleSummary(puzzle, 0, True, True, True, number)
#     except:
#         continue
#     else:
#         number += 1

