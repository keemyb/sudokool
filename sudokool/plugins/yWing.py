from sudokool.plugin import Plugin

class yWing(Plugin):

    def __init__(self):
        self.name = "Y-Wing"
        self.minSize = None
        self.maxSize = None
        self.rank = 140
        self.yWingGroups = []

    def solve(self, puzzle):
        self.generateYWingGroups(puzzle)

        successString = "Y-Wing: {0} has been removed from {1}, as it can be seen by {2}, part of a Y-Wing"

        for yWingGroup in self.yWingGroups:
            yWingLocations = yWingGroup[0]
            yWingCandidate = yWingGroup[1]
            firstArm = yWingLocations[1]
            secondArm = yWingLocations[2]

            firstArmNeighbours = puzzle.combinedNeighbours(firstArm)
            secondArmNeighbours = puzzle.combinedNeighbours(secondArm)

            commonNeighbours = ((set(firstArmNeighbours) &
                                set(secondArmNeighbours)) -
                                set(yWingLocations))

            for location in commonNeighbours:

                removedCandidates = puzzle.removeSolvingCandidates(location, yWingCandidate)

                if removedCandidates:
                    puzzle.addToLog(successString, yWingCandidate, location, (firstArm, secondArm))

    def cleanup(self, puzzle):
        if not self.yWingGroups:
            return

        for yWingGroup in self.yWingGroups:
            yWingLocations = yWingGroup[0]
            for location in yWingLocations:
                if not puzzle.isEmpty(location):
                    continue
                if len(puzzle.allSolvingCandidates(location)) != 2:
                    continue
                if yWingGroup in self.yWingGroups:
                    self.yWingGroups.remove(yWingGroup)
                    break

    def generateYWingGroups(self, puzzle):
        if self.yWingGroups:
            return

        for firstPair in puzzle.nLocations(puzzle.emptyLocations(), 2):
            yWingResult = self.yWingPairValid(firstPair)
            if not yWingResult:
                continue

            firstAlignment = yWingResult[0]
            firstCommonCandidates = yWingResult[1]

            for secondPair in puzzle.nLocations(puzzle.emptyLocations(), 2):
                if secondPair == firstPair:
                    continue

                if not any(location in firstPair for location in secondPair):
                    continue

                yWingResult = self.yWingPairValid(secondPair)
                if not yWingResult:
                    continue

                secondAlignment = yWingResult[0]
                secondCommonCandidates = yWingResult[1]

                if secondAlignment == firstAlignment:
                    continue

                if secondCommonCandidates == firstCommonCandidates:
                    continue

                pivot = set(firstPair) & set(secondPair)

                yWingLocations = [(set(firstPair) - pivot).pop(),
                         (set(secondPair) - pivot).pop()]
                yWingLocations.insert(0, pivot.pop())

                yWingCandidate = puzzle.commonSolvingCandidates(*yWingLocations[1:])

                if not yWingCandidate:
                    continue

                yWing = ([yWingLocations[0]] + sorted(yWingLocations[1:]),
                         yWingCandidate.pop())

                if yWing in self.yWingGroups:
                    continue

                self.yWingGroups.append(yWing)

    def yWingPairValid(self, puzzle, pair):
        alignment = puzzle.alignment(*pair)
        if not alignment:
            return False

        commonCandidates = puzzle.commonSolvingCandidates(*pair)
        if not commonCandidates:
            return False

        firstLocationCandidates = puzzle.allSolvingCandidates(pair[0])
        secondLocationCandidates = puzzle.allSolvingCandidates(pair[1])

        if firstLocationCandidates == secondLocationCandidates:
            return False

        if len(firstLocationCandidates) != 2:
            return False

        if len(secondLocationCandidates) != 2:
            return False

        return alignment, commonCandidates, firstLocationCandidates, secondLocationCandidates
