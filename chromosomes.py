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
        assert poly_genes.ndim == 3, "poly_genes must be 3D np.array (n_genes, n_vertices, 2)"
        n_poly_genes, n_vertices, n_xy = poly_genes.shape
        assert n_xy == 2, "poly_genes 3rd dimension must have size 2 (x&y coordinatess)."

        assert color_genes.ndim == 2, "Genes must be 3D np.array (n_genes, rgba)"
        n_color_genes, n_rgba = color_genes.shape
        assert n_color_genes == n_poly_genes, \
            "First dimension of poly_genes and color_genes must have the same length"
        assert n_rgba == 4, "color_genes 2nd dimension must have size 4 (rgba)."
        
        self._poly_genes = poly_genes
        self._color_genes = color_genes
        
    
    def get_graphic_items(self):
        """ Returns a list with the QGraphicItem representation of each gene
        """
        qitems = []
        for poly_gene, color_gene in zip(self._poly_genes, self._color_genes):
            qpoints = [QtCore.QPointF(row[0], row[1]) for row in poly_gene]
            qcolor = QtGui.QColor(*color_gene) # unpack tuple 
            qpoly = QtGui.QPolygonF(qpoints)
            qitem = QtGui.QGraphicsPolygonItem(qpoly)
            qitem.setPen(NO_PEN)
            qitem.setBrush(QtGui.QBrush(qcolor))
            qitems.append(qitem)
        return qitems
        
    
    @staticmethod
    def create_random(n_genes, n_vertices, x, y, width, height):
        """ Creates random QtGsPolyChromosome"""
        
        poly_genes = np_rnd.rand(n_genes, n_vertices, 2)
        poly_genes[:,:,0] = width  * poly_genes[:,:,0] + x
        poly_genes[:,:,1] = height * poly_genes[:,:,1] + y
        
        color_genes = np_rnd.random_integers(0, 255, size = (n_genes, 4)).astype(np.uint8)

        return QtGsPolyChromosome(poly_genes, color_genes)
    
