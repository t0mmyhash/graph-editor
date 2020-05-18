import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from analyzer import Analyzer
from misc.utils import loadStylesheets
from editor.editor_window import NodeEditorWindow
from editor.editor_sub_window import CalculatorSubWindow
from editor.drag_vertices_list import QDMDragListbox
from misc.utils import dumpException, pp
from misc.register_vertices import *

DEBUG = False

class GraphEditorWindow(NodeEditorWindow):

    def initUI(self):
        #self.name_company = 'Tashkent'
        #self.name_product = 'Graph editor'

        self.stylesheet_filename = os.path.join(os.path.dirname(__file__), "qss/nodeeditor.qss")
        loadStylesheets(self.stylesheet_filename)

        self.empty_icon = QIcon(".")

        if DEBUG:
            print("Registered vertices:")
            pp(CALC_NODES)

        self.subwindow_counter = 0
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)
        self.active_flag = False
        self.createNodesDock()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("diploma")
        self.setGeometry(200, 100, 1300, 800)

        #self.onFileOpen()

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            # hacky fix for PyQt 5.14.x
            import sys
            sys.exit(0)

    def createActions(self):
        super().createActions()

        self.actClose = QAction("Cl&ose", self, statusTip="Close the active window", triggered=self.mdiArea.closeActiveSubWindow)
        self.actCloseAll = QAction("Close &All", self, statusTip="Close all the windows", triggered=self.mdiArea.closeAllSubWindows)
        self.actTile = QAction("&Tile", self, statusTip="Tile the windows", triggered=self.mdiArea.tileSubWindows)
        self.actCascade = QAction("&Cascade", self, statusTip="Cascade the windows", triggered=self.mdiArea.cascadeSubWindows)
        self.actNext = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild, statusTip="Move the focus to the next window", triggered=self.mdiArea.activateNextSubWindow)
        self.actPrevious = QAction("Pre&vious", self, shortcut=QKeySequence.PreviousChild, statusTip="Move the focus to the previous window", triggered=self.mdiArea.activatePreviousSubWindow)

        self.actSeparator = QAction(self)
        self.actSeparator.setSeparator(True)

        #self.actAbout = QAction("&About", self, statusTip="Show the application's About box", triggered=self.about)

    def updateToolButtons(self):
        self.toolButtonEq.setEnabled(self.active_flag)
        self.toolButtonCoreGraph.setEnabled(self.active_flag)
        self.toolButtonCycle.setEnabled(self.active_flag)
        self.toolButtonEq.setEnabled(self.active_flag)
        self.toolButtonCoreGraph.setEnabled(self.active_flag)

    def getCurrentNodeEditorWidget(self):
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def onFileNew(self):
        try:
            subwnd = self.createMdiChild()
            subwnd.widget().fileNew()
            subwnd.show()
            self.active_flag = False
            self.updateToolButtons()
            self.subwindow_counter += 1
        except Exception as e: dumpException(e)

    def onFileOpen(self):
        #dir = QFileDialog.getExistingDirectory(None, 'Select a directory', "/desktop", QFileDialog.ShowDirsOnl | QFileDialog.DontResolveSymlinks)
        # self.getFileDialogDirectory() #TODO: скопировать в строчку ниже
        fnames, filter = QFileDialog.getOpenFileNames(self, 'Open graph from file', '/Users/ouroboros/Desktop/', self.getFileDialogFilter())

        try:
            for fname in fnames:
                if fname:
                    existing = self.findMdiChild(fname)
                    if existing:
                        self.mdiArea.setActiveSubWindow(existing)
                    else:
                        # we need to create new subWindow and open the file
                        nodeeditor = CalculatorSubWindow()
                        if nodeeditor.fileLoad(fname):
                            self.statusBar().showMessage("File %s loaded" % fname, 5000)
                            nodeeditor.setTitle()
                            subwnd = self.createMdiChild(nodeeditor)
                            subwnd.show()
                            self.active_flag = True
                            self.updateToolButtons()
                            self.subwindow_counter +=1
                        else:
                            nodeeditor.close()
        except Exception as e: dumpException(e)

    def about(self):
        QMessageBox.information(self,"Текст")

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
#        self.helpMenu.addAction(self.actAbout)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        # print("update Menus")
        active = self.getCurrentNodeEditorWidget()
        hasMdiChild = (active is not None)

        self.actSave.setEnabled(hasMdiChild)
        self.actSaveAs.setEnabled(hasMdiChild)
        self.actClose.setEnabled(hasMdiChild)
        self.actCloseAll.setEnabled(hasMdiChild)
        self.actTile.setEnabled(hasMdiChild)
        self.actCascade.setEnabled(hasMdiChild)
        self.actNext.setEnabled(hasMdiChild)
        self.actPrevious.setEnabled(hasMdiChild)
        self.actSeparator.setVisible(hasMdiChild)
        self.toolButtonCorr.setEnabled(hasMdiChild)
        hasMdiChild = (active is not None) and self.active_flag
        self.toolButtonEq.setEnabled(hasMdiChild)
        self.toolButtonCoreGraph.setEnabled(hasMdiChild)
        self.toolButtonCycle.setEnabled(hasMdiChild)
        self.toolButtonEq.setEnabled(hasMdiChild)
        self.toolButtonCoreGraph.setEnabled(hasMdiChild)
        self.updateEditMenu()

    def updateEditMenu(self):
        try:
            # print("update Edit Menu")
            active = self.getCurrentNodeEditorWidget()
            hasMdiChild = (active is not None)

            self.actPaste.setEnabled(hasMdiChild)

            self.actCut.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actCopy.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.actDelete.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.actUndo.setEnabled(hasMdiChild and active.canUndo())
            self.actRedo.setEnabled(hasMdiChild and active.canRedo())
        except Exception as e: dumpException(e)

    def updateWindowMenu(self):
        self.windowMenu.clear()

        toolbar_nodes = self.windowMenu.addAction("Вершины")
        toolbar_nodes.setCheckable(True)
        toolbar_nodes.triggered.connect(self.onWindowNodesToolbar)
        toolbar_nodes.setChecked(self.nodesDock.isVisible())

        self.windowMenu.addSeparator()

        self.windowMenu.addAction(self.actClose)
        self.windowMenu.addAction(self.actCloseAll)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actTile)
        self.windowMenu.addAction(self.actCascade)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.actNext)
        self.windowMenu.addAction(self.actPrevious)
        self.windowMenu.addAction(self.actSeparator)

        windows = self.mdiArea.subWindowList()
        self.actSeparator.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.getUserFriendlyFilename())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.getCurrentNodeEditorWidget())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def onWindowNodesToolbar(self):
        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def checkCorrect(self):
        calcWindow = self.getCurrentNodeEditorWidget()
        anal = Analyzer(calcWindow.scene.nodes, calcWindow.scene.edges)
        # print(anal.edges)
        # print(anal.vertices)
        isOk, msg = anal.checkCorrectness()
        # print(isOk, msg)
        if isOk:
            QMessageBox.about(self, "Правильность ввода", "Граф корректен.")
            self.active_flag = True
            self.updateMenus()
        else:
            QMessageBox.warning(self, "Правильность ввода", msg+'.')

    def makeCore(self):
        calcWindow = self.getCurrentNodeEditorWidget()
        #print(calcWindow.filename)
        # if calcWindow.filename == "/Users/ouroboros/Desktop/df5.json":
        #     print("Core(0, 0) : labels :: -> b - > a - >, brackets :: -> (1 -> ( ->.")
        #     print("Core(1, 1) : labels :: -> b - > a -> b -> a - >, brackets :: -> (1 -> )1 -> ( -> ( ->.")
        #     print("Core(1, 1) : labels :: -> b - > b -> a -> a - >, brackets :: -> (1 -> ( -> )1 -> ( ->.")
        # elif calcWindow.filename == "/Users/ouroboros/Desktop/df6.json":
        #     print("Core(0, 0) : labels :: -> _ -> b - > b - >, brackets :: empty")
        #     print("Core(1, 1) : labels :: -> _ -> a - > b -> a -> b - >, brackets :: -> _ -> ( -> _ -> ) -> _ ->.")
        anal = Analyzer(calcWindow.scene.nodes, calcWindow.scene.edges)
        anal.checkCycles()
        anal.buildCore()
        # isOk, coreLabels, coreBrackets = anal.sentencesCore()
        # print(isOk, coreLabels, coreBrackets)

    def checkCycles(self):
        calcWindow = self.getCurrentNodeEditorWidget()
        anal = Analyzer(calcWindow.scene.nodes, calcWindow.scene.edges)
        # print(anal.edges)
        # print(anal.vertices)
        msg = anal.checkCycles()
        if msg == '.':
            QMessageBox.warning(self, "Циклы в L-графе", "В графе нет циклов.")
        else:
            QMessageBox.about(self, "Циклы в L-графе", msg)
        # print(isOk, msg)

    def graphEquivalence(self):
        if self.subwindow_counter != 2:
            QMessageBox.warning(self, "Равенство языков", "Должно быть два открытых графа.")
        else:
            calcWindow = self.getCurrentNodeEditorWidget()
            first_graph = Analyzer(calcWindow.scene.nodes, calcWindow.scene.edges)
            self.mdiArea.activateNextSubWindow()
            calcWindow = self.getCurrentNodeEditorWidget()
            second_graph = Analyzer(calcWindow.scene.nodes, calcWindow.scene.edges)
            self.mdiArea.activateNextSubWindow()
            print("-----Первый граф")
            first_graph.checkCycles()
            print("-----Второй граф")
            second_graph.checkCycles()

        #print(self.subwindow_counter)

    def createToolBars(self):
        tb = self.addToolBar('Инструменты')
        self.toolButtonEq = QToolButton()
        self.toolButtonEq.setText("Проверить языки графов на равенство")
        self.toolButtonEq.clicked.connect(self.graphEquivalence)

        self.toolButtonCycle = QToolButton()
        self.toolButtonCycle.setText("Циклы")
        self.toolButtonCycle.clicked.connect(self.checkCycles)

        # self.toolButtonDet = QToolButton()
        # self.toolButtonDet.setText("Детерминированность")

        self.toolButtonCorr = QToolButton()
        self.toolButtonCorr.setText("Правильность ввода")
        self.toolButtonCorr.clicked.connect(self.checkCorrect)

        self.toolButtonCoreGraph = QToolButton()
        self.toolButtonCoreGraph.setText("Ядро L-графа")
        self.toolButtonCoreGraph.clicked.connect(self.makeCore)

        self.toolButtonEq.setEnabled(self.active_flag)
        self.toolButtonCoreGraph.setEnabled(self.active_flag)
        self.toolButtonCycle.setEnabled(self.active_flag)
        self.toolButtonEq.setEnabled(self.active_flag)
        self.toolButtonCorr.setEnabled(self.active_flag)
        self.toolButtonCoreGraph.setEnabled(self.active_flag)
        # toolButton.setAutoExclusive(True)
        tb.addWidget(self.toolButtonCorr)
        tb.addWidget(self.toolButtonCycle)
        #tb.addWidget(toolButtonDet)
        tb.addWidget(self.toolButtonCoreGraph)

        tb.addWidget(self.toolButtonEq)

    def createNodesDock(self):
        self.nodesListWidget = QDMDragListbox()
        self.nodesDock = QDockWidget("Вершины")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.nodesDock)

    def createStatusBar(self):
        self.statusBar().showMessage("ready")

    def createMdiChild(self, child_widget=None):
        nodeeditor = child_widget if child_widget is not None else CalculatorSubWindow()
        subwnd = self.mdiArea.addSubWindow(nodeeditor)
        subwnd.setWindowIcon(self.empty_icon)
        # nodeeditor.scene.addItemSelectedListener(self.updateEditMenu)
        # nodeeditor.scene.addItemsDeselectedListener(self.updateEditMenu)
        nodeeditor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        nodeeditor.addCloseEventListener(self.onSubWndClose)
        return subwnd

    def onSubWndClose(self, widget, event):
        existing = self.findMdiChild(widget.filename)
        self.mdiArea.setActiveSubWindow(existing)

        if self.maybeSave():
            event.accept()
            self.active_flag = False
            self.subwindow_counter -= 1
        else:
            event.ignore()

    def findMdiChild(self, filename):
        for window in self.mdiArea.subWindowList():
            if window.widget().filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)