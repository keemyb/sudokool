from sudoku import sudoku
from operator import add, or_
from math import sqrt
from copy import deepcopy

def puzzleSummary(puzzle, maxLevel, printPuzzle, breakdown, printGhostValues, no = None):

    preSolved = puzzle
    postSolved = deepcopy(preSolved)

    solveReport = solver(postSolved, maxLevel, breakdown)

    numberOfPreSolvedValues = reduce(add, [1 for value in preSolved.values.itervalues() if value != 0], 0)
    numberOfPostSolvedValues = reduce(add, [1 for value in postSolved.values.itervalues() if value != 0], 0)

    if no == None:
        no = 1

    if printPuzzle:
        printPuzzle = str(preSolved) + "\n" + str(postSolved) + "\n"
    else:
        printPuzzle = ""

    changedGhostsString = ""
    if printGhostValues:
        for key in postSolved.ghostValues.iterkeys():
            if postSolved.ghostValues[key] != preSolved.ghostValues[key]:
                changedGhostsString += "\n" + str(key) + " " + str(preSolved.ghostValues[key]) + " " + str(postSolved.ghostValues[key])

    return str(no) + " " + str(numberOfPreSolvedValues) + " ---> " + str(numberOfPostSolvedValues) + "\n" + str(solveReport[1]) + str(solveReport[2]) + str(changedGhostsString) + "\n" + printPuzzle + "\n" * 2

def fromText(textfile, seperator, maxLevel, n, specific, breakdown, showModified, showSolved, printPuzzle, printGhostValues):
    
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
        results += puzzleSummary(puzzle, maxLevel, printPuzzle, breakdown, printGhostValues)
        no += 1

    return results

def solver(puzzle, maxLevel, breakdown, history = None):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin]

    #puzzle is complete if gridSize ^ 2 values are filled
    if reduce(add, [1 for value in puzzle.values.itervalues() if value != 0], 0) == puzzle.gridSize ** 2:
        if breakdown:
            return False, [entry[0] for entry in history if history != None], [entry[2] for entry in history if history != None]
        else:
            return False, [entry[0] for entry in history if history != None], ""

    if maxLevel > len(methods):
        maxLevel = len(methods)

    #if solver is run for the first time, solve using first method
    if history == None:
        methods[0]()
        if breakdown:
            history = [(0, puzzle.changes, str(puzzle))]
        else:
            history = [(0, puzzle.changes)]
        return solver(puzzle, maxLevel, breakdown, history)
    
    #if last attempt was successful, go back to first level

    lastMethod = history[-1][0]
    if history[-1][1] == True:
        nextMethod = 0
    #or if unsuccessful, increase level or exit if highest level was tried
    else:
        if lastMethod == maxLevel - 1:
            if breakdown:
                return False, [entry[0] for entry in history if history != None], [entry[2] for entry in history if history != None]
            else:
                return False, [entry[0] for entry in history if history != None], ""
        else:
            nextMethod = lastMethod + 1

    methods[nextMethod]()
    if breakdown:
        history.append((nextMethod, puzzle.changes, str(puzzle)))
    else:
        history.append((nextMethod, puzzle.changes))
    
    return solver(puzzle, maxLevel, breakdown, history)

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

string8 = "1004200006000705005008006800100000060052004006008060007000073006"

string6 = "020000000020054100100064200043300010"
##string6 = "123456123456123456123456123456123456"

puzzle9 = sudoku(9,3,3,string9)

puzzle8 = sudoku(8,2,4,string8)

puzzle6 = sudoku(6,2,3,string6)

for puzzle in [puzzle9]:
    print puzzleSummary(puzzle, 3, True, True, True)

# print fromText("easy50.txt", "========\n", 3, 50, True, False, True, True, True, True)