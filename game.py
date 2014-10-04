import kivy
kivy.require('1.8.0')

from sudoku import Sudoku
from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.uix.gridlayout import GridLayout
from kivy.uix.listview import ListView

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.core.window import Window

from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty

superWhite = .92, .97, 1, 1
offWhite = .85, .90, .93, 1
red = .84, .29, .34, 1
blue = .69, .78, .85, 1
green = .67, .75, .57, 1
brown = .87, .67, .49, 1

class logOutput(ListView):
    def __init__(self, MainSwitcher, **kwargs):
        super(logOutput, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.logStart = len(self.MainSwitcher.sudoku.log)

    def update(self):

        self.item_strings = self.MainSwitcher.sudoku.log[self.logStart:]

class solveStep(Button):

    def __init__(self, MainSwitcher, step, **kwargs):
        super(solveStep, self).__init__(**kwargs)
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

class solveAll(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(solveAll, self).__init__(**kwargs)
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

class solveMode(Button):
    def __init__(self, MainSwitcher, **kwargs):
        super(solveMode, self).__init__(**kwargs)
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

class updateUserCandidates(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(updateUserCandidates, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

        self.states = {True: "Update Candidates",
                       False: "Don't Update Candidates"}

        self.text = self.states[self.MainSwitcher.updateUserCandidates]

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.updateUserCandidates = not self.MainSwitcher.updateUserCandidates
            self.text = self.states[self.MainSwitcher.updateUserCandidates]
            return True

class valueOrCandidateChange(Button):

    def __init__(self, MainSwitcher, **kwargs):
        super(valueOrCandidateChange, self).__init__(**kwargs)
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

class ConstantCell(Label):
    def __init__(self, MainSwitcher, **kwargs):
        super(ConstantCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

class EmptyCell(GridLayout):
    def __init__(self, MainSwitcher, **kwargs):
        super(EmptyCell, self).__init__(**kwargs)
        self.MainSwitcher = MainSwitcher

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos):
            self.MainSwitcher.selected = self.location

            return True

class Candidate(Label):
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
        self.current = "select"
        Window.bind(size=self.on_screenSizeChange)
        self.bind(sudoku=self.on_sudoku)
        self.bind(selected=self.on_selected)
        self.bind(highlightOccourences=self.on_highlightOccourences)
        self.bind(updateUserCandidates=self.on_updateUserCandidates)
        self.bind(solveMode=self.on_solveMode)
        # self.bind(highlightClashes=self.on_highlightClashes)

    def updateCells(self, locations=None):
        if locations is None:
            self.ids.puzzleView.clear_widgets()
            self.initialisePuzzleView()

    def on_updateUserCandidates(self, caller, value):
        if self.updateUserCandidates:
            self.sudoku.updateUserCandidates()
            self.updateCells()

    def on_screenSizeChange(self, caller, size):
        self.resizeCells()
        self.gameScreenGridOrient()
        if not self.solveMode:
            self.resizePlayModeGrid()
            self.miscButtonsOrient()

    def on_selected(self, caller, selected):
        self.enforceInputButtonState()
        self.on_highlightOccourences(caller, self.on_highlightOccourences)

    def on_solveMode(self, caller, selected):
        self.enforceSolveModeText()

        if self.solveMode:
            discrepancies = False
            modifiedLocations = False

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

    def enforceInputButtonState(self):
        if self.sudoku.isConstant(self.selected):
            newDisabledState = True
        else:
            newDisabledState = False

        for button in self.ids.inputsGrid.buttons:
            button.disabled = newDisabledState

    def on_highlightOccourences(self, caller, value):
        for cell in self.ids.puzzleView.cells:
            if self.sudoku.isFilled(cell.location):
                cell.color = superWhite
            else:
                for candidate in cell.candidates:
                    candidate.color = superWhite

        if self.highlightOccourences and self.sudoku.isFilled(self.selected):
            for cell in self.ids.puzzleView.cells:
                if self.sudoku.isFilled(cell.location):
                    if (cell.value == self.sudoku.getValue(self.selected) and
                            cell.location != self.selected):
                        cell.color = blue
                else:
                    for candidate in cell.candidates:
                        if candidate.value == self.sudoku.getValue(self.selected):
                            candidate.color = blue

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
            else:
                self.sudoku.toggleUserCandidate(self.selected, value)
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

        if Window.size[0] > Window.size[1]:
            cols = None
            rows = 1
        else:
            cols = 1
            rows = None

        self.ids.miscPlayButtons.cols = cols
        self.ids.miscPlayButtons.rows = rows

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
        sudoku.initialiseCandidates()
        return sudoku

    def resizeCells(self):
        if self.sudoku is None:
            return

        cellWidth = self.cellWidth()
        candidateWidth = self.candidateWidth()

        for cell in self.ids.puzzleView.cells:
            cell.size = cellWidth, cellWidth
            cell.font_size = cellWidth*.8
            if self.sudoku.isEmpty(cell.location):
                for candidate in cell.candidates:
                    candidate.size = [candidateWidth]*2
                    candidate.font_size = candidateWidth*.8

        self.ids.puzzleView.size = [cellWidth*self.sudoku.unitSize()]*2

    def cellWidth(self):
        windowWidth = min(Window.size)
        cellWidth = windowWidth/float(self.sudoku.unitSize())

        return cellWidth

    def candidateWidth(self):
        cellWidth = self.cellWidth()

        widthDivisor = max(self.sudoku.subGridsInRow(), self.sudoku.subGridsInColumn())

        candidateWidth = cellWidth/float(widthDivisor)

        return candidateWidth

    def setSudoku(self, size):
        self.sudoku = self.newSudoku(size)

    def on_sudoku(self, caller, sudoku):
        self.current = "game"
        if self.updateUserCandidates:
            self.sudoku.initialiseUserCandidates()
        self.initialisePuzzleView()
        self.initialiseInputGrid()
        self.initialiseValueOrCandidateChangeButton()
        self.initialiseUpdateUserCandidatesButton()
        self.initialiseLogOutput()
        self.initialiseSolveButtons()
        self.initialiseSolveModeButton()
        self.on_screenSizeChange(self, Window.size)

    def initialiseLogOutput(self):
        newlogOutput = logOutput(self)

        self.logOutput = newlogOutput

        self.ids.logSpace.add_widget(newlogOutput)

    def initialiseSolveButtons(self):
        self.solveButtons = []

        solveOneStep = solveStep(self, 1)
        solveAllSteps = solveAll(self)

        for button in (solveOneStep, solveAllSteps):
            self.ids.miscSolveButtons.add_widget(button)
            self.solveButtons.append(button)

    def initialiseSolveModeButton(self):
        self.solveModeButtons = []

        solveModeForPlay = solveMode(self)
        solveModeForSolve = solveMode(self)

        self.ids.miscPlayButtons.add_widget(solveModeForPlay)
        self.ids.miscSolveButtons.add_widget(solveModeForSolve)

        for button in (solveModeForPlay, solveModeForSolve):
            self.solveModeButtons.append(button)

    def initialiseUpdateUserCandidatesButton(self):
        self.ids.miscPlayButtons.add_widget(updateUserCandidates(self))

    def initialiseValueOrCandidateChangeButton(self):
        self.ids.miscPlayButtons.add_widget(valueOrCandidateChange(self))

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
        button.font_size = button.size[0]*0.8
        return button

    def initialisePuzzleView(self):
        self.ids.puzzleView.cols = self.sudoku.unitSize()
        self.ids.puzzleView.cells = []
        for location in self.sudoku.locations():
            if self.sudoku.isConstant(location):
                newCell = self.newFilledCell(location, True)
            elif self.sudoku.isModified(location):
                newCell = self.newFilledCell(location, False)
            else:
                newCell = self.newEmptyCell(location)

            newCell.location = location
            newCell.size = [self.cellWidth()]*2

            self.ids.puzzleView.add_widget(newCell)
            self.ids.puzzleView.cells.append(newCell)

    def newFilledCell(self, location, constant):
        if constant:
            cell = ConstantCell(self)
        else:
            cell = ModifiedCell(self)

        cell.font_size = self.cellWidth()*0.8

        cell.value = self.sudoku.getValue(location)
        cell.text = str(cell.value)

        return cell

    def newEmptyCell(self, location):
        cell = EmptyCell(self)

        cols = max(self.sudoku.subGridsInRow(), self.sudoku.subGridsInColumn())

        cell.cols = cols
        cell.candidates = []

        if self.solveMode:
            for candidate in self.sudoku.allSolvingCandidates(location):
                candidateLabel = self.newCandidateLabel(candidate)

                cell.add_widget(candidateLabel)
                cell.candidates.append(candidateLabel)
        else:
            for candidate in self.sudoku.userCandidates(location):
                candidateLabel = self.newCandidateLabel(candidate)

                cell.add_widget(candidateLabel)
                cell.candidates.append(candidateLabel)

        return cell

    def newCandidateLabel(self, candidate):
        candidateLabel = Candidate()
        candidateLabel.text = str(candidate)
        candidateLabel.value = candidate

        candidateLabel.size = [self.candidateWidth()]*2
        candidateLabel.font_size = self.candidateWidth()*.8

        return candidateLabel

class SudokoolApp(App):

    def build(self):
        self.game = Game()
        return self.game

if __name__ == "__main__":
    SudokoolApp().run()
