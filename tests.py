from sudoku import sudoku

def easy(self):
    
    easy50 = open("easy50.txt", "r")
    stringEasy = ""
    for line in easy50:
        stringEasy += line.strip()
    for i in xrange(50):
        start = (i * 89)
        end = start + 9 * 9 
        stringEasy9 = stringEasy[start : end]
        puzzleEasy9 = sudoku(9,3,3,stringEasy9)

        puzzleEasy9.oneGhostLeft()
        print puzzleEasy9
        print
                                
##puzzleInv = sudoku(9,4,3,string9)
##puzzle8 = sudoku(8,2,4,"")
            
string9 = "030647080709000206010903040301070804800304002402050603080501020103000409020439060"
string6 = "020000000020054100100064200043300010"
##string9 = "100920000524010000000000070050008102000000000402700090060000000000030945000071006"
string9 = "904200007010000000000706500000800090020904060040002000001607000000000030300005702"
puzzle9 = sudoku(9,3,3,string9)

##print puzzle9
##puzzle9.oneGhostLeft()
##print puzzle9

print easy(puzzle9)

puzzle6 = sudoku(6,2,3,string6)
##puzzle6.oneGhostLeft()
##print puzzle6
