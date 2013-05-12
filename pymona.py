#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Monalisa genetic algorithms in Python.

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


COL_ID        = 0
COL_NUM_GENES = 1

        

class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent = None, target_image = None):
    
        super(MainWindow, self).__init__(parent=parent)

        self._setup_menu()
        self._setup_models()
        self._setup_views()

        self.setWindowTitle("PyMona")
        self.setGeometry(50, 50, 800, 600)
        
        #if file_names != None:
        #    self.openFiles(file_names)             
        

    def _setup_menu(self):
        """ Sets up the main menu.
        """
        file_menu = QtGui.QMenu("&File", self)
        #open_action = file_menu.addAction("&Open...", self.openFiles)
        #open_action.setShortcut("Ctrl+O")
        open_action = file_menu.addAction("&Test...", self.test)
        open_action.setShortcut("Ctrl+T")
        quit_action = file_menu.addAction("E&xit", self.quit_application)
        quit_action.setShortcut("Ctrl+Q")
        
        help_menu = QtGui.QMenu('&Help', self)
        help_menu.addAction('&About', self.about)

        self.menuBar().addMenu(file_menu)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(help_menu)

        
    def _setup_models(self):
        """ Sets up table models """
        pass


    def _setup_views(self):
    
        central_splitter = QtGui.QSplitter(self, orientation = Qt.Horizontal)
        central_splitter.setStretchFactor(0, 0)
        central_splitter.setStretchFactor(1, 1)
        self.setCentralWidget(central_splitter)

        # -- controls --
        
        controls_widget = QtGui.QWidget()
        central_splitter.addWidget(controls_widget)
        
        controls_layout = QtGui.QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        

        controls_group_box = QtGui.QGroupBox("Controls")
        controls_layout.addWidget(controls_group_box)
        
        # -- results --

        results_widget = QtGui.QWidget()
        central_splitter.addWidget(results_widget)
        
        results_layout = QtGui.QVBoxLayout()
        results_widget.setLayout(results_layout)

        results_group_box = QtGui.QGroupBox("Results")
        results_layout.addWidget(results_group_box)


        #self.graphics_view = QtGui.QGraphicsView(self.graphics_scene)
        #results_layout.addWidget(self.graphics_view)

        

        
    def __not_used__openFiles(self, file_names=None):
        
        if not file_names:
            file_names = QtGui.QFileDialog.getOpenFileNames(self,
                    "Choose one or more data files", '', '*.h5')[0]
        for file_name in file_names:
            logger.info("Loading data from: {!r}".format(file_name))
            #self.load_model(file_name)
            
    def load_model(self, file_name):
        """ Loads the model data from a HDF-5 file"""
        assert False, "Not yet implemented"
        logger.debug('loading data from: {}'.format(file_name))
        pass
            
    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def quit_application(self):
        self.close()

    def test(self):
        """ Simple function used to test stuff during run-time
        """
        logger.info('self.test()')
        logger.info('self.test() done...')
        

        
##################
## Main program ##
##################        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    
    parser = argparse.ArgumentParser(description="PyMona genetic algorithm framework")
    parser.add_argument('target_image', metavar='TARGET_IMAGE',
                        help='The target image that the evolution is aiming at')
    parser.add_argument('-l', '--log-level', dest='log_level', default = 'debug', 
        help    = "Log level. Only log messages with a level higher or equal than this will be printed. Default: 'warn'", 
        choices = ('debug', 'info', 'warn', 'error', 'critical'))
    
    args = parser.parse_args()

    logging.basicConfig(level = args.log_level.upper(), 
        format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')

    logger.info('Started {}'.format(PROGRAM_NAME))
    window = MainWindow(target_image = args.target_image)
    window.show()
    exit_code = app.exec_()
    logger.info('Done {}'.format(PROGRAM_NAME))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
    
    