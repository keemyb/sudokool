from sudoku import Sudoku

def play(puzzle):
		print puzzle
		counter = 0
		while sum([1 for value in puzzle.values.itervalues() if value != 0]) < (puzzle.gridSize ** 2):
			if counter > 5:
				return
			
			try:
				location = int(raw_input("What location do you want to modify? "))
				if puzzle.values[location] != 0:
					continue
			except:
				counter += 1
				print "Invalid location"
				continue
			else:
				counter = 0
			
			try:
				value = int(raw_input("What value do you want to place in location " + str(location) + "? "))
			except:
				counter += 1
				print "Invalid value"
				continue
			else:
				counter = 0
			
			if value in puzzle.setOfPossibleNumbers:
				puzzle.values[location] = value
				print puzzle
				print
		
		if puzzle.isValid:
			print "Puzzle Completed"
		else:
			print "Invalid Puzzle"
string9 = "003020600\
900305001\
001806400\
008102900\
700000008\
006708200\
002609500\
800203009\
005010300"

puzzle9 = Sudoku(string9)
puzzle9.nakedSingle()
puzzle9.hiddenSingle()
puzzle9.nakedSingle()
puzzle9.hiddenSingle()
puzzle9.nakedSingle()
puzzle9.hiddenSingle()


play(puzzle9)
