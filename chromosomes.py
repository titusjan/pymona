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

    def __init__(self, poly_genes, color_genes, z_genes):
        """ Class where each gene can be representated as a polygon (QGraphicsPolyItem).
        
            Each polygon has a color and a z-value (depth).
            All polygons have the same number of vertices. 
            
            poly_genes must be a 3D float array with shape  (n_poly, n_vertices, 2)
            color genes must be a 2D uint8 array with shape (n_poly, 4) or (1,4)
                in the latter case all polygon will share this color
            z_genes must be a 1D array with length n_poly or length 1
                in the latter case all polygons will have the same z-value
        """
        self._poly_genes = poly_genes
        self._color_genes = color_genes
        self._z_genes = z_genes
        
        assert color_genes.dtype == np.uint8, "Color genes must be of type np.uint8"
        
        assert poly_genes.ndim == 3, "poly_genes must be 3D np.array (n_genes, n_vertices, 2)"
        assert poly_genes.shape[2] == 2, "poly_genes 3rd dimension must have size 2 (x&y coordinatess)."

        self._n_colors = color_genes.shape[0]
        assert color_genes.shape == (1,4) or color_genes.shape == (self.n_polygons,4), \
            "color_genes shape must be (1,4) or (n_polygons,4)"

        self._n_z_values = z_genes.shape[0]
        assert z_genes.shape == (1,) or z_genes.shape == (self.n_polygons,), \
            "color_genes length must be 1 or n_polygons"
        
        
    @property
    def n_polygons(self):
        "Returns the number polygons in the chromosome"
        return self._poly_genes.shape[0]
        
    @property
    def n_vertices(self):
        "Returns the number of vertices per polygon"
        return self._poly_genes.shape[1]
        
    @property
    def n_colors(self):
        "Returns the number colors in the gene"
        return self._n_colors
        
    
    def get_graphic_items(self):
        """ Returns a list with the QGraphicItem representation of each gene
        """
        qitems = []
        for idx, poly_gene in enumerate(self._poly_genes):

            if self._n_colors == 1:
                color_gene = self._color_genes[0]
            else:
                color_gene = self._color_genes[idx]
                
            if self._n_z_values == 1:
                z_gene = self._z_genes[0]
            else:
                z_gene = self._z_genes[idx]
                
            qpoints = [QtCore.QPointF(row[0], row[1]) for row in poly_gene]
            qpoly = QtGui.QPolygonF(qpoints)
            qitem = QtGui.QGraphicsPolygonItem(qpoly)
            
            qcolor = QtGui.QColor(*color_gene) # unpack tuple 
            qitem.setBrush(QtGui.QBrush(qcolor))
            qitem.setPen(NO_PEN)
            
            qitem.setZValue(z_gene)
            
            qitems.append(qitem)
            
        return qitems

        
    def clone(self):

        if False:
            noise_poly  = 10.0   * np_rnd.randn(self.n_polygons, self.n_vertices, 2)
            noise_color = 2.5   * np_rnd.randn(self.n_polygons, 4)
            noise_z     = 0.001 * np_rnd.randn(self.n_polygons)
        else:
            noise_poly  = 5.0   * np_rnd.randn(self.n_polygons, self.n_vertices, 2)
            noise_color = 5.0   * np_rnd.randn(self.n_polygons, 4)
            noise_z     = 0.0001 * np_rnd.randn(self.n_polygons)

    
        new_poly_genes  = self._poly_genes  + noise_poly
        new_color_genes = self._color_genes + noise_color
        new_z_genes     = self._z_genes     + noise_z

        
        np.clip(new_color_genes, 0, 255, out = new_color_genes)
        np.clip(new_z_genes, 0.0, 1.0, out = new_z_genes)


        return QtGsPolyChromosome(new_poly_genes, new_color_genes.astype(np.uint8), new_z_genes)
        
    
    @staticmethod
    def create_random(n_polygons, n_vertices, rectangle, 
                      color = None, 
                      z     = None):
        """ Creates random QtGsPolyChromosome.
        
            rectangle should be a (x, y, width, height) tuple.
            
            Will create n_polygons polygons each having n_vertices vertices 
            The vertices vary from (x, y) to (x+width, y+with)
            
            If color is None it will be set randomly, otherwise it must be 
            a 1 by 4 array or (r,g,b,a) tuple and all polygons will have that 
            color.
            
            If z is None it will be set randomly between 0 and 1, otherwise it 
            must be a float and all polygons will have that z value (depth).
        """
        
        x, y, width, height = rectangle
        
        poly_genes = np_rnd.rand(n_polygons, n_vertices, 2)
        poly_genes[:,:,0] *= width  
        poly_genes[:,:,0] += x
        poly_genes[:,:,1] *= height 
        poly_genes[:,:,1] += y
        
        if color == None:
            color_genes = np_rnd.random_integers(0, 255, size = (n_polygons,4)).astype(np.uint8)
        else:
            color_genes = np.array(color).reshape(1,4).astype(np.uint8)
            
        if z == None:
            z_genes = np_rnd.rand(n_polygons) 
        else:
            z_genes = np.array(z).reshape(1)
            
        return QtGsPolyChromosome(poly_genes, color_genes, z_genes)
    

