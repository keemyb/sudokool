from sudoku import sudoku
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
        gridSize = int(sqrt(len(puzzleString)))
        subGridsX = int(sqrt(gridSize))
        puzzle = sudoku(gridSize, subGridsX, subGridsX, puzzleString)
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
    gridSize = int(sqrt(len(puzzle)))
    subGridsX = int(sqrt(gridSize))
    return sudoku(gridSize, subGridsX, subGridsX, puzzle)

string9 = "030647080709000206010903040301070804800304002402050603080501020103000409020439060"
string9 = "100920000524010000000000070050008102000000000402700090060000000000030945000071006"
##string9 = "904200007010000000000706500000800090020904060040002000001607000000000030300005702"
string9 = "400270600\
798156234\
020840007\
237468951\
849531726\
561792843\
082015479\
070024300\
004087002"
string9 = "003020600\
900305001\
001806400\
008102900\
700000008\
006708200\
002609500\
800203009\
005010300"

string9 = "109700032\
003012549\
060090008\
080001004\
004839200\
200400080\
300070020\
546920100\
720005806"

string8 = "1004200006000705005008006800100000060052004006008060007000073006"

string6 = "020000000020054100100064200043300010"
##string6 = "123456123456123456123456123456123456"

puzzle9 = sudoku(9,3,3,string9)

puzzle8 = sudoku(8,2,4,string8)

puzzle6 = sudoku(6,2,3,string6)

# for puzzleNo in [6,7,42,47,48,49,50]:
#     print fromTextPuzzleSummary("easy50.txt", "========\n", 6, puzzleNo, True, True, True, True, True, True)

print puzzle9

solver(puzzle9, 6)

print puzzle9.isValid()
puzzle9.values[81] = "b"
print puzzle9
print puzzle9.isValid()