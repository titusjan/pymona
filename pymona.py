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

    def __init__(self, target_image = None):
    
        super(MainWindow, self).__init__()

        self.setup_menu()
        self.setup_models()
        self.setup_views()

        self.setWindowTitle("PyMona")
        self.setGeometry(50, 50, 800, 600)
        
        #if file_names != None:
        #    self.openFiles(file_names)             
        

    def setup_menu(self):
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

        
    def setup_models(self):
        """ Sets up table models """
        
        self.model = QtGui.QStandardItemModel(0, 2, self)
        self.model.setHeaderData(COL_ID,         QtCore.Qt.Horizontal, "ID")
        self.model.setHeaderData(COL_NUM_GENES,  QtCore.Qt.Horizontal, "# genes")
        
        self.graphics_scene = QtGui.QGraphicsScene(self)
        
        #self.graphics_scene.setSceneRect(-20, -20, 420, 340)
        
        
        self.graphics_scene.setSceneRect(0, 0, 300, 300) # TODO 300x200

        if True:        
            # Draw black boundary around the scene rect
            #self.graphics_scene.addRect(self.graphics_scene.sceneRect())
            bw = 2.0 # border width
            hbw = bw / 4.0
            pen = QtGui.QPen()
            pen.setWidth(bw)
            sr = self.graphics_scene.sceneRect()
            if False:
                self.graphics_scene.addRect(sr.x()+hbw, sr.y()+hbw, 
                                            sr.width()-bw, sr.height()-bw, 
                                            pen=pen)
            else:
                self.graphics_scene.addRect(sr.x()-hbw, sr.y()-hbw, 
                                            sr.width(), sr.height(), 
                                            pen=pen)

            logger.debug("self.graphics_scene.sceneRect(): {}".format(self.graphics_scene.sceneRect()))       
        
            target_pixmap = QtGui.QPixmap("images/mona_lisa_300x300.jpg")
            #self.graphics_scene.addPixmap(target_pixmap)
            
            color = QtGui.QColor(255, 0, 0, 255)
            pen = QtGui.QPen(color)
            pen.setWidth(5)
            pen.setStyle(QtCore.Qt.NoPen)
            self.graphics_scene.addEllipse(50, 60, 80, 60, 
                pen = pen, 
                brush = QtGui.QBrush(color))

            color = QtGui.QColor(0, 255, 0, 255)
            pen = QtGui.QPen(color)
            pen.setWidth(5)
            pen.setStyle(QtCore.Qt.NoPen)
            self.graphics_scene.addEllipse(150, 60, 60, 80, 
                pen = pen, 
                brush = QtGui.QBrush(color))

            color = QtGui.QColor(0, 0, 255, 255)
            pen = QtGui.QPen(color)
            pen.setWidth(5)
            pen.setStyle(QtCore.Qt.NoPen)
            self.graphics_scene.addEllipse(50, 160, 70, 70, 
                pen = pen, 
                brush = QtGui.QBrush(color))

        
        brush_color = QtGui.QColor(100, 150, 200, 255)
        pen_color =  QtGui.QColor(200, 0, 0, 255)
        pen = QtGui.QPen(pen_color)
        pen.setWidth(0)
        #pen.setStyle(QtCore.Qt.NoPen)
        self.graphics_scene.addRect(0, 0, 10, 10, 
            pen = pen, 
            brush = QtGui.QBrush(brush_color))
        
            
    def load_model(self, file_name):
        """ Loads the model data from a HDF-5 file"""
        assert False, "Not yet implemented"
        logger.debug('loading data from: {}'.format(file_name))
        pass


    def setup_views(self):
    
        central_splitter = QtGui.QSplitter(self, orientation = Qt.Vertical)
        central_splitter.setStretchFactor(0, 0)
        central_splitter.setStretchFactor(1, 1)
        self.setCentralWidget(central_splitter)
        
        # -- canvas --

        results_group_box = QtGui.QGroupBox("Results")
        central_splitter.addWidget(results_group_box)
        
        results_layout = QtGui.QVBoxLayout()
        results_group_box.setLayout(results_layout)

        self.graphics_view = QtGui.QGraphicsView(self.graphics_scene)
        results_layout.addWidget(self.graphics_view)

        # -- table --
        
        data_group_box = QtGui.QGroupBox("Data")
        central_splitter.addWidget(data_group_box)
        
        data_layout = QtGui.QVBoxLayout()
        data_group_box.setLayout(data_layout)
        
        self.genes_table = QtGui.QTableView()  
        self.genes_table.setModel(self.model)
        self.genes_table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers) 
        self.genes_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.genes_table.setColumnWidth(COL_ID, 400)
        self.genes_table.setColumnWidth(COL_NUM_GENES, 200)
        self.genes_table.horizontalHeader().setStretchLastSection(True)
        
        selection_model = self.genes_table.selectionModel()
        #selection_model.selectionChanged.connect(self.onSelectionChanged)
        
        data_layout.addWidget(self.genes_table)

        
    def __not_used__openFiles(self, file_names=None):
        
        if not file_names:
            file_names = QtGui.QFileDialog.getOpenFileNames(self,
                    "Choose one or more data files", '', '*.h5')[0]
        for file_name in file_names:
            logger.info("Loading data from: {!r}".format(file_name))
            #self.load_model(file_name)


            
    def test(self):
        """ Simple function used to test stuff during run-time
        """
        logger.info('self.test()')
        logger.info('self.test() done...')
        
        
            
    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def quit_application(self):
        self.close()
        
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
    
    