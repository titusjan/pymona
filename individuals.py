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

from libimg import render_qgraphics_scene
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
        #self._graphics_scene.setBackgroundBrush(Qt.ligthGray)
        self._graphics_scene.setBackgroundBrush(QtGui.QColor(127, 127, 127))
        
        self._chromosomes = chromosomes
        self._add_chromosomes_to_scene()

        
    def clone(self):
        new_chromosomes = [chr.clone() for chr in self._chromosomes]
        return QtGsIndividual(new_chromosomes, self._img_width, self._img_height)
        

    @property
    def image(self):
        return render_qgraphics_scene(self.graphics_scene, self._img_width, self._img_height)
        
    @property
    def graphics_scene(self):
        return self._graphics_scene
        
    def _add_chromosomes_to_scene(self):
        for chromosome in self._chromosomes:
            for qitem in chromosome.get_graphic_items():
                self._graphics_scene.addItem(qitem)
            
            


#############
## Testing ##
############# 
    
if __name__ == '__main__':

    import sys
    from libimg import render_qgraphics_scene

    def test():
    
        img_width = 400
        img_height = 300
        
        if True:
            x, w = 0, img_width
            y, h = 0, img_height 
            rect = (x, y, w, h)
            
        else:
            # Let the x value vary from -0.5 to 1.5 width
            # Let the y value vary from -0.5 to 1.5 height
            x, w = -0.5 * img_width,  2 * img_width
            y, h = -0.5 * img_height, 2 * img_height 
            rect = (x, y, w, h)
        
        alt = 1
        chromos = []
        
        if alt == 0:
            n_poly = 200
            alpha = 15
            chromos = []
            chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect, color = (255, 0, 0, alpha)) )
            chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect, color = (0, 255, 0, alpha)) )
            chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect, color = (0, 0, 255, alpha)) )
        if alt == 1:
            n_poly = 2
            alpha = 255
            chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect, color = (0, 0, 0, alpha)) )
        elif alt == 2:
            chromos.append( QtGsPolyChromosome.create_random(4, 150, rect) )
        else:
            assert False, "invalid alternative"
        
        individual = QtGsIndividual( chromos, img_width, img_height)
        
        img = individual.image
        logger.info('saving: individual.png')
        img.save("individual.png")
        
        
    def main():
    
        logging.basicConfig(level = 'DEBUG', 
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started...')
        app = QtGui.QApplication(sys.argv)
        test()
        logger.info('Done...')
        

if __name__ == '__main__':
    main()
    
    