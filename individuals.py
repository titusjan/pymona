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

from genes import QtgPolyGene


class Individual(object):  # Abstract base class
    pass


class QtGsIndividual(Individual):

    def __init__(self, qt_gi_genes, img_width, img_height):
        """ Qt grapics scene individual.
        
            An individual that can make a QGraphicsScene of itself.
            The genes should be a list of QGraphicsItems
            
            img_width and img_heights is the size of the target image in pixels
        """
        self._img_width = int(img_width)
        self._img_height = int(img_height)
        
        # The scene rectangle is one larger than the image size in pixels. 
        # Single pixel goes from coordinage 0.0 up to 1.0, two pixels from 0.0 to 2.0, etc.
        # Just like we need 5 poles to make a fence of 4 meters.
        scene_rect = QtCore.QRectF(0, 0, self._img_width + 1, self._img_height + 1)
        self._graphics_scene = QtGui.QGraphicsScene(scene_rect)
        self._graphics_scene.setBackgroundBrush(Qt.gray)
        
        self._genes = qt_gi_genes
        self._add_genes_to_scene(self._genes)
        
        
    @property
    def genes(self):
        return self._genes        
        
    @property
    def graphics_scene(self):
        return self._graphics_scene
        
    def _add_genes_to_scene(self, genes):
        for gene in genes:
            self.graphics_scene.addItem(gene)
            



def test():

    import sys
    from libimg import render_qgraphics_scene

    app = QtGui.QApplication(sys.argv)
    
    genes = []
    genes.append(QtgPolyGene.create_filled_poly(points = [(0,40), (90, -10), (300, 100), (20,5)], 
                                                color = (255, 0, 0, 255) ))
    genes.append(QtgPolyGene.create_filled_poly(points = [(200, 300), (140, -40), (70,45.4)], 
                                                color = (0, 255, 255, 155)  ))
    
    width = 250
    height = 150
    
    individual = QtGsIndividual(genes, width, height)
    
    img = render_qgraphics_scene(individual.graphics_scene, width, height)
    img.save("individual.png")
    
    
def main():

    logging.basicConfig(level = 'DEBUG', 
        #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
        format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        
    logger.info('Started...')
    test()
    logger.info('Done...')
    

if __name__ == '__main__':
    main()
    
    