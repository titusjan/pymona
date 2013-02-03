#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Environment classes

"""
from __future__ import print_function
from __future__ import division

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
        """ Creates a QtPolyGene object from a list of (x,y) tuples.
        
            Color must be (r, g, b, a) tuple
        """
        if points is None:
            points = []
            
        if color is None:
            qcolor = QtGui.QColor(0, 0, 0, 0)
        else:
            qcolor = QtGui.QColor(*color) # unpack tuple
            
        print (qcolor)
            
        qpoints = [QtCore.QPointF(x, y) for (x,y) in points]
        qpoly = QtGui.QPolygonF(qpoints)
        qitem = QtGui.QGraphicsPolygonItem(qpoly)
        qitem.setPen(NO_PEN)
        qitem.setBrush(QtGui.QBrush(qcolor))
        return qitem
    
    
                