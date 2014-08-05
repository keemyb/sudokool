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

string9 = "010030000\
900000104\
500001020\
000400063\
050010090\
280003000\
060100009\
307000006\
000060040"

string9 = "006200000\
000900150\
502740060\
308004005\
007030000\
000090003\
080000000\
000076800\
610000900"

hiddenTripleTestString = "528600049\
136490025\
794205630\
000100200\
007826300\
002509060\
240300976\
809702413\
070904582"

hiddenTripleTestString = "370408100\
000903704\
940100083\
420000005\
000504000\
800000046\
010049000\
509600400\
004200931"

hiddenTripleTest = Sudoku(hiddenTripleTestString)

# string8 = "1004200006000705005008006800100000060052004006008060007000073006"

# string6 = "020000000020054100100064200043300010"
# ##string6 = "123456123456123456123456123456123456"

# puzzle9 = Sudoku(string9)

# puzzle8 = Sudoku(string8)

# puzzle6 = Sudoku(string6)
# puzzle6 = Sudoku("0" * 36)

# for puzzleNo in [6,7,42,47,48,49,50]:
# for puzzleNo in xrange(1,51):
#     print fromTextPuzzleSummary("easy50.txt", "========\n", 0, puzzleNo, True, True, True, True, True, True)

blankPuz = Sudoku("0" * 81)
xWingTest = Sudoku("100000569492056108056109240009640801064010000218035604040500016905061402621000005")
print xWingTest
print xWingTest.values
print xWingTest.setOfPossibleValues

# print puzzleSummary(xWingTest, 0, True, True, True)

string16 = "B07805E0300AD0CG\
004007000C0FA002\
A000000000043700\
0050009F00000008\
0400B8000E079300\
00E37C0000FDB004\
9F07005D03000080\
500D0F3024A8C0G0\
08000000B0000GD5\
00D000000800F0E0\
00A090F0067000BC\
000C0AB0000E7240\
7A090B1000500630\
D0CEF070A0000800\
0000E0A00D005000\
0635G9C00B00E000"

puzzle16 = Sudoku(string16)
print puzzle16
print puzzle16.gridSize
print puzzle16.setOfPossibleValues
print puzzle16.values[16]
print puzzleSummary(puzzle16, 0, True, True, True)

hard = Sudoku("4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......")
print puzzleSummary(hard, 0, True, True, True)