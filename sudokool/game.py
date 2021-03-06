import kivy
kivy.require('1.8.0')

from sudokool import Sudoku
from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.listview import ListView

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics import Line

def nextSquareNumber(n):
    '''
    Returns the next square number, or itself if it is a square
    '''
    squareRoot = n**0.5
    if squareRoot == int(squareRoot):
        return n
    else:
        return int(squareRoot+1)**2

class ColourPalette():
    def __init__(self):
        self.colours = {}

        self.colours["superWhite"] = .92, .97, 1, 1
        self.colours["offWhite"] = .85, .90, .93, 1
        self.colours["red"] = .84, .29, .34, 1
        self.colours["salmon"] = .91, .59, .48, 1
        self.colours["blue"] = .69, .78, .85, 1
        self.colours["green"] = .67, .75, .57, 1
        self.colours["brown"] = .87, .67, .49, 1
        self.colours["black"] = 0, 0, 0, 1
        self.colours["yellow"] = 1, .95, 0, 1
        self.colours["gold"] = .5, .42, .26, 1

        self.colours["cellBack"] = self.colours["offWhite"]
        self.colours["emptyBack"] = self.colours["cellBack"]
        self.colours["candidateBack"] = self.colours["brown"]

        self.colours["constantText"] = self.colours["green"]
        self.colours["modifiedText"] = self.colours["blue"]
        self.colours["candidateText"] = self.colours["superWhite"]

        self.colours["occourenceText"] = self.colours["gold"]

        self.colours["clashingModifiedBack"] = self.colours["red"]
        self.colours["clashingConstantBack"] = self.colours["salmon"]

        self.colours["noOverlay"] = 0, 0, 0, 0
        self.colours["selectedNeighbourOverlay"] = list(self.colours["yellow"][:-1])+[.1]
        self.colours["selectedOverlay"] = list(self.colours["yellow"][:-1])+[.3]
        self.colours["selectedCandidateNeighbourOverlay"] = list(self.colours["yellow"][:-1])+[.2]
        self.colours["selectedCandidateOverlay"] = list(self.colours["yellow"][:-1])+[.4]

        self.colours["cellBorders"] = self.colours["black"]
        self.colours["subGridBorders"] = self.colours["black"]

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

class Redo(Button):

    def __init__(self, MainSwitcher, step, **kwargs):
        super(Redo, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.type = "redo"

        self.step = step
        self.text = "Redo " + str(step) + " step"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if not self.MainSwitcher.solveMode:
                self.MainSwitcher.sudoku.redo()
                self.MainSwitcher.updateCells()

            return True

class Undo(Button):

    def __init__(self, MainSwitcher, step, **kwargs):
        super(Undo, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.type = "undo"

        self.step = step
        self.text = "Undo " + str(step) + " step"

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            if not self.MainSwitcher.solveMode:
                self.MainSwitcher.sudoku.undo()
                self.MainSwitcher.updateCells()

            return True

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
                self.MainSwitcher.updateCells()

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

                self.MainSwitcher.sudoku.solve(forceSolveOnFail=True)

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

class Cell(Label):
    def __init__(self, MainSwitcher, location, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher
        self.location = location
        self.bind(size=self.update, pos=self.update)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

    def update(self, *args):
        return

class ModifiedCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ModifiedCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher
        self.bind(size=self.update, pos=self.update)

    def update(self, *args):
        self.text = str(self.MainSwitcher.sudoku.getValue(self.location))
        self.MainSwitcher.paintBackground(self)
        self.MainSwitcher.paintFilledNeighbourOverlay(self)

        if self.MainSwitcher.sudoku.isModified(self.location):
            self.opacity = 1
        else:
            self.opacity = 0



class ConstantCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ConstantCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher
        self.bind(size=self.update, pos=self.update)

    def update(self, *args):
        self.MainSwitcher.paintBackground(self)
        self.MainSwitcher.paintFilledNeighbourOverlay(self)

        if self.MainSwitcher.sudoku.isConstant(self.location):
            self.opacity = 1
        else:
            self.opacity = 0


class EmptyCell(GridLayout):
    def __init__(self, MainSwitcher, **kwargs):
        super(EmptyCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher
        self.bind(size=self.update, pos=self.update)

    def update(self, *args):
        self.MainSwitcher.paintEmptyNeighbourOverlay(self)

        if self.MainSwitcher.solveMode:
            candidates = self.MainSwitcher.sudoku.allSolvingCandidates(self.location)
        else:
            candidates = self.MainSwitcher.sudoku.userCandidates(self.location)

        for candidate in self.candidates:
            if candidate.value in candidates:
                candidate.opacity = 1
            else:
                candidate.opacity = 0

        if self.MainSwitcher.sudoku.isEmpty(self.location):
            self.opacity = 1
        else:
            self.opacity = 0

class CellHolder(ScatterLayout):
    def __init__(self, **kwargs):
        super(CellHolder, self).__init__(**kwargs)
        self.auto_bring_to_front = False
        self.do_rotation = False
        self.do_scale = False
        self.do_translation = False

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

    def validSelection(self):
        if self.selected in self.sudoku.locations():
            return True
        else:
            return False

    def updateCells(self):
        for cell in self.ids.puzzleView.constantCells:
            cell.update()
        for cell in self.ids.puzzleView.modifiedCells:
            cell.update()
        for cell in self.ids.puzzleView.emptyCells:
            cell.update()

    def on_updateUserCandidates(self, caller, value):
        if self.updateUserCandidates:
            self.sudoku.updateUserCandidates()
            self.updateCells()

    def on_screenSizeChange(self, caller, size):
        self.resizeCells()
        self.gameScreenGridOrient()
        self.paintBorders()
        if not self.solveMode:
            self.resizePlayModeGrid()
            self.miscButtonsOrient()

    def on_selected(self, caller, selected):
        self.enforceClearLocationButtonState()
        self.enforceInputButtonState()
        self.updateCells()

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
                solvedPuzzle.solve(forceSolveOnFail=True)

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

            self.updateCells()

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

    def enforceUndoButtons(self):
        for button in self.undoButtons:
            if button.type == "undo":
                button.disabled = not bool(self.sudoku.undoStack)
            elif button.type == "redo":
                button.disabled = not bool(self.sudoku.redoStack)

    def on_highlightOccourences(self, caller, value):
        self.updateCells()

    def on_highlightClashes(self, caller, value):
        self.updateCells()

    def paintBorders(self):
        self.ids.puzzleView.canvas.after.clear()
        #Cell borders
        with self.ids.puzzleView.canvas.after:
            Color(*self.palette.rgba("cellBorders"))

            for i in xrange(1, self.sudoku.unitSize()):
                Line(points=[i*self.cellWidth(), 0,
                             i*self.cellWidth(), self.ids.puzzleView.height],
                     width=1)
                Line(points=[0, i*self.cellWidth(),
                             self.ids.puzzleView.height, i*self.cellWidth()],
                     width=1)

        #Subgrid borders
        with self.ids.puzzleView.canvas.after:
            Color(*self.palette.rgba("subGridBorders"))

            for i in xrange(0, self.sudoku.unitSize()+1, self.sudoku.subGridsInColumn()):
                Line(points=[i*self.cellWidth(), 0,
                             i*self.cellWidth(), self.ids.puzzleView.height],
                     width=2)

                Line(points=[0, i*self.cellWidth(),
                             self.ids.puzzleView.height, i*self.cellWidth()],
                     width=2)

    def paintBackground(self, cell):
        cell.canvas.before.clear()
        if self.highlightClashes and self.sudoku.isClashing(cell.location):
            with cell.canvas.before:
                if isinstance(cell, ConstantCell):
                    Color(*self.palette.rgba("clashingConstantBack"))
                else:
                    Color(*self.palette.rgba("clashingModifiedBack"))
        else:
            with cell.canvas.before:
                Color(*self.palette.rgba("cellBack"))

        with cell.canvas.before:
            Rectangle(size=cell.size, pos=cell.pos)

    def paintFilledNeighbourOverlay(self, cell):
        if not self.validSelection():
            return

        cell.canvas.before.remove(cell.highlight)
        if self.highlightOccourences and cell.location == self.selected:
            with cell.canvas.before:
                cell.highlight = Color(*self.palette.rgba("selectedOverlay"))
        elif self.highlightOccourences and \
                        cell.location in self.sudoku.allCombinedNeighbours(self.selected):
            with cell.canvas.before:
                cell.highlight = Color(*self.palette.rgba("selectedNeighbourOverlay"))
        else:
            with cell.canvas.before:
                cell.highlight = Color(*self.palette.rgba("noOverlay"))

        with cell.canvas.before:
            Rectangle(size=cell.size, pos=cell.pos)

    def paintEmptyNeighbourOverlay(self, cell):
        if not self.validSelection():
            return

        self.paintFilledNeighbourOverlay(cell)

        for candidate in cell.candidates:
            candidate.canvas.before.remove(candidate.highlight)
            if self.highlightOccourences and cell.location == self.selected:
                with candidate.canvas.before:
                    candidate.highlight = Color(*self.palette.rgba("selectedCandidateOverlay"))
            elif self.highlightOccourences and \
                            cell.location in self.sudoku.allCombinedNeighbours(self.selected):
                with candidate.canvas.before:
                    candidate.highlight = Color(*self.palette.rgba("selectedCandidateNeighbourOverlay"))
            else:
                with candidate.canvas.before:
                    candidate.highlight = Color(*self.palette.rgba("noOverlay"))

            with candidate.canvas.before:
                Rectangle(size=candidate.size, pos=candidate.pos)

    def setValue(self, value):
        if not self.validSelection():
            return
        elif self.sudoku.isConstant(self.selected):
            return
        else:
            if self.changeValues:
                self.sudoku.setValue(self.selected, value)
                if self.updateUserCandidates:
                    self.sudoku.updateUserCandidates()

            else:
                self.sudoku.toggleUserCandidate(self.selected, value)

            self.enforceUndoButtons()
            self.updateCells()

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
        sudoku = Sudoku(size=size)
        sudoku.initialiseCandidates()
        return sudoku

    def resizeCells(self):
        if self.sudoku is None:
            return

        def resize(cell, empty):
            cell.size = self.cellSize()
            cell.font_size = self.cellWidth() * self.padDecimal

            if empty:
                for candidate in cell.candidates:
                    candidate.size = self.candidateSize()
                    candidate.font_size = self.candidateWidth() * self.padDecimal
        for cell in self.ids.puzzleView.touchCells:
            resize(cell, False)
        for cell in self.ids.puzzleView.constantCells:
            resize(cell, False)
        for cell in self.ids.puzzleView.modifiedCells:
            resize(cell, False)
        for cell in self.ids.puzzleView.emptyCells:
            resize(cell, True)

        self.ids.puzzleView.size = [self.cellWidth() * self.sudoku.unitSize()] * 2
        self.updateCells()

    def cellWidth(self):
        windowWidth = min(Window.size)
        cellWidth = windowWidth/float(self.sudoku.unitSize())

        return cellWidth

    def candidateWidth(self):
        cellWidth = self.cellWidth()

        # Using the square root of the next highest square number, so that the cells don't look cramped.
        widthDivisor = nextSquareNumber(self.sudoku.unitSize())**0.5

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
        self.initialiseUndoButtons()
        self.on_screenSizeChange(self, Window.size)

    def initialiseUndoButtons(self):
        self.undoButtons = []

        undoOneStep = Undo(self, 1)
        redoOneStep = Redo(self, 1)

        for button in (undoOneStep, redoOneStep):
            self.ids.undoButtons.add_widget(button)
            self.undoButtons.append(button)

        self.enforceUndoButtons()

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

        self.ids.puzzleView.touchCells = []
        self.ids.puzzleView.constantCells = []
        self.ids.puzzleView.modifiedCells = []
        self.ids.puzzleView.emptyCells = []

        cellSize = self.cellSize()

        for location in self.sudoku.locations():
            cellHolder = self.newCellHolder(location, cellSize)
            self.ids.puzzleView.add_widget(cellHolder)

        self.resizeCells()

    def newCellHolder(self, location, cellSize):
        cellHolder = CellHolder(size=cellSize)
        touchCell = Cell(self, location)
        constantCell = self.newFilledCell(location, True)
        modifiedCell = self.newFilledCell(location, False)
        emptyCell = self.newEmptyCell(location)

        self.ids.puzzleView.touchCells.append(touchCell)
        self.ids.puzzleView.constantCells.append(constantCell)
        self.ids.puzzleView.modifiedCells.append(modifiedCell)
        self.ids.puzzleView.emptyCells.append(emptyCell)

        for cell in (touchCell, constantCell, modifiedCell, emptyCell):
            cell.location = location
            cell.size = self.cellSize()
            cell.update()
            cellHolder.add_widget(cell)

        return cellHolder

    def newFilledCell(self, location, constant):
        if constant:
            cell = ConstantCell(self)
        else:
            cell = ModifiedCell(self)

        cell.font_size = self.cellWidth() * self.padDecimal

        with cell.canvas.before:
            cell.highlight = Color(*self.palette.rgba("noOverlay"))

        cell.value = self.sudoku.getValue(location)
        cell.text = str(cell.value)

        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell(self)

        # Using the square root of the next highest square number, so that the cells don't look cramped.
        cols = int(nextSquareNumber(self.sudoku.unitSize())**0.5)

        cell.cols = cols
        cell.candidates = []

        with cell.canvas.before:
            cell.highlight = Color(*self.palette.rgba("noOverlay"))

        for value in self.sudoku.setOfPossibleValues:
            candidateCell = self.newCandidateCell(value)

            cell.add_widget(candidateCell)
            cell.candidates.append(candidateCell)

        return cell

    def newCandidateCell(self, value):
        candidateCell = Candidate()
        candidateCell.text = str(value)
        candidateCell.value = value

        with candidateCell.canvas.before:
            candidateCell.highlight = Color(*self.palette.rgba("noOverlay"))

        candidateCell.size = self.candidateSize()
        candidateCell.font_size = self.candidateWidth() * self.padDecimal

        return candidateCell

class SudokoolApp(App):

    def build(self):
        self.game = Game()
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
