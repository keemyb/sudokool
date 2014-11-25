from sudokool.plugin import Plugin

class xyzWing(Plugin):
    '''XYZ-Wing

    This plugin looks for a group of 3 locations. One location must contain
    only three candidates (X, Y, Z). It must be aligned with two locations,
    one of which contain only (X, Z) and one that only contains (Y, Z).

    Any locations that are aligned in either the same row, column and subGrid
    as all 3 locations cannot contain the candidate Z, so it is removed.
    '''

    def __init__(self):
        self.name = "XYZ-Wing"
        self.minSize = None
        self.maxSize = None
        self.rank = 160
        self.xyzWingGroups = []

    def solve(self, puzzle):
        self.generateXYZWingGroups(puzzle)

        successString = "XYZ-Wing: {0} has been removed from {1}, as it can be seen by {2}, an XYZ-Wing"

        for xyzWingGroup in self.xyzWingGroups:
            xyzWingLocations = xyzWingGroup[0]
            xyzWingCandidate = xyzWingGroup[1]
            pivot = xyzWingLocations[0]
            firstArm = xyzWingLocations[1]
            secondArm = xyzWingLocations[2]

            pivotNeighbours = puzzle.combinedNeighbours(pivot, *xyzWingLocations)
            firstArmNeighbours = puzzle.combinedNeighbours(firstArm, *xyzWingLocations)
            secondArmNeighbours = puzzle.combinedNeighbours(secondArm, *xyzWingLocations)

            commonNeighbours = (set(pivotNeighbours) &
                                set(firstArmNeighbours) &
                                set(secondArmNeighbours))

            for location in commonNeighbours:

                removedCandidates = puzzle.removeSolvingCandidates(location, xyzWingCandidate)

                if removedCandidates:
                    puzzle.addToLog(successString, xyzWingCandidate, location, xyzWingLocations)

    def cleanup(self, puzzle):
        if not self.xyzWingGroups:
            return

        for xyzWingGroup in self.xyzWingGroups:
            xyzWingLocations = xyzWingGroup[0]
            for location in xyzWingLocations:
                if not puzzle.isEmpty(location):
                    continue
                numberOfCandidates = len(puzzle.allSolvingCandidates(location))
                if numberOfCandidates not in (2,3):
                    continue
                if xyzWingGroup in self.xyzWingGroups:
                    self.xyzWingGroups.remove(xyzWingGroup)
                    break

    def generateXYZWingGroups(self, puzzle):
        if self.xyzWingGroups:
            return

        for firstPair in puzzle.nLocations(puzzle.emptyLocations(), 2):
            result = self.xyzWingPairValid(firstPair)
            if not result:
                continue

            pivot = result[0]
            firstArm = result[1]
            firstArmCandidates = result[2]

            for secondPair in puzzle.nLocations(puzzle.emptyLocations(), 2):
                if sorted(secondPair) == sorted(firstPair):
                    continue

                if pivot not in secondPair:
                    continue

                result = self.xyzWingPairValid(secondPair)
                if not result:
                    continue

                secondArm = result[1]
                secondArmCandidates = result[2]

                if puzzle.alignment(pivot, firstArm, secondArm):
                    continue

                if secondArmCandidates == firstArmCandidates:
                    continue

                xyzWingCandidate = puzzle.commonSolvingCandidates(firstArm, secondArm)

                arms = firstArm, secondArm

                xyzWing = ([pivot] + sorted(arms), xyzWingCandidate.pop())

                if xyzWing in self.xyzWingGroups:
                    continue

                self.xyzWingGroups.append(xyzWing)

    def xyzWingPairValid(self, puzzle, pair):
        alignment = puzzle.alignment(*pair)
        if not alignment:
            return False

        pivot, nonPivot = None, None

        for location in pair:
            candidates = puzzle.allSolvingCandidates(location)
            if len(candidates) == 3:
                pivot = location
                pivotCandidates = candidates
            elif len(candidates) == 2:
                nonPivot = location
                nonPivotCandidates = candidates

        if any(location is None for location in (pivot, nonPivot)):
            return False

        if not pivotCandidates > nonPivotCandidates:
            return False

        return pivot, nonPivot, nonPivotCandidates
