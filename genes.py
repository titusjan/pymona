#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Environment classes

"""
from __future__ import print_function
from __future__ import division

import numpy as np
import types
import logging
logger = logging.getLogger(__name__)

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

            
NO_PEN = QtGui.QPen()
NO_PEN.setStyle(QtCore.Qt.NoPen)

class QtgPolyGene(QtGui.QGraphicsPolygonItem):

    def __init__(*args, **kw_args):
        super(QtgPolyGene, self).__init__(*args, **kw_args)
        
        
    @staticmethod
    def create_filled_poly(points = None, color = None ):
        """ Creates a QtPolyGene object from a list of points
            
            points : must be either a list of (x,y) tuples, 
                     or must be an r by 2 numpy array [[x1, y1], [x2, y2], ...]
            color  : must be (r, g, b, a) tuple
        """
        if points is None:
            qpoints = []
        elif type(points) == types.TupleType or type(points) == types.ListType:
            qpoints = [QtCore.QPointF(x, y) for (x,y) in points]
        elif type(points) == np.ndarray:
            assert points.ndim == 2, "Points must be 2 dimensional"
            n_rows, n_cols = points.shape
            assert n_cols == 2, "points must be an r by 2 array"
            qpoints = [QtCore.QPointF(row[0], row[1]) for row in points]
        else:
            assert False, "Invalid type: {}".format(type(points))
            
        if color is None:
            qcolor = QtGui.QColor(0, 0, 0, 0)
        elif (type(color) == types.TupleType or 
              type(color) == types.ListType or 
              type(color) == np.ndarray):
            qcolor = QtGui.QColor(*color) # unpack tuple
        elif type(color) == QtGui.QColor:
            qcolor = color
        else:
            qcolor = QtGui.QColor(color)
            
        qpoly = QtGui.QPolygonF(qpoints)
        qitem = QtGui.QGraphicsPolygonItem(qpoly)
        qitem.setPen(NO_PEN)
        qitem.setBrush(QtGui.QBrush(qcolor))
        return qitem
    
    
                