import kivy
kivy.require('1.8.0')

from sudoku import Sudoku
from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.graphics import Color
from kivy.graphics import Rectangle

class ColourPalette():
    def __init__(self):
        self.colours = {}

        self.colours["superWhite"] = .92, .97, 1, 1
        self.colours["offWhite"] = .85, .90, .93, 1
        self.colours["red"] = .84, .29, .34, 1
        self.colours["blue"] = .69, .78, .85, 1
        self.colours["green"] = .67, .75, .57, 1
        self.colours["brown"] = .87, .67, .49, 1
        self.colours["black"] = 0, 0, 0, 1
        self.colours["gold"] = .5, .42, .26, 1

        self.colours["cellBack"] = self.colours["offWhite"]
        self.colours["emptyBack"] = self.colours["cellBack"]
        self.colours["candidateBack"] = self.colours["brown"]

        self.colours["constantText"] = self.colours["green"]
        self.colours["modifiedText"] = self.colours["blue"]
        self.colours["candidateText"] = self.colours["superWhite"]

        self.colours["occourenceText"] = self.colours["gold"]

    def rgba(self, colour):
        return self.colours[colour]

    def rgb(self, colour):
        return self.colours[colour][:-1]

class LogOutput(ListView):
    def __init__(self, MainSwitcher, **kwargs):
        super(LogOutput, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.logStart = len(self.MainSwitcher.sudoku.log)

    def update(self):

        self.item_strings = self.MainSwitcher.sudoku.log[self.logStart:]

class ClearLocation(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(ClearLocation, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.text = "Clear location"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if self.MainSwitcher.sudoku.isConstant(self.MainSwitcher.selected):
                return True
            else:
                self.MainSwitcher.sudoku.clearLocation(self.MainSwitcher.selected)
                self.MainSwitcher.updateCells([self.MainSwitcher.selected])

                return True

class SolveStep(Button):

    def __init__(self, MainSwitcher, step, **kwargs):
        super(SolveStep, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.step = step
        self.text = "Solve " + str(step) + " step"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if self.MainSwitcher.sudoku.solveMode:
                self.MainSwitcher.logOutput.logStart = len(self.MainSwitcher.sudoku.log)

                self.MainSwitcher.sudoku.solve(maxSuccessfulSolveOperations=self.step)

                self.MainSwitcher.logOutput.update()

                self.MainSwitcher.updateCells()

            return True

class SolveAll(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(SolveAll, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.text = "Solve all"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if self.MainSwitcher.sudoku.solveMode:
                self.MainSwitcher.logOutput.logStart = len(self.MainSwitcher.sudoku.log)

                self.MainSwitcher.sudoku.solve(bruteForceOnFail=True)

                self.MainSwitcher.logOutput.update()

                self.MainSwitcher.updateCells()

            return True

class SolveMode(Button):
    def __init__(self, MainSwitcher, **kwargs):
        super(SolveMode, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.states = {True: "Exit Solve Mode",
                       False: "Enter Solve Mode"}

        self.text = self.states[self.MainSwitcher.solveMode]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.solveMode = not self.MainSwitcher.solveMode
            self.updateText()

    def updateText(self):
        self.text = self.states[self.MainSwitcher.solveMode]

class UpdateUserCandidates(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(UpdateUserCandidates, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.states = {True: "Update Candidates",
                       False: "Don't Update Candidates"}

        self.text = self.states[self.MainSwitcher.updateUserCandidates]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.updateUserCandidates = not self.MainSwitcher.updateUserCandidates
            self.text = self.states[self.MainSwitcher.updateUserCandidates]
            return True

class ValueOrCandidateChange(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(ValueOrCandidateChange, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.states = {True: "Values",
                       False: "Candidates"}

        self.text = self.states[self.MainSwitcher.changeValues]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.changeValues = not self.MainSwitcher.changeValues
            self.text = self.states[self.MainSwitcher.changeValues]
            return True

class Input(Button):
    def __init__(self, MainSwitcher, **kwargs):
        super(Input, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.bind(size=self.redraw)

    def redraw(self, *args):
        self.font_size = min(self.size[0], self.size[1]) * self.MainSwitcher.padDecimal

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.setValue(self.value)

            return True

class ModifiedCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ModifiedCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

    def update(self):
        if self.MainSwitcher.highlightOccourences and self.MainSwitcher.selected > 0:
            if (self.MainSwitcher.sudoku.getValue(self.MainSwitcher.selected) ==
                self.value):
                self.color = self.MainSwitcher.palette.rgba("occourenceText")
            else:
                self.color = self.MainSwitcher.palette.rgba("modifiedText")
        else:
            self.color = self.MainSwitcher.palette.rgba("modifiedText")

class ConstantCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ConstantCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

    def update(self):
        if self.MainSwitcher.highlightOccourences and self.MainSwitcher.selected > 0:
            if (self.MainSwitcher.sudoku.getValue(self.MainSwitcher.selected) ==
                self.value):
                self.color = self.MainSwitcher.palette.rgba("occourenceText")
            else:
                self.color = self.MainSwitcher.palette.rgba("constantText")
        else:
            self.color = self.MainSwitcher.palette.rgba("constantText")

class EmptyCell(GridLayout):
    def __init__(self, MainSwitcher, **kwargs):
        super(EmptyCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

    def update(self):
        if self.MainSwitcher.highlightOccourences and self.MainSwitcher.selected > 0:
            for candidate in self.candidates:
                if (self.MainSwitcher.sudoku.getValue(self.MainSwitcher.selected) ==
                        candidate.value):
                    candidate.color = self.MainSwitcher.palette.rgba("occourenceText")
                else:
                    candidate.color = self.MainSwitcher.palette.rgba("candidateText")
        else:
            for candidate in self.candidates:
                candidate.color = self.MainSwitcher.palette.rgba("candidateText")

class Candidate(Label):
    pass

class EmptyCandidate(Label):
    pass

class PlayModeScreen(Screen):
    pass

class SolveModeScreen(Screen):
    pass

class GameScreen(Screen):
    pass

class SelectScreen(Screen):
    pass

class Game(ScreenManager):
    app = ObjectProperty(None)
    sudoku = ObjectProperty(None)
    selected = NumericProperty(-1)
    changeValues = BooleanProperty(True)
    solveMode = BooleanProperty(False)
    updateUserCandidates = BooleanProperty(True)
    highlightOccourences = BooleanProperty(True)
    highlightClashes = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.palette = ColourPalette()
        self.padDecimal = 0.8
        self.current = "select"
        Window.bind(size=self.on_screenSizeChange)
        self.bind(sudoku=self.on_sudoku)
        self.bind(selected=self.on_selected)
        self.bind(highlightOccourences=self.on_highlightOccourences)
        self.bind(updateUserCandidates=self.on_updateUserCandidates)
        self.bind(solveMode=self.on_solveMode)
        self.bind(highlightClashes=self.on_highlightClashes)

    def updateCells(self, locations=None):
        if self.solveMode:
            self.ids.puzzleView.clear_widgets()
            self.initialisePuzzleView()
        else:
            unchangedCells = [cell for cell in self.ids.puzzleView.cells if cell.location not in locations]

            self.ids.puzzleView.clear_widgets()
            self.ids.puzzleView.cells = []

            for location in self.sudoku.locations():
                if location not in locations:
                    cell = unchangedCells[0]
                    unchangedCells = unchangedCells[1:]
                else:
                    cell = self.newCell(location)

                self.ids.puzzleView.add_widget(cell)
                self.ids.puzzleView.cells.append(cell)

        for cell in self.ids.puzzleView.cells:
            cell.update()

    def on_updateUserCandidates(self, caller, value):
        if self.updateUserCandidates:
            self.sudoku.updateUserCandidates()
            self.updateCells(self.sudoku.locations())

    def on_screenSizeChange(self, caller, size):
        self.resizeCells()
        self.gameScreenGridOrient()
        if not self.solveMode:
            self.resizePlayModeGrid()
            self.miscButtonsOrient()

    def on_selected(self, caller, selected):
        self.enforceClearLocationButtonState()
        self.enforceInputButtonState()
        if self.selected < 1:
            self.updateCells([])
        else:
            self.updateCells([self.selected])

    def on_solveMode(self, caller, selected):
        self.enforceSolveModeText()

        if self.solveMode:
            discrepancies = False
            modifiedLocations = False

            self.selected = -1

            if self.sudoku.modifiedLocations():
                modifiedLocations = True

            if modifiedLocations:
                valuesString = "".join([str(self.sudoku.getValue(location)) if self.sudoku.isConstant(location) else "0" for location in self.sudoku.locations()])
                solvedPuzzle = Sudoku(valuesString)
                solvedPuzzle.solve(10, bruteForceOnFail=True)

                for location in self.sudoku.modifiedLocations():
                    if self.sudoku.getValue(location) != solvedPuzzle.getValue(location):
                        discrepancies = True
                        break

            if discrepancies:
                for location in self.sudoku.modifiedLocations():
                    self.sudoku.clearLocation(location)

            self.sudoku.hasIntersections = False
            self.sudoku.hasCandidates = False
            self.sudoku.initialiseCandidates()

            self.ids.playSolveSwitcher.current = "solveMode"
        else:
            if not self.sudoku.isComplete():
                self.sudoku.userCandidatesDict = {}
                self.sudoku.userCandidatesDict.update(self.sudoku.solvingCandidatesDict)

            self.ids.playSolveSwitcher.current = "playMode"

    def enforceSolveModeText(self):
        for button in self.solveModeButtons:
            button.updateText()

    def enforceClearLocationButtonState(self):
        if self.sudoku.isConstant(self.selected):
            self.clearLocationButton.disabled = True
        else:
            self.clearLocationButton.disabled = False

    def enforceInputButtonState(self):
        if self.sudoku.isConstant(self.selected):
            newDisabledState = True
        else:
            newDisabledState = False

        for button in self.ids.inputsGrid.buttons:
            button.disabled = newDisabledState

    def on_highlightOccourences(self, caller, value):
        self.updateCells()

    def on_highlightClashes(self, caller, value):
        self.updateCells()

    def setValue(self, value):
        if self.selected < 1:
            return
        elif self.sudoku.isConstant(self.selected):
            return
        else:
            if self.changeValues:
                self.sudoku.setValue(self.selected, value)
                if self.updateUserCandidates:
                    self.sudoku.updateUserCandidates()

                    affectedLocations = self.sudoku.allCombinedNeighbours(self.selected)
                    affectedLocations.add(self.selected)

                    self.updateCells(affectedLocations)
                else:
                    self.updateCells([self.selected])
            else:
                self.sudoku.toggleUserCandidate(self.selected, value)
                self.updateCells([self.selected])

    def resizePlayModeGrid(self):

        if Window.size[0] > Window.size[1]:
            size_hint_x = None
            size_hint_y = 1
            width = Window.size[0] - self.ids.puzzleView.width
            self.ids.playModeGrid.width = width
        else:
            size_hint_x = 1
            size_hint_y = None
            height = Window.size[1] - self.ids.puzzleView.height
            self.ids.playModeGrid.height = height

        self.ids.playModeGrid.size_hint = size_hint_x, size_hint_y

    def miscButtonsOrient(self):
        cols = 1
        rows = None

        self.ids.miscPlayButtons.cols = cols
        self.ids.miscPlayButtons.rows = rows

        self.ids.miscSolveButtons.cols = cols
        self.ids.miscSolveButtons.rows = rows

    def gameScreenGridOrient(self):

        if Window.size[0] > Window.size[1]:
            cols = None
            rows = 1
        else:
            cols = 1
            rows = None

        self.ids.gameScreenGrid.cols = cols
        self.ids.gameScreenGrid.rows = rows

    def newSudoku(self, size):
        if size < 9:
            sudoku = Sudoku(size=size)
        else:
            sudoku = Sudoku("009003201470002030800000074020000300000000710000794000000300000000925000000018500")
            # sudoku = Sudoku(size=size)
        sudoku.initialiseCandidates()
        return sudoku

    def resizeCells(self):
        if self.sudoku is None:
            return

        for cell in self.ids.puzzleView.cells:
            cell.size = self.cellSize()
            cell.font_size = self.cellWidth() * self.padDecimal

            if self.sudoku.isEmpty(cell.location):
                for candidate in cell.candidates:
                    candidate.size = self.candidateSize()
                    candidate.font_size = self.candidateWidth() * self.padDecimal

        self.ids.puzzleView.size = [self.cellWidth() * self.sudoku.unitSize()] * 2

    def cellWidth(self):
        windowWidth = min(Window.size)
        cellWidth = windowWidth/float(self.sudoku.unitSize())

        return cellWidth

    def candidateWidth(self):
        cellWidth = self.cellWidth()

        widthDivisor = max(self.sudoku.subGridsInRow(), self.sudoku.subGridsInColumn())

        candidateWidth = cellWidth/float(widthDivisor)

        return candidateWidth

    def cellSize(self):
        return [self.cellWidth()] * 2

    def candidateSize(self):
        return [self.candidateWidth()] * 2

    def setSudoku(self, size):
        self.sudoku = self.newSudoku(size)

    def on_sudoku(self, caller, sudoku):
        self.current = "game"
        if self.updateUserCandidates:
            self.sudoku.initialiseUserCandidates()
        self.initialisePuzzleView()
        self.initialiseInputGrid()
        self.initialiseClearLocationButton()
        self.initialiseValueOrCandidateChangeButton()
        self.initialiseUpdateUserCandidatesButton()
        self.initialiseLogOutput()
        self.initialiseSolveButtons()
        self.initialiseSolveModeButton()
        self.on_screenSizeChange(self, Window.size)

    def initialiseClearLocationButton(self):
        clearLocationButton = ClearLocation(self)

        self.clearLocationButton = clearLocationButton

        self.ids.miscPlayButtons.add_widget(clearLocationButton)

    def initialiseLogOutput(self):
        newlogOutput = LogOutput(self)

        self.logOutput = newlogOutput

        self.ids.logSpace.add_widget(newlogOutput)

    def initialiseSolveButtons(self):
        self.solveButtons = []

        solveOneStep = SolveStep(self, 1)
        solveAllSteps = SolveAll(self)

        for button in (solveOneStep, solveAllSteps):
            self.ids.miscSolveButtons.add_widget(button)
            self.solveButtons.append(button)

    def initialiseSolveModeButton(self):
        self.solveModeButtons = []

        solveModeForPlay = SolveMode(self)
        solveModeForSolve = SolveMode(self)

        self.ids.miscPlayButtons.add_widget(solveModeForPlay)
        self.ids.miscSolveButtons.add_widget(solveModeForSolve)

        for button in (solveModeForPlay, solveModeForSolve):
            self.solveModeButtons.append(button)

    def initialiseUpdateUserCandidatesButton(self):
        self.ids.miscPlayButtons.add_widget(UpdateUserCandidates(self))

    def initialiseValueOrCandidateChangeButton(self):
        self.ids.miscPlayButtons.add_widget(ValueOrCandidateChange(self))

    def initialiseInputGrid(self):
        cols = max(self.sudoku.subGridsInRow(), self.sudoku.subGridsInColumn())

        self.ids.inputsGrid.cols = cols
        self.ids.inputsGrid.buttons = []
        for value in self.sudoku.possibleValues():
            newInputButton = self.newInputButton(value)

            self.ids.inputsGrid.add_widget(newInputButton)
            self.ids.inputsGrid.buttons.append(newInputButton)

    def newInputButton(self, value):
        button = Input(self)
        button.text = str(value)
        button.value = value
        button.font_size = min(button.size) * self.padDecimal
        return button

    def initialisePuzzleView(self):
        self.ids.puzzleView.cols = self.sudoku.unitSize()

        self.ids.puzzleView.size_hint = None, None
        self.ids.puzzleView.size = [self.cellWidth() * self.sudoku.unitSize()] * 2

        self.ids.puzzleView.cells = []

        for location in self.sudoku.locations():
            cell = self.newCell(location)

            self.ids.puzzleView.add_widget(cell)
            self.ids.puzzleView.cells.append(cell)

        self.resizeCells()

    def newCell(self, location):
        if self.sudoku.isConstant(location):
            newCell = self.newFilledCell(location, True)
        elif self.sudoku.isModified(location):
            newCell = self.newFilledCell(location, False)
        else:
            newCell = self.newEmptyCell(location)

        newCell.location = location
        newCell.size = self.cellSize()

        return newCell

    def newFilledCell(self, location, constant):
        if constant:
            cell = ConstantCell(self)
        else:
            cell = ModifiedCell(self)

        cell.font_size = self.cellWidth() * self.padDecimal

        cell.value = self.sudoku.getValue(location)
        cell.text = str(cell.value)

        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell(self)

        cols = max(self.sudoku.subGridsInRow(), self.sudoku.subGridsInColumn())

        cell.cols = cols
        cell.candidates = []

        if self.solveMode:
            candidates = self.sudoku.allSolvingCandidates(location)
        else:
            candidates = self.sudoku.userCandidates(location)

        for value in self.sudoku.setOfPossibleValues:
            candidateCell = self.newCandidateCell(value, candidates)

            cell.add_widget(candidateCell)
            cell.candidates.append(candidateCell)

        return cell

    def newCandidateCell(self, value, candidates):
        if value in candidates:
            candidateCell = Candidate()
            candidateCell.text = str(value)
            candidateCell.value = value
        else:
            candidateCell = EmptyCandidate()
            candidateCell.value = 0

        candidateCell.size = self.candidateSize()
        candidateCell.font_size = self.candidateWidth() * self.padDecimal

        return candidateCell

class SudokoolApp(App):

    def build(self):
        self.game = Game()
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
