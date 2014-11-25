from sudoku import Sudoku
from puzzleSummary import puzzleSummary

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

def visualizeEdges(puzzle):
    string = ""
    vPipe = "="
    hPipe = "="
    # first line to accommodate vertical pipe and following spaces (minus one to account for last v pipe)
    # second line for numbers (and following spaces)
    horizontalDivider = (hPipe * ((len(vPipe) + 1) * (puzzle.subGridsX + 1) - 1) +
                   hPipe * (puzzle.gridSize * 2) +
                   "\n")

    def isFirstLocationOnLine(location):
        if (location - 1) % (puzzle.gridSize * puzzle.subGridsX) == 0:
            return True
        return False

    def isFirstLocationInRowInSubGrid(location):
        if (location - 1) % puzzle.subGridsY == 0:
            return True
        return False

    def isLastLocationInRow(location):
        if location % puzzle.gridSize == 0:
            return True
        return False

    def isLastLocation(location):
        if location == puzzle.gridSize ** 2:
            return True
        return False

    edges = puzzle.edges

    for location in puzzle.locations():

        if isFirstLocationOnLine(location):
            string += horizontalDivider

        if isFirstLocationInRowInSubGrid(location):
            string += vPipe + " "

        if edges[location] == (False,)*4:
            cornerLocation = 5
        elif edges[location][0] and edges[location][1]:
            cornerLocation = 9
        elif edges[location][1] and edges[location][2]:
            cornerLocation = 3
        elif edges[location][2] and edges[location][3]:
            cornerLocation = 1
        elif edges[location][3] and edges[location][0]:
            cornerLocation = 7
        elif edges[location][0]:
            cornerLocation = 8
        elif edges[location][1]:
            cornerLocation = 6
        elif edges[location][2]:
            cornerLocation = 2
        elif edges[location][3]:
            cornerLocation = 4

        string += str(cornerLocation) + " "

        if isLastLocationInRow(location):
            string += vPipe + "\n"

        if isLastLocation(location):
            string += horizontalDivider

    return string

easy = Sudoku(size=9)
print easy
print len(easy.undoStack)

# easy.setValue(1,1)
# print easy
# easy.undo()
# print easy
# easy.setValue(2,1)
# print easy.redoStack
# easy.redo()
# print easy
# print easy.undoStack
# print easy.redoStack

# blank = Sudoku(size=9)
# print blank
# print blank.history

# with open("newfile.txt", "w") as results:
#     for i in xrange(5):
#         newPuzzle = Sudoku(size=9,)# difficulty=0.25)
#         results.write(str(i + 1)+"\n")
#         results.write(str(newPuzzle))
#         valuesString = "".join([str(newPuzzle.getValue(location)) if newPuzzle.isFilled(location) else "0" for location in newPuzzle.locations()])
#         results.write(str(valuesString)+"\n")
#         newPuzzle.solve()
#         results.write(str(newPuzzle))
#         results.write(str(newPuzzle.log))
#         results.write("\n"*3)


# blank.solve()
# print blank
# print blank.log
# blank.solve()
# print blank
# print blank
# print blank.log
# blank = Sudoku(size=8)
# # print blank.generateMask()
# blank.solve(forceSolveOnFail=True)
# print blank

# for puzzleNo in [6,7,42,47,48,49,50]:
# # for puzzleNo in xrange(5,11):
# # for puzzleNo in xrange(1,51):
#     print fromTextPuzzleSummary("easy50.txt", "========\n", 0, puzzleNo, True, True, True, True, True, True)
#     print

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

# easy = Sudoku(string16)
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
