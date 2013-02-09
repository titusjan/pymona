#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function
from __future__ import division

import numpy as np
import numpy.random as np_rnd
import types
import logging
logger = logging.getLogger(__name__)

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

            
NO_PEN = QtGui.QPen()
NO_PEN.setStyle(QtCore.Qt.NoPen)

class Chromosome(object):
    """ Class that stores a number of genes"""
    pass
    
class QtGsChromosome(Chromosome):
    """ Abstract base class where each gene can be representated as a QtGui.QGraphicsItem
    
        All genes are the same size and represent the same type of graphics item
    """ 

    def as_graphic_items(self):
        """ Returns a list with the QGraphicItem representation of each gene
        """
        assert False, "Abstract class. Please instantiate from a descendant class."
    
    
class QtGsPolyChromosome(Chromosome):

    def __init__(self, poly_genes, color_genes):
        """ Class where each gene can be representated as a QtGui.QGraphicsPolyItem
        
            All genes are the same size and their poly has the same number of vertices.
            
            poly_genes must be a 3D float array with dimensions: n_genes, n_vertices, 2
            color genes must be a 2D uint8 array with dimensions: n_genes, 4
            
            
        """
        self._poly_genes = poly_genes
        self._color_genes = color_genes
        
        assert poly_genes.ndim == 3, "poly_genes must be 3D np.array (n_genes, n_vertices, 2)"
        assert poly_genes.shape[2] == 2, "poly_genes 3rd dimension must have size 2 (x&y coordinatess)."

        self._n_colors = color_genes.shape[0]
        assert color_genes.shape == (1,4) or color_genes.shape == (self.n_polygons,4), \
            "color_genes shape must be (1,4) or (n_vertices,4)"
        
    @property
    def n_polygons(self):
        "Returns the number polygons in the chromosome"
        return self._poly_genes.shape[0]
        
    @property
    def n_vertices(self):
        "Returns the number of vertices per polygon"
        return self._poly_genes.shape[0]
        
    
    def get_graphic_items(self):
        """ Returns a list with the QGraphicItem representation of each gene
        """
        qitems = []
        for idx, poly_gene in enumerate(self._poly_genes):

            if self._n_colors == 1:
                color_gene = self._color_genes[0]
            else:
                color_gene = self._color_genes[idx]
                
            qpoints = [QtCore.QPointF(row[0], row[1]) for row in poly_gene]
            qpoly = QtGui.QPolygonF(qpoints)
            qitem = QtGui.QGraphicsPolygonItem(qpoly)
            
            qcolor = QtGui.QColor(*color_gene) # unpack tuple 
            qitem.setBrush(QtGui.QBrush(qcolor))
            qitem.setPen(NO_PEN)
            
            qitems.append(qitem)
            
        return qitems
        
    
    @staticmethod
    def create_random(n_polygons, n_vertices, x, y, width, height, 
                      color = None):
        """ Creates random QtGsPolyChromosome.
        
            Will create n_polygons polygons each having n_vertices vertices 
            The vertices vary from (x, y) to (x+width, y+with)
            
            If color is None it will be set randomly, otherwise it must be 
            a 1 by 4 array or (r,g,b,a) tuple and all polygons will have that 
            color.
        """
        
        poly_genes = np_rnd.rand(n_polygons, n_vertices, 2)
        poly_genes[:,:,0] *= width  
        poly_genes[:,:,0] += x
        poly_genes[:,:,1] *= height 
        poly_genes[:,:,1] += y
        
        if color == None:
            color_genes = np_rnd.random_integers(0, 255, size = (n_polygons,4)).astype(np.uint8)
        else:
            color_genes = np.array(color).reshape(1,4).astype(np.uint8)
            
        return QtGsPolyChromosome(poly_genes, color_genes)
    
