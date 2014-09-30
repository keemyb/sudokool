import kivy
kivy.require('1.8.0')  # replace with your current kivy version !

from kivy.app import App
from sudoku import Sudoku

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics import Line

from kivy.core.window import Window
from kivy.logger import Logger
from random import random

white = .85, .90, .93, 1
red = .84, .29, .34, 1
blue = .69, .78, .85, 1
green = .67, .75, .57, 1
brown = .87, .67, .49, 1

def randomColor():
    return (random(), random(), random(), 1)


class screen(BoxLayout):

    def __init__(self, sudoku, **kwargs):
        super(screen, self).__init__(**kwargs)

        self.locationsGrid = allLocationsGrid(sudoku)
        self.inputButtonGrid = inputButtonGrid(sudoku)
        self.valueOrCandidateButton = toggleValueOrCandidateEdit(sudoku)
        self.userOrSolvingButton = toggleUserOrSolvingCandidates(sudoku)
        self.autoUpdateButton = toggleAutoUpdateCandidates(sudoku)
        self.solveModeButton = toggleSolveMode(sudoku)
        self.solveOneStepButton = solveStep(sudoku, 1)
        self.solveAllButton = solveAll(sudoku)

        self.buttonHolder = GridLayout(cols=4, size_hint_y=.1, height=20)
        self.buttonHolder.add_widget(self.valueOrCandidateButton)
        self.buttonHolder.add_widget(self.userOrSolvingButton)
        self.buttonHolder.add_widget(self.autoUpdateButton)
        self.buttonHolder.add_widget(self.solveModeButton)

        self.buttonHolder2 = GridLayout(cols=4, size_hint_y=.1, height=20)
        self.buttonHolder2.add_widget(self.solveOneStepButton)
        self.buttonHolder2.add_widget(self.solveAllButton)

        self.add_widget(self.locationsGrid)
        self.add_widget(self.inputButtonGrid)
        self.add_widget(self.buttonHolder)
        self.add_widget(self.buttonHolder2)


class cell(GridLayout):

    def __init__(self, sudoku, location, **kwargs):
        super(cell, self).__init__(**kwargs)

        self.location = location

        if location in sudoku.constants:
            self.initConstant(sudoku, location)
        elif location in sudoku.emptyLocations():
            self.initEmpty(sudoku, location)
        elif location in sudoku.locations():
            self.initUser(sudoku, location)

    def initConstant(self, sudoku, location):

        value = str(sudoku.getValue(location))
        self.add_widget(Label(text=value, font_size=40, color=green))

    def initEmpty(self, sudoku, location):

        self.cols = sudoku.subGridsInRow()

        if sudoku.displaySolvingCandidates:
            if sudoku.hasSolvingCandidates(location):
                for candidate in sorted(sudoku.solvingCandidates(location)):
                    candidateValue = str(candidate)
                    candidateLabel = Label(text=candidateValue, color=red)
                    self.add_widget(candidateLabel)

        else:
            if sudoku.hasUserCandidates(location):
                for candidate in sorted(sudoku.userCandidates(location)):
                    candidateValue = str(candidate)
                    candidateLabel = Label(text=candidateValue, color=red)
                    self.add_widget(candidateLabel)

    def initUser(self, sudoku, location):

        value = str(sudoku.getValue(location))
        self.add_widget(Label(text=value, font_size=30, color=blue))

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            sudoku.selected = self.location

            return True

    def update(self, sudoku):

        if self.location in sudoku.constants:
            return

        self.clear_widgets()

        if self.location == sudoku.selected and sudoku.isEmpty(self.location):
            with self.canvas.before:
                Color(*brown)
                Line(rectangle=(self.pos[0], self.pos[1], self.size[0], self.size[1]))
        else:
            self.canvas.before.clear()

        if not sudoku.isEmpty(self.location):
            value = str(sudoku.getValue(self.location))
            self.add_widget(Label(text=value, font_size=40, color=blue))
            return

        if sudoku.displaySolvingCandidates:
            if sudoku.hasSolvingCandidates(self.location):
                for candidate in sorted(sudoku.solvingCandidates(self.location)):
                    candidateValue = str(candidate)
                    candidateLabel = Label(text=candidateValue, color=red)
                    self.add_widget(candidateLabel)

        else:
            if sudoku.hasUserCandidates(self.location):
                for candidate in sorted(sudoku.userCandidates(self.location)):
                    candidateValue = str(candidate)
                    candidateLabel = Label(text=candidateValue, color=red)
                    self.add_widget(candidateLabel)

            if sudoku.highlightOccourences:
                if not sudoku.selected:
                    return
                if not sudoku.isEmpty(sudoku.selected):
                    if sudoku.getValue(sudoku.selected) in sudoku.userCandidates(self.location):
                        for candidate in self.children:
                            if candidate.text == str(sudoku.getValue(sudoku.selected)):
                                candidate.color = brown


class allLocationsGrid(GridLayout):

    def __init__(self, sudoku, **kwargs):
        super(allLocationsGrid, self).__init__(**kwargs)

        self.cols = sudoku.unitSize()

        self.locations = []

        for location in sudoku.locations():
            newLocation = cell(sudoku, location)
            self.locations.append(newLocation)
            self.add_widget(newLocation)

    def on_touch_up(self, touch):  # temp fix, needs to use on_touch_down method

        if self.collide_point(*touch.pos):
            for cell in self.children:
                cell.update(sudoku)

            for button in self.parent.inputButtonGrid.children:
                if sudoku.isConstant(sudoku.selected):
                    button.disabled = True
                else:
                    button.disabled = False

            return True


class inputButton(Button):

    def __init__(self, value, **kwargs):
        super(inputButton, self).__init__(**kwargs)

        self.text = str(value)
        self.value = value
        self.font_size = 30

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if not sudoku.isConstant(sudoku.selected):

                if sudoku.changeValues:
                    sudoku.setValue(sudoku.selected, self.value)
                else:
                    sudoku.toggleUserCandidate(sudoku.selected, self.value)

                if sudoku.autoUpdateUserCandidates:
                    sudoku.updateUserCandidates()

            for cell in self.parent.parent.locationsGrid.children:
                cell.update(sudoku)

            return True


class inputButtonGrid(GridLayout):

    def __init__(self, sudoku, **kwargs):
        super(inputButtonGrid, self).__init__(**kwargs)

        self.cols = sudoku.subGridsInRow()

        for value in sudoku.possibleValues():
            newInputButton = inputButton(value)
            self.add_widget(newInputButton)


class toggleValueOrCandidateEdit(Button):

    def __init__(self, sudoku, **kwargs):
        super(toggleValueOrCandidateEdit, self).__init__(**kwargs)

        self.states = {True: "Values",
                       False: "Candidates"}

        self.text = self.states[sudoku.changeValues]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            sudoku.changeValues = not sudoku.changeValues
            self.text = self.states[sudoku.changeValues]
            return True


class toggleUserOrSolvingCandidates(Button):

    def __init__(self, sudoku, **kwargs):
        super(toggleUserOrSolvingCandidates, self).__init__(**kwargs)

        self.states = {True: "Solving",
                       False: "User"}

        self.text = self.states[sudoku.displaySolvingCandidates]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            sudoku.displaySolvingCandidates = not sudoku.displaySolvingCandidates
            self.text = self.states[sudoku.displaySolvingCandidates]
            return True


class toggleSolveMode(Button):

    def __init__(self, sudoku, **kwargs):
        super(toggleSolveMode, self).__init__(**kwargs)

        self.states = {True: "Exit Solve Mode",
                       False: "Go Solve!"}

        self.text = self.states[sudoku.solveMode]

    def on_touch_down(self, touch):
        from copy import deepcopy

        if self.collide_point(*touch.pos):
            sudoku.solveMode = not sudoku.solveMode
            self.text = self.states[sudoku.solveMode]

            if sudoku.solveMode:
                discrepancies = False
                anyUserLocations = False

                for location in sudoku.filledLocations():
                    if sudoku.isConstant(location):
                        continue
                    anyUserLocations = True

                if anyUserLocations:
                    solvedPuzzle = deepcopy(sudoku)
                    for location in solvedPuzzle.filledLocations():
                        if solvedPuzzle.isConstant(location):
                            continue
                        solvedPuzzle.clearLocation(location)
                    solvedPuzzle.solve(10, bruteForceOnFail=True)

                    for location in sudoku.filledLocations():
                        if sudoku.isConstant(location):
                            continue
                        if sudoku.getValue(location) != solvedPuzzle.getValue(location):
                            discrepancies = True
                            break

                if discrepancies:
                    for location in sudoku.filledLocations():
                        if sudoku.isConstant(location):
                            continue
                        sudoku.clearLocation(location)

                sudoku.hasIntersections = False
                sudoku.hasCandidates = False
                sudoku.initialiseCandidates()

                sudoku.displaySolvingCandidates = True

            else:
                if not sudoku.isComplete():
                    sudoku.userCandidatesDict = {}
                    sudoku.userCandidatesDict.update(sudoku.candidates)

                sudoku.displaySolvingCandidates = False

            for button in self.parent.parent.inputButtonGrid.children:
                button.disabled = sudoku.solveMode

            for cell in self.parent.parent.locationsGrid.children:
                cell.update(sudoku)

            return True


class toggleAutoUpdateCandidates(Button):

    def __init__(self, sudoku, **kwargs):
        super(toggleAutoUpdateCandidates, self).__init__(**kwargs)

        self.states = {True: "Auto Update",
                       False: "Not Auto Update"}

        self.text = self.states[sudoku.autoUpdateUserCandidates]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            sudoku.autoUpdateUserCandidates = not sudoku.autoUpdateUserCandidates
            self.text = self.states[sudoku.autoUpdateUserCandidates]
            if sudoku.autoUpdateUserCandidates:
                sudoku.updateUserCandidates()
                for cell in self.parent.parent.locationsGrid.children:
                    cell.update(sudoku)
            return True


class solveStep(Button):

    def __init__(self, sudoku, step, **kwargs):
        super(solveStep, self).__init__(**kwargs)

        self.step = step

        self.text = "Solve " + str(step) + " step"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if sudoku.solveMode:
                sudoku.solve(maxSuccessfulSolveOperations=self.step)
                for cell in self.parent.parent.locationsGrid.children:
                    cell.update(sudoku)
            return True

class solveAll(Button):

    def __init__(self, sudoku, **kwargs):
        super(solveAll, self).__init__(**kwargs)

        self.text = "Solve all"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if sudoku.solveMode:
                sudoku.solve(bruteForceOnFail=True)
                for cell in self.parent.parent.locationsGrid.children:
                    cell.update(sudoku)
            return True


class SudokuApp(App):

    def build(self):
        sudoku.selected = None
        sudoku.changeValues = True
        sudoku.displaySolvingCandidates = False
        sudoku.solveMode = False
        sudoku.autoUpdateUserCandidates = True
        sudoku.highlightOccourences = True
        if sudoku.autoUpdateUserCandidates:
            sudoku.initialiseUserCandidates()

        return screen(sudoku)

string9 = "003020600\
900305001\
001806400\
008102900\
700000008\
006708200\
002609500\
800203009\
005010300"
sudoku = Sudoku(string9)

string16 = "B07805E0300AD0CG\
004007000C0FA002\
A000000000043700\
0050009F00000008\
0400B8000E079300\
00E37C0000FDB004\
9F07005D03000080\
500D0F3024A8C0G0\
08000000B0000GD5\
00D000000800F0E0\
00A090F0067000BC\
000C0AB0000E7240\
7A090B1000500630\
D0CEF070A0000800\
0000E0A00D005000\
0635G9C00B00E000"

bigSudoku = Sudoku(string16)
sudoku.initialiseIntersections()

if __name__ == '__main__':
    SudokuApp().run()
