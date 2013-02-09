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

from chromosomes import QtGsPolyChromosome


class Individual(object):  # Abstract base class
    pass


class QtGsIndividual(Individual):

    def __init__(self, chromosomes, img_width, img_height):
        """ Qt grapics scene individual.
        
            An individual that can make a QGraphicsScene of itself.
            The genes should be a list of QGraphicsItems
            
            chromosomes must be a list of Chromosome objects
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
        
        self._chromosomes = chromosomes
        self._add_chromosomes_to_scene()
        
        
    @property
    def genes(self):
        return self._genes        
        
    @property
    def graphics_scene(self):
        return self._graphics_scene
        
    def _add_chromosomes_to_scene(self):
        for chromosome in self._chromosomes:
            for qitem in chromosome.get_graphic_items():
                self.graphics_scene.addItem(qitem)
            


#############
## Testing ##
############# 
    
if __name__ == '__main__':

    def test():
    
        import sys
        from libimg import render_qgraphics_scene
    
        app = QtGui.QApplication(sys.argv)
    
        img_width = 400
        img_height = 300
        
        if True:
            x, w = 0, img_width
            y, h = 0, img_height 
        else:
            # Let the x value vary from -0.5 to 1.5 width
            # Let the y value vary from -0.5 to 1.5 height
            x, w = -0.5 * img_width,  2 * img_width
            y, h = -0.5 * img_height, 2 * img_height 

        if True:
            chromos = []
            chromos.append( QtGsPolyChromosome.create_random(2, 3, x, y, w, h, color = (255, 0, 0, 100)) )
            chromos.append( QtGsPolyChromosome.create_random(2, 4, x, y, w, h, color = (0, 255, 0, 100)) )
            chromos.append( QtGsPolyChromosome.create_random(2, 5, x, y, w, h, color = (0, 0, 255, 100)) )
            individual = QtGsIndividual( chromos, img_width, img_height)
        else:
            chrrr = QtGsPolyChromosome.create_random(4, 150, x, y, w, h) 
        
        individual = QtGsIndividual( chromos, img_width, img_height)
        
        img = render_qgraphics_scene(individual.graphics_scene, img_width, img_height)
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
    
    