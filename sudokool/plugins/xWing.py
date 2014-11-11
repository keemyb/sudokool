from sudokool.plugin import Plugin

class xWing(Plugin):
    '''X-Wing

    An X-Wing is a group of 4 locations arranged in a rectangle that share a
    common candidate. The X-Wing candidate must also not be found anywhere else
    in either it's rows or columns. If found the X-Wing candidate will be
    removed from the locations in the plane (row or column) where they are found.
    '''

    def __init__(self):
        self.name = "X-Wing"
        self.minSize = None
        self.maxSize = None
        self.rank = 120
        self.xWingGroups = []

    def solve(self, puzzle):
        self.generateXWingGroups(puzzle)

        successString = "X-Wing: {0} has been removed from {1}, as it is in alignment with the X-Wing, {2}"

        from collections import defaultdict

        # creating a dictionary, where the keys are the X-Wing locations, and
        # the values are a list of candidates. The reason for this is that a
        # single X-Wing formation may have many candidates, so it is more
        # efficient to find all candidates applicable to a formation at once.
        xWings = defaultdict(list)

        for group in self.xWingGroups:

            commonXWingCandidates = puzzle.commonSolvingCandidates(*group)

            if len(commonXWingCandidates) == 0:
                continue

            rowCandidates = (puzzle.allSolvingCandidates(*puzzle.rowNeighbours(group[0], *group)) |
                             puzzle.allSolvingCandidates(*puzzle.rowNeighbours(group[2], *group)))
            columnCandidates = (puzzle.allSolvingCandidates(*puzzle.columnNeighbours(group[0], *group)) |
                                puzzle.allSolvingCandidates(*puzzle.columnNeighbours(group[1], *group)))

            for candidate in commonXWingCandidates:
                if (candidate not in rowCandidates or candidate not in columnCandidates):
                    xWings[group].append(candidate)

        for group, candidates in xWings.iteritems():

            for location in self.xWingNeighbours(puzzle, group):

                removedCandidates = puzzle.removeSolvingCandidates(location, *candidates)

                if removedCandidates:

                    # Needs to be more verbose, showing where the alignment occours
                    puzzle.addToLog(successString, removedCandidates, location, group)

    def generateXWingGroups(self, puzzle):
        if self.xWingGroups:
            return

        for firstRowIndex, firstRow in enumerate(puzzle.intersectionTypes["row"]):
            if len(firstRow) < 2:
                continue

            for firstRowGroup in puzzle.nLocations(firstRow, 2):

                    # We use the first row index so that we only find X-Wings
                    # were the second row is below the first. This prevents us
                    # finding duplicate formations.
                    for secondRow in puzzle.intersectionTypes["row"][firstRowIndex + 1:]:
                        if len(secondRow) < 2:
                            continue

                        for secondRowGroup in puzzle.nLocations(secondRow, 2):
                                # if the top left and bottom right locations
                                # are in the same subGrid, the other two
                                # locations are as well and this is not a valid
                                # X-Wing formation. 
                                if "subGrid" in puzzle.alignment(firstRowGroup[0], secondRowGroup[1]):
                                    continue

                                # if the first and second locations from both
                                # rows share the same column, we have found a
                                # rectangular shape. 
                                if "column" in puzzle.alignment(firstRowGroup[0], secondRowGroup[0]) and \
                                   "column" in puzzle.alignment(firstRowGroup[1], secondRowGroup[1]):
                                    self.xWingGroups.append((firstRowGroup + secondRowGroup))

    def cleanup(self, puzzle):
        if not self.xWingGroups:
            return

        for group in self.xWingGroups:
            for location in group:
                if puzzle.isEmpty(location):
                    continue
                if location not in group:
                    continue
                if group in self.xWingGroups:
                    self.xWingGroups.remove(group)

    def xWingNeighbours(self, puzzle, xWing):
        return (puzzle.rowNeighbours(xWing[0], *xWing) +
                puzzle.rowNeighbours(xWing[2], *xWing) +
                puzzle.columnNeighbours(xWing[0], *xWing) +
                puzzle.columnNeighbours(xWing[1], *xWing))
