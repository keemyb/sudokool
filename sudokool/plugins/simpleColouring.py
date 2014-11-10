from sudokool.plugin import Plugin

class simpleColouring(Plugin):

    def __init__(self):
        self.name = "Simple Colouring"
        self.description ='''
        pass
        '''
        self.minSize = None
        self.maxSize = None
        self.rank = 15
        self.conjugateChains = []
        self.conjugatePairs = []

    def solve(self, puzzle):

        self.generateConjugateChains(puzzle)

        for chainGroup in self.conjugateChains:
            chain, candidate = chainGroup[0], chainGroup[1]
            colourOne, colourTwo = chain[::2], chain[1::2]

            simpleColouringMethods = (self.chainOnOff,
                                      self.simpleColourCase2,
                                      self.simpleColourCase4,
                                      self.simpleColourCase5)

            for method in simpleColouringMethods:
                method(puzzle, chain, colourOne, colourTwo, candidate)

    def cleanup(self, puzzle):
        self.cleanupConjugatePairs(puzzle)
        self.cleanupConjugateChains(puzzle)

    def cleanupConjugatePairs(self, puzzle):
        if not self.conjugatePairs:
            return

        for group in self.conjugatePairs:
            pair = group[0]
            if all(puzzle.isEmpty(location) for location in pair):
                continue
            if group in self.conjugatePairs:
                self.conjugatePairs.remove(group)

    def cleanupConjugateChains(self, puzzle):
        if not self.conjugateChains:
            return

        for chainGroup in self.conjugateChains:
            if self.validConjugateChain(puzzle, chainGroup):
                continue
            if chainGroup in self.conjugateChains:
                self.conjugateChains.remove(chainGroup)

    def validConjugateChain(self, puzzle, chainGroup):
        chain, candidate = chainGroup[0], chainGroup[1]
        if (chain, candidate) not in self.conjugateChains:
            return False

        for location in chain:
            if not puzzle.isEmpty(location):
                return False
            if len(puzzle.allSolvingCandidates(location)) <= 1:
                return False
            if candidate not in puzzle.solvingCandidatesDict[location]:
                return False
        return True

    def chainOnOff(self, puzzle, chain, colourOne, colourTwo, candidate):
        """Tests to see if one colour being ON is valid, if it is invalid
           the other colour must be the solution."""

        successString = "Chain ON/OFF: {0} has been removed from locations {1}, as it is part of an invalid colour"

        for testColour in (colourOne, colourTwo):
            if not self.validConjugateChain(puzzle, (chain, candidate)):
                break

            candidatesToRemove = {location: [candidate] for location in testColour}

            # We are looking for a contradiction, so if the prospective change
            # checks out we haven't learnt anything new.
            if puzzle.testProspectiveChange(candidatesToRemove):
                continue

            for correctColour in (colourOne, colourTwo):
                if testColour != correctColour:
                    candidatesToRemove = {location: [candidate] for location in correctColour}
                    puzzle.applyProspectiveChange(candidatesToRemove)
                    puzzle.changes = True
                    puzzle.addToLog(successString, candidate, [location for location in correctColour])
                    return

    def simpleColourCase2(self, puzzle, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same colour and unit, this colour must
           be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 2: locations {0} have been set to {1}, as it shares a unit with a chain where two colours are the same"

        for colour in (colourOne, colourTwo):
            if not self.validConjugateChain(puzzle, (chain, candidate)):
                break

            for pair in puzzle.nLocations(colour, 2):

                if not puzzle.alignment(*pair):
                    continue

                if colour == colourOne:
                    correctColour = colourTwo
                else:
                    correctColour = colourOne

                valuesToAdd = {location: candidate for location in correctColour}
                puzzle.applyProspectiveChange(None, valuesToAdd)
                puzzle.changes = True
                puzzle.addToLog(successString, [location for location in correctColour], candidate)
                return

    def simpleColourCase4(self, puzzle, chain, colourOne, colourTwo, candidate):
        """If two locations are in the same unit and have different colours,
           all other locations in the unit must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 4: {0} has been removed from {1}, as these locations are in the same unit as one of two locations that must be ON"

        for pair in puzzle.nLocations(chain, 2):
            if not self.validConjugateChain(puzzle, (chain, candidate)):
                break

            for alignment in puzzle.alignment(*pair):
                if ((pair[0] in colourOne and pair[1] in colourTwo) or
                    (pair[1] in colourOne and pair[0] in colourTwo)):
                    for location in puzzle.neighbourMethods[alignment](pair[0], *pair):

                        removedCandidates = puzzle.removeSolvingCandidates(location, candidate)

                        if removedCandidates:
                            puzzle.addToLog(successString, candidate, location)

    def simpleColourCase5(self, puzzle, chain, colourOne, colourTwo, candidate):
        """If a location can see two locations in a chain that have different
           colours, this location must have that candidate removed,
           as one colour must be OFF, and the other colour must be ON."""

        successString = "Simple Colouring Case 5: {0} has been removed from {1}, as this location can see both {2}, locations of different colours"

        for location in puzzle.emptyLocations():
            if location in chain:
                continue

            if candidate not in puzzle.allSolvingCandidates(location):
                continue

            for pair in puzzle.nLocations(chain, 2):
                if not self.validConjugateChain(puzzle, (chain, candidate)):
                    break

                if not (((pair[0] in colourOne and pair[1] in colourTwo) or
                        (pair[1] in colourOne and pair[0] in colourTwo))):
                    continue

                alignsWithFirstElement = puzzle.alignment(pair[0], location)
                alignsWithSecondElement = puzzle.alignment(pair[1], location)
                if alignsWithFirstElement and alignsWithSecondElement:

                    removedCandidates = puzzle.removeSolvingCandidates(location, candidate)

                    if removedCandidates:
                        puzzle.addToLog(successString, candidate, location, pair)

    def generateConjugatePairs(self, puzzle):

        if self.conjugatePairs:
            return

        for location in puzzle.emptyLocations():

            locationCandidates = puzzle.allSolvingCandidates(location)

            for candidate in locationCandidates:

                for method in puzzle.neighbourMethods.itervalues():

                    candidateCount = 1
                    prospectiveLocation = None

                    for neighbour in method(location):
                        neighbourCandidates = puzzle.allSolvingCandidates(neighbour)

                        if candidate in neighbourCandidates:
                            candidateCount += 1
                            prospectiveLocation = neighbour

                    if candidateCount != 2:
                        continue

                    group = (sorted((location, prospectiveLocation)), candidate)

                    if group not in self.conjugatePairs:
                        self.conjugatePairs.append(group)

    def generateConjugateChains(self, puzzle):

        if self.conjugateChains:
            return

        self.generateConjugatePairs(puzzle)

        for pairGroup in self.conjugatePairs:

            pair, candidates = pairGroup[0], pairGroup[1]
            chain = pair[:]

            lastChain = None
            while lastChain != chain:

                firstLink, lastLink = chain[0], chain[-1]
                lastChain = chain[:]

                for prospectivePairGroup in self.conjugatePairs:

                    prospectivePair = prospectivePairGroup[0]
                    prospectiveCandidates = prospectivePairGroup[1]

                    if prospectiveCandidates != candidates:
                        continue

                    if all(location in chain for location in prospectivePair):
                        continue

                    if any(location == firstLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.insert(0, prospectivePair[1])
                            break
                        else:
                            chain.insert(0, prospectivePair[0])
                            break

                    if any(location == lastLink for location in prospectivePair):
                        if prospectivePair[0] in chain:
                            chain.append(prospectivePair[1])
                            break
                        else:
                            chain.append(prospectivePair[0])
                            break

            if len(chain) < 3:
                continue

            chainIsASubset = False
            for existingChainGroup in self.conjugateChains[:]:
                existingChain = existingChainGroup[0]
                existingChainCandidates = existingChainGroup[1]

                if existingChainCandidates != candidates:
                    continue

                # if all locations in the current chain already exist in another,
                # it is a subset and will not be added. We break here as the
                # larger chain does not need to be purged.
                if all(location in existingChain for location in chain):
                    chainIsASubset = True
                    break

                # if all locations in the existing chain exist in the current chain,
                # the existing chain will be removed.
                if all(location in chain for location in existingChain):
                    if existingChainGroup in self.conjugateChains:
                        self.conjugateChains.remove(existingChainGroup)

            if not chainIsASubset:
                self.conjugateChains.append((chain, candidates))
