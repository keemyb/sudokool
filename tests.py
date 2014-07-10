from sudoku import sudoku
from operator import add, or_

def fromText(textfile, n, level, onlyShowSolved, ghostValues = True):
    
    fileToRead = open(textfile, "r")
    currentPuzzle = ""
    puzzles = []
    for line in fileToRead:
        if len(puzzles) < n:
            if line != "========\n":
                currentPuzzle += line.strip()
            else:
                puzzles.append(currentPuzzle)
                currentPuzzle = ""

    results = ""
    no = 1

    for puzzle in puzzles:
        preSolved = sudoku(9,3,3,puzzle)
        postSolved = sudoku(9,3,3,puzzle)

        print solver(postSolved, level)

        numberOfPreSolvedValues = reduce(add, [1 for value in preSolved.values.itervalues() if value != 0], 0)
        numberOfPostSolvedValues = reduce(add, [1 for value in postSolved.values.itervalues() if value != 0], 0)

        changedGhosts = {}
        for key in postSolved.ghostValues.iterkeys():
            if postSolved.ghostValues[key] != preSolved.ghostValues[key]:
                changedGhosts[key] = postSolved.ghostValues[key], preSolved.ghostValues[key]

        results += str(no) + " " + str(numberOfPreSolvedValues) + " " + str(numberOfPostSolvedValues) + " " + str(changedGhosts) + "\n"
        no += 1

    return results

    # for i in xrange(1):
    #     start = (i * 89)
    #     end = start + 9 * 9 

    #     stringEasy9 = stringEasy[start : end]

    #     pre, post = sudoku(9,3,3,stringEasy9), sudoku(9,3,3,stringEasy9)

    #     start = 81
    #     for value in pre.values.itervalues():
    #         if value == 0:
    #             start -= 1

    #     solver(post)
    #     preGhost = {}
    #     postGhost = {}
    #     for key in post.ghostValues.iterkeys():
    #         if post.ghostValues[key] != pre.ghostValues[key]:
    #             preGhost[key] = pre.ghostValues[key]
    #             postGhost[key] = post.ghostValues[key]

    #     fullString = "\n" + str(i + 1) + " ======================" + "\n" + str(pre) + str(preGhost) + "\n" + str(post) + str(postGhost)
    #     liteString = "\n" + str(i + 1) + " ======================" + "\n" + str(pre) + str(post)

    #     if onlyShowSolved:
    #         if pre.ghostValues != post.ghostValues:
    #             if ghostValues:
    #                 print fullString
    #             else:
    #                 print liteString
    #     else:
    #         if ghostValues:
    #             print fullString
    #         else:
    #             print liteString


    #     end = 81
    #     for value in post.values.itervalues():
    #         if value == 0:
    #             end -= 1


    #     results[i + 1] = [start, end]
    
    # print            
    # return results

def solver(puzzle, maxLevel, history = None):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin]

    #puzzle is complete if gridSize ^ 2 values are filled
    if reduce(add, [1 for value in puzzle.values.itervalues() if value != 0], 0) == puzzle.gridSize ** 2:
        return True, [entry[0] for entry in history if history != None]

    if maxLevel > len(methods):
        maxLevel = len(methods)

    #if solver is run for the first time, solve using first method
    if history == None:
        methods[0]()
        history = [(0, puzzle.changes)]
        return solver(puzzle, maxLevel, history)
    
    # #check to see if last couple attempts were all unsuccessful, if so, quit
    # elif len(history) > len(methods):
    #     if reduce(or_, [boolean[1] for boolean in history][-(len(methods)):]) == False:
    #         return False
    
    #if last attempt was successful, go back to first level
    lastMethod = history[-1][0]
    if history[-1][1] == True:
        nextMethod = 0
    #or if unsuccessful, increase level or exit if highest level was tried
    else:
        if lastMethod == maxLevel - 1:
            return False, [entry[0] for entry in history if history != None]
        else:
            nextMethod = lastMethod + 1

    methods[nextMethod]()
    history.append((nextMethod, puzzle.changes))
    return solver(puzzle, maxLevel, history)

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

# for puzzle in [puzzle9, puzzle8]:
#     # puzzle.nakedSingle()
#     # print puzzle
#     # print puzzle.ghostValues
#     # puzzle.nakedTwin()
#     # print puzzle
#     # print puzzle.ghostValues

#     print puzzle
#     print puzzle.ghostValues
#     puzzle.nakedTwin()
#     print puzzle
#     print puzzle.ghostValues

print fromText("easy50.txt", 1, 3, True)
# print fromText("easy50.txt", 50, 1, True) == fromText("easy50.txt", 50, 2, True)