#!/usr/bin/env python
""" GSTP Radiometer Analysis Tool

"""
from __future__ import print_function

PROGRAM_NAME = 'PyMona'
PROGRAM_VERSION = '0.0.1'
ABOUT_MESSAGE = u"""%(prog)s version %(version)s
""" % {"prog": PROGRAM_NAME, "version": PROGRAM_VERSION}

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


import argparse
import os.path
import sys
import logging
logger = logging.getLogger(__name__)


COL_DIRNAME   = 0
COL_BASENAME  = 1
COL_LAMP      = 2
COL_MSM_LABEL = 3
COL_COLOR     = 4
COL_STYLE     = 5


class ComboBoxDelegate(QtGui.QItemDelegate):

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        return editor

    def setEditorData(self, comboBox, index):
    
        model = index.model()
        for label, user_data in model.getComboBoxItems(index):
            comboBox.addItem(label, userData = user_data)
        
        value = model.data(index, Qt.DisplayRole)
        idx = comboBox.findText(value)
        logger.debug("found index: {} for value {}".format(idx, value))
        comboBox.setCurrentIndex(idx)

    def setModelData(self, comboBox, model, index):
        user_data = comboBox.itemData(comboBox.currentIndex(), role=Qt.UserRole)
        model.setData(index, user_data, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
        
        

class MainWindow(QtGui.QMainWindow):

    def __init__(self, file_names = None):
    
        super(MainWindow, self).__init__()

        self.setupMenu()
        self.setupModels()
        self.setupViews()

        self.setWindowTitle("PyMona")
        self.resize(1300, 670)
        
        if file_names != None:
            self.openFiles(file_names)             
            

    def setupMenu(self):
        """ Sets up the main menu.
        """
        fileMenu = QtGui.QMenu("&File", self)
        openAction = fileMenu.addAction("&Open...", self.openFiles)
        openAction.setShortcut("Ctrl+O")
        quitAction = fileMenu.addAction("E&xit", self.fileQuit)
        quitAction.setShortcut("Ctrl+Q")
        
        helpMenu = QtGui.QMenu('&Help', self)
        helpMenu.addAction('&About', self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(helpMenu)

        
    def setupModels(self):
        """ Sets up table models """
        
        self.all_results = []
        self.model = QtGui.QStandardItemModel(0, 4, self) # set nr of columns to 6 to include color & style

        self.model.setHeaderData(COL_DIRNAME,   QtCore.Qt.Horizontal, "Location")
        self.model.setHeaderData(COL_BASENAME,  QtCore.Qt.Horizontal, "File")
        self.model.setHeaderData(COL_LAMP,      QtCore.Qt.Horizontal, "Lamp")
        self.model.setHeaderData(COL_MSM_LABEL, QtCore.Qt.Horizontal, "Measurement label")
        self.model.setHeaderData(COL_COLOR,     QtCore.Qt.Horizontal, "Color")
        self.model.setHeaderData(COL_STYLE,     QtCore.Qt.Horizontal, "Style")  
        
         # The reference result (this changes when a new row is selected in the table)
        self.ref_idx = 0
        

    def appendResult(self, file_name, result):
        
        row = len(self.all_results)
        self.model.insertRow(row)
        
        dir_name, base_name = os.path.split(os.path.abspath(file_name))
        self.model.setData(self.model.index(row, COL_DIRNAME), dir_name)
        self.model.setData(self.model.index(row, COL_BASENAME), base_name)
        self.model.setData(self.model.index(row, COL_LAMP), "lamp-{:d}".format(row))
        self.model.setData(self.model.index(row, COL_MSM_LABEL), "measurement label {:d}".format(row))

        self.model.setData(self.model.index(row, COL_COLOR), "color")
        self.model.setData(self.model.index(row, COL_STYLE), "style")

        self.all_results.append(result)
        
            
    def loadModel(self, file_name):
        """ Loads the model data from a HDF-5 file"""
        
        logger.debug('loading data from: {}'.format(file_name))
        try:
            result = read_stored_results_from_hdf5(file_name)
        except Exception, ex:
            logger.exception("Error opening: %s", ex)
            QtGui.QMessageBox.warning(self, "Error opening file", str(ex))        
            return
        
        self.appendResult(file_name, result)
        self.onSubtractTableChanged() # sets self.subtracted_data and updates plots


    def setupViews(self):
    
        central_splitter = QtGui.QSplitter(self, orientation = Qt.Vertical)
        central_splitter.setStretchFactor(0, 0)
        central_splitter.setStretchFactor(1, 1)
        self.setCentralWidget(central_splitter)
        
        # -- fit plot --

        results_group_box = QtGui.QGroupBox("Fit results")
        central_splitter.addWidget(results_group_box)
        
        
        results_layout = QtGui.QVBoxLayout()
        results_group_box.setLayout(results_layout)

        # -- subtract table --
        
        subtract_group_box = QtGui.QGroupBox("Dark subtraction")
        central_splitter.addWidget(subtract_group_box)
        
        subtract_layout = QtGui.QVBoxLayout()
        subtract_group_box.setLayout(subtract_layout)
        
        self.compare_table = QtGui.QTableView()  # TODO: rename
        self.compare_table.setModel(self.model)
        self.compare_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) 
        self.compare_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.compare_table.setColumnWidth(COL_DIRNAME, 400)
        self.compare_table.setColumnWidth(COL_BASENAME, 200)
        self.compare_table.setColumnWidth(COL_LAMP, 100)
        self.compare_table.setColumnWidth(COL_MSM_LABEL, 200)
        self.compare_table.setColumnWidth(COL_COLOR, 100)
        self.compare_table.setColumnWidth(COL_STYLE, 100)
        self.compare_table.horizontalHeader().setStretchLastSection(True)
        
        selection_model = self.compare_table.selectionModel()
        selection_model.selectionChanged.connect(self.onSelectionChanged)
        
        subtract_layout.addWidget(self.compare_table)
  
    def onSelectionChanged(self, selected=None, deselected=None):
        """ Makes the selected result the reference result
        
            Called when a row is selected in the table.
        """
        logger.debug("onSubtractTableChanged")
    
        selection_model = self.compare_table.selectionModel()
        
        assert len(selection_model.selectedRows()) == 1, \
            "Only one row should be select, got: {}".format(len(selection_model.selectedRows()) )
        selection = selection_model.selectedRows()[0]
        self.ref_idx = selection.row()
        logger.debug("Reference is now: {}".format(self.ref_idx))

        

    def onSubtractTableChanged(self, top_left_index=None, botrom_right_index=None):
        """ Called when an item in the dark subract table has changed
        """
        logger.debug("onSubtractTableChanged")
        self.compare_table.selectRow(0)
        
 
    def getTableItem(self, row, col):
        return self.model.data(self.model.index(row, col), Qt.DisplayRole)
        
    
        
    
            
    def test(self):
        """ Simple function used to test stuff during run-time"""
        import inspect
        from pprint import pprint
        from utils import print_class_tree
        
        logger.debug('self.test()')

        
        
    def openFiles(self, file_names=None):
        if not file_names:
            file_names = QtGui.QFileDialog.getOpenFileNames(self,
                    "Choose one or more data files", '', '*.h5')[0]

            print ("File names: {}".format(file_names))
        for file_name in file_names:
            logger.info("Loading data from: {!r}".format(file_name))
            self.loadModel(file_name)

            
    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def fileQuit(self):
        self.close()

    #def closeEvent(self, ce):
    #    self.fileQuit()
        

def main():
    
    app = QtGui.QApplication(sys.argv)
    
    parser = argparse.ArgumentParser(description='Compare irradiances measured with the ESA GSTP Radiometer')
    parser.add_argument('file_names', metavar='FILE', nargs='*', help='files to compare')
    parser.add_argument('-l', '--log-level', dest='log_level', default = 'warn', 
        help    = "Log level. Only log messages with a level higher or equal than this will be printed. Default: 'warn'", 
        choices = ('debug', 'info', 'warn', 'error', 'critical'))
    
    args = parser.parse_args()

    logging.basicConfig(level = args.log_level.upper(), 
        #format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')

    logger.info('Started GSTP Rad comparison')
    window = MainWindow(file_names = args.file_names)
    window.show()
    exit_code = app.exec_()
    logger.info('Done GSTP Radiometer comparison')
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
    