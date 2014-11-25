from sudokool.plugin import Plugin

class swordfish(Plugin):
    '''Swordfish

    A regular swordfish is a group of 9 locations arranged such that there are
    3 rows and 3 columns, each containing 3 locations. These locations must
    A regular swordfish contains 9 locations, 3 in each row and column.
    If candidate the swordfish has in common does not appear in any of the
    swordfish columns, that candidate can be removed from every other location
    in it's rows, and vice versa.

    A regular               Another               One More
    Swordfish pattern       Swordfish pattern     Swordfish pattern
    # # #                   # #                   # #
    # # #                   #   #                 #   #
    # # #                     # #                 # # #

    Note the swordfish pattern on the middle and right. They are still valid
    configurations as they cover 3 rows and 3 columns. The below implementation
    can only find regular swordfishes and those like the middle one where there
    are two locations in every row and column.
    '''

    def __init__(self):
        self.name = "Swordfish"
        self.minSize = None
        self.maxSize = None
        self.rank = 130
        self.swordfishGroups = []

    def solve(self, puzzle):
        self.generateSwordfishGroups(puzzle)

        successString = "Swordfish: {0} has been removed from {1}, as it is in alignment with the Swordfish, {2}"

        from collections import defaultdict

        swordfishes = defaultdict(list)

        for group in self.swordfishGroups:

            commonCandidates = puzzle.commonSolvingCandidates(*group)

            if len(commonCandidates) == 0:
                continue

            rowCandidates = defaultdict(set)
            for neighbour in self.swordfishRowNeighbours(puzzle, group):
                rowCandidates[puzzle.getRow(neighbour)].union(puzzle.allSolvingCandidates(neighbour))

            columnCandidates = defaultdict(set)
            for neighbour in self.swordfishColumnNeighbours(puzzle, group):
                columnCandidates[puzzle.getColumn(neighbour)].union(puzzle.allSolvingCandidates(neighbour))

            for candidate in commonCandidates:
                inAllRows = all(candidate in candidates for candidates in rowCandidates.itervalues())
                inAllColumns = all(candidate in candidates for candidates in columnCandidates.itervalues())
                notInRows = not any(candidate in candidates for candidates in rowCandidates.itervalues())
                notInColumns = not any(candidate in candidates for candidates in columnCandidates.itervalues())

                if (inAllRows and notInColumns) or (inAllColumns and notInRows):
                    swordfishes[group].append(candidate)

        for group, candidates in swordfishes.iteritems():
            neighbours = self.swordfishNeighbours(puzzle, group)

            for location in neighbours:

                removedCandidates = puzzle.removeSolvingCandidates(location, *candidates)

                if removedCandidates:
                    puzzle.addToLog(successString, removedCandidates, location, group)

    def cleanup(self, puzzle):
        if not self.swordfishGroups:
            return

        for group in self.swordfishGroups:
            for location in group:
                if puzzle.isEmpty(location):
                    continue
                if location not in group:
                    continue
                if group in self.swordfishGroups:
                    self.swordfishGroups.remove(group)

    def generateSwordfishGroups(self, puzzle):
        if self.swordfishGroups:
            return

        self.swordfishGroups = (self.generate2SwordfishGroups(puzzle) +
                                self.generate3SwordfishGroups(puzzle))

    def generate2SwordfishGroups(self, puzzle):

        swordfishGroups = []

        # 2 location per line swordfish
        for firstRowIndex, firstRow in enumerate(puzzle.intersectionTypes["row"][:-3]):
            if len(firstRow) < 2:
                continue

            for firstRowGroup in puzzle.nLocations(firstRow, 2):

                for secondRowIndex, secondRow in enumerate(puzzle.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 2:
                        continue

                    for secondRowGroup in puzzle.nLocations(secondRow, 2):
                        alignments = 0

                        for locationOne in firstRowGroup:
                            for locationTwo in secondRowGroup:
                                if "column" in puzzle.alignment(locationOne, locationTwo):
                                    alignments += 1
                                    locationsInSameColumn = (locationOne, locationTwo)

                        if alignments != 1:
                            continue

                        for thirdRow in puzzle.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 2:
                                continue

                            for thirdRowGroup in puzzle.nLocations(thirdRow, 2):
                                alignments2 = 0

                                for locationOne in thirdRowGroup:
                                    for row in (firstRowGroup, secondRowGroup):
                                        for locationTwo in [location for location in row if location not in locationsInSameColumn]:
                                            if "column" in puzzle.alignment(locationOne, locationTwo):
                                                alignments2 += 1

                                if alignments2 == 2:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups

    def generate3SwordfishGroups(self, puzzle):

        swordfishGroups = []

        # 3 location per line swordfish
        for firstRowIndex, firstRow in enumerate(puzzle.intersectionTypes["row"][:-3]):
            if len(firstRow) < 3:
                continue

            for firstRowGroup in puzzle.nLocations(firstRow, 3):

                for secondRowIndex, secondRow in enumerate(puzzle.intersectionTypes["row"][firstRowIndex + 1:-2]):
                    if len(secondRow) < 3:
                        continue

                    for secondRowGroup in puzzle.nLocations(secondRow, 3):
                        alignments = 0

                        for i in xrange(3):
                            if "column" in puzzle.alignment(firstRowGroup[i], secondRowGroup[i]):
                                    alignments += 1

                        if alignments != 3:
                            continue

                        for thirdRow in puzzle.intersectionTypes["row"][firstRowIndex + secondRowIndex + 2:]:
                            if len(thirdRow) < 3:
                                continue

                            for thirdRowGroup in puzzle.nLocations(thirdRow, 3):
                                alignments2 = 0

                                for i in xrange(3):
                                    if "column" in puzzle.alignment(firstRowGroup[i], thirdRowGroup[i]):
                                        alignments2 += 1

                                if alignments2 == 3:
                                    swordfishGroups.append(firstRowGroup + secondRowGroup + thirdRowGroup)

        return swordfishGroups

    def swordfishRowNeighbours(self, puzzle, swordfish):

        rowNeighbours = set([]).union(*[puzzle.rowNeighbours(location) for location in swordfish])

        rowNeighbours -= set(swordfish)

        return rowNeighbours

    def swordfishColumnNeighbours(self, puzzle, swordfish):

        columnNeighbours = set([]).union(*[puzzle.columnNeighbours(location) for location in swordfish])

        columnNeighbours -= set(swordfish)

        return columnNeighbours

    def swordfishNeighbours(self, puzzle, swordfish):

        return self.swordfishRowNeighbours(puzzle, swordfish).union(
            self.swordfishColumnNeighbours(puzzle, swordfish))
