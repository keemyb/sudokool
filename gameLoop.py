from sudoku import sudoku

def gameLoop(puzzle):
        print puzzle
        while sum([1 for value in puzzle.values.itervalues() if value != 0]) < (puzzle.gridSize ** 2):
                try:
                        location = int(raw_input("What location do you want to modify? "))
                        if puzzle.values[location] != 0:
                                continue
                except:
                        continue
                else:
                        try:
                                value = int(raw_input("What value do you want to place in location " + str(location) + "? "))
                        except:
                                continue
                        if value in puzzle.setOfPossibleNumbers:
                                puzzle.values[location] = value
                                print puzzle
                                print
        if puzzle.isValid:
                print "Puzzle Completed"
string9 = "003020600\
900305001\
001806400\
008102900\
700000008\
006708200\
002609500\
800203009\
005010300"

puzzle9 = sudoku(9,3,3,string9)
puzzle9.nakedSingle()
puzzle9.hiddenSingle()
puzzle9.nakedSingle()
puzzle9.hiddenSingle()
puzzle9.nakedSingle()
puzzle9.hiddenSingle()


gameLoop(puzzle9)
