from sudoku import sudoku

def easy(full = True):
    
    easy50 = open("easy50.txt", "r")
    stringEasy = ""
    for line in easy50:
        stringEasy += line.strip()

    results = {}

    for i in xrange(50):
        start = (i * 89)
        end = start + 9 * 9 

        stringEasy9 = stringEasy[start : end]

        start = 81
        for value in stringEasy9:
            if int(value) == 0:
                start -= 1

        puzzleEasy9 = sudoku(9,3,3,stringEasy9)
        if full:
            print
            print str(i + 1) + " ======================"
            print puzzleEasy9
        solver(puzzleEasy9)
        if full:
            print puzzleEasy9
            print puzzleEasy9.ghostValues

        end = 81
        for value in puzzleEasy9.values.itervalues():
            if value == 0:
                end -= 1

        results[i + 1] = [start, end]
    
    print            
    return results

def solver(puzzle):
    methods = [puzzle.nakedSingle, puzzle.hiddenSingle, puzzle.nakedTwin]
    methods = [puzzle.nakedSingle]
    puzzle.changes = True
    while puzzle.changes:
        for method in range(len(methods)):
            methods[method]()
            

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

string8 = "1004200006000705005008006800100000060052004006008060007000073006"

string6 = "020000000020054100100064200043300010"
##string6 = "123456123456123456123456123456123456"

puzzle9 = sudoku(9,3,3,string9)

puzzle8 = sudoku(8,2,4,string8)

puzzle6 = sudoku(6,2,3,string6)

# puzzle9.nakedTwin()
print puzzle9
print puzzle9.ghostValues
print
print puzzle8
print puzzle8.ghostValues
puzzle8.nakedSingle()
print puzzle8
print puzzle8.ghostValues
# puzzle9.populateGhosts()
# print puzzle9.ghostData
# puzzle9.nakedTwin()
# print puzzle9.ghostData
# print puzzle9

print easy(True)
