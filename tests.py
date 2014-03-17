from sudoku import sudoku

def easy(self):
    
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
            if value == str(0) or int(0):
                start -= 1

        puzzleEasy9 = sudoku(9,3,3,stringEasy9)
        puzzleEasy9.oneGhostLeft()

        end = 81
        for value in puzzleEasy9.data.itervalues():
            if value == str(0) or int(0):
                end -= 1

        results[i + 1] = [start, end]
                
    return results
            
string9 = "030647080709000206010903040301070804800304002402050603080501020103000409020439060"
string9 = "100920000524010000000000070050008102000000000402700090060000000000030945000071006"
string9 = "904200007010000000000706500000800090020904060040002000001607000000000030300005702"

string8 = "1004200006000705005008006800100000060052004006008060007000073006"

string6 = "020000000020054100100064200043300010"
##string6 = "123456123456123456123456123456123456"

puzzle9 = sudoku(9,3,3,string9)

puzzle8 = sudoku(8,2,4,string8)

puzzle6 = sudoku(6,2,3,string6)

##print puzzle9
##puzzle9.oneGhostLeft()
##print puzzle9

##print easy(puzzle9)

##puzzle6.oneGhostLeft()
##print puzzle6

print puzzle6
##puzzle8.populateGhosts()
for i in xrange(36):
    print i + 1, puzzle6.getColumnInSubGrid(i + 1)
