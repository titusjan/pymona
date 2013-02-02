#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


COL_ID        = 0
COL_NUM_GENES = 1


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
        self.setGeometry(50, 50, 800, 600)
        
        #if file_names != None:
        #    self.openFiles(file_names)             
        
            
    def about(self):
        QtGui.QMessageBox.about(self, "About %s" % PROGRAM_NAME, ABOUT_MESSAGE)

    def fileQuit(self):
        self.close()


    def setupMenu(self):
        """ Sets up the main menu.
        """
        fileMenu = QtGui.QMenu("&File", self)
        #openAction = fileMenu.addAction("&Open...", self.openFiles)
        #openAction.setShortcut("Ctrl+O")
        openAction = fileMenu.addAction("&Test...", self.test)
        openAction.setShortcut("Ctrl+T")
        quitAction = fileMenu.addAction("E&xit", self.fileQuit)
        quitAction.setShortcut("Ctrl+Q")
        
        helpMenu = QtGui.QMenu('&Help', self)
        helpMenu.addAction('&About', self.about)

        self.menuBar().addMenu(fileMenu)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(helpMenu)

        
    def setupModels(self):
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
        
            
    def loadModel(self, file_name):
        """ Loads the model data from a HDF-5 file"""
        assert False, "Not yet implemented"
        logger.debug('loading data from: {}'.format(file_name))
        pass


    def setupViews(self):
    
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
            #self.loadModel(file_name)
            

  
    def __not_used__onSelectionChanged(self, selected=None, deselected=None):
        """ Makes the selected result the reference result
        
            Called when a row is selected in the table.
        """
        logger.debug("onSubtractTableChanged")
        
        selection_model = self.genes_table.selectionModel()
        
        assert len(selection_model.selectedRows()) == 1, \
            "Only one row should be select, got: {}".format(len(selection_model.selectedRows()) )
        selection = selection_model.selectedRows()[0]
        self.ref_idx = selection.row()
        logger.debug("Reference is now: {}".format(self.ref_idx))
        

    def __not_used__onSubtractTableChanged(self, top_left_index=None, botrom_right_index=None):
        """ Called when an item in the dark subract table has changed
        """
        logger.debug("onSubtractTableChanged")
        pass
        
 
    def __not_used__getTableItem(self, row, col):
        return self.model.data(self.model.index(row, col), Qt.DisplayRole)
    
            
    def test(self):
        """ Simple function used to test stuff during run-time"""
        import numpy as np
        import matplotlib.image as mpimg
        import matplotlib.pyplot as plt
        import inspect
        from pprint import pprint
        logger.info('self.test()')
        
        # user scene.render
        paint_image = QtGui.QImage(300, 300, QtGui.QImage.Format.Format_ARGB32) # ARGB32 is slow!
        #paint_image = QtGui.QImage(300, 300, QtGui.QImage.Format.Format_RGB32)
        logger.debug(paint_image.format())
        logger.debug("image depth: {}".format(paint_image.depth()))
        
        painter = QtGui.QPainter(paint_image)
        logger.debug(paint_image.format())
        logger.debug("image depth: {}".format(paint_image.depth()))
        
        
        self.graphics_scene.render(painter, 
                                   source = self.graphics_scene.sceneRect(),
                                   #target = QtCore.QRectF(50, 50, 100, 200), 
                                   aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)

        
        image = paint_image
        logger.debug(image.format())
        logger.debug("image depth: {}".format(image.depth()))
        
        img_size = image.size() # QSize object
        logger.debug(img_size) 

        #buffer = image.bits()
        buffer = image.constBits()
        logger.debug(type(buffer))
        logger.debug(len(buffer))
        for idx, elem in enumerate(buffer[0:32]):
            logger.debug("buffer[{0}] = {1} ({2} {2:x})".format(idx, elem, ord(elem)))
        assert img_size.width() * img_size.height() * image.depth() == len(buffer) * 8, \
            "size mismatch: {} != {}".format(img_size.width() * img_size.height() * image.depth(), len(buffer) * 8) 


        #return # TODO: remove
        if True:
            #img_arr = np.ndarray(shape=(img_size.width(), img_size.height()), dtype=np.uint32, buffer=buffer)
            img_arr = np.ndarray(shape=(img_size.width(), img_size.height()), 
                #dtype=[('a', np.uint8), ('r', np.uint8), ('g', np.uint8), ('b', np.uint8)],  #ARGB32
                dtype=[('b', np.uint8), ('g', np.uint8), ('r', np.uint8), ('a', np.uint8)],   #ARGB32
                buffer=buffer)

        img_rgba = np.ndarray(shape=(img_size.width(), img_size.height(), 4), dtype = np.uint8)
            
        if True:
            img_rgba[:,:,0] = img_arr[:]['r']
            img_rgba[:,:,1] = img_arr[:]['g']
            img_rgba[:,:,2] = img_arr[:]['b']
            img_rgba[:,:,3] = img_arr[:]['a']
        else:            
            img_rgba[:,:,0] = img_arr[:]['b']
            img_rgba[:,:,1] = img_arr[:]['g']
            img_rgba[:,:,2] = img_arr[:]['r']
            img_rgba[:,:,3] = img_arr[:]['a']
        

        #mpimg.imsave('image.png', img_arr, vmin=0, vmax=255)
        mpimg.imsave('image.png', img_rgba, vmin=0, vmax=255)
        
        if False:
            bytes = QtCore.QByteArray()
            buffer = QtCore.QBuffer(bytes)
            buffer.open(QtCore.QIODevice.WriteOnly)
            pix_map.save("test.png", "PNG") # writes pixmap into bytes in PNG format
            logger.debug(buffer.size())

        painter.end()
        logger.debug("Painter is active: {}".format(painter.isActive()))
        
        logger.info('self.test() done...')
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    
    parser = argparse.ArgumentParser(description='Compare irradiances measured with the ESA GSTP Radiometer')
    parser.add_argument('file_names', metavar='FILE', nargs='*', help='files to compare')
    parser.add_argument('-l', '--log-level', dest='log_level', default = 'debug', 
        help    = "Log level. Only log messages with a level higher or equal than this will be printed. Default: 'warn'", 
        choices = ('debug', 'info', 'warn', 'error', 'critical'))
    
    args = parser.parse_args()

    logging.basicConfig(level = args.log_level.upper(), 
        #format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')

    logger.info('Started {}'.format(PROGRAM_NAME))
    window = MainWindow(file_names = args.file_names)
    window.show()
    exit_code = app.exec_()
    logger.info('Done {}'.format(PROGRAM_NAME))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
    
    