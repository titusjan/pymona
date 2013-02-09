#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Environment classes

"""
from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger(__name__)

import sys

from PySide import QtCore, QtGui

from libimg import (qt_image_to_array, array_to_qt_image, image_array_abs_diff)
from chromosomes import QtGsPolyChromosome
from individuals import QtGsIndividual


class Environment(object):  # Abstract base class
    pass
    

class QtImgEnvironment(Environment):

    def __init__(self, target_image):
        """ Environment that contains one individual who will be compared with a target_image
        
            The target_image should be a QImage.
        """
        self._target_image   = target_image
        self._target_arr     = None  # cache array of target image
        self._individual     = None
        self._individual_arr = None  # cache array of image of indivual 
        self._fitness_arr    = None  # cache of fitness array
        
    def _clear_cache(self):
        self._individual_arr = None
        self._fitness_arr = None
        logger.debug("cache cleared")

    @property
    def individual(self):
        return self._individual
   
    @individual.setter
    def individual(self, individual):
        self._individual = individual
        self._clear_cache()
   
    @individual.deleter
    def individual(self):
        self._individual = None
        self._clear_cache()
        print ("@individual.deleter called")
    
    @property
    def individual_arr(self):
        assert self.individual != None, "Individual not set"
        if self._individual_arr == None:
            self._individual_arr = qt_image_to_array(self.individual.image) 
        return self._individual_arr  

    @property
    def target_image(self):
        return self._target_image

    @property
    def target_arr(self):
        if self._target_arr == None:
            self._target_arr = qt_image_to_array(self.target_image) 
        return self._target_arr  
        
    @property
    def fitness_arr(self):
        if self._fitness_arr == None:
            self._fitness_arr = image_array_abs_diff(self.target_arr, self.individual_arr)
        return self._fitness_arr 
        
    @property
    def fitness_image(self):
        " Returns the image of the array that is used to determine the fitness score"
        return array_to_qt_image(self.fitness_arr)
        
    @property
    def fitness_score(self):
        " Returns the fitness score of the individual in the environment"
        return score_rgb(self.fitness_arr)
        

#############
## Testing ##
############# 
    
if __name__ == '__main__':

    import sys
    import numpy as np
    
    def test():
        
        target_image = QtGui.QImage(sys.argv[1])
        environment = QtImgEnvironment(target_image)
   
        img_width = target_image.width()
        img_height = target_image.height()
        
        x, w = 0, img_width
        y, h = 0, img_height 

        n_poly = 1
        chromos = []
        #chromos.append( QtGsPolyChromosome.create_random(n_poly, 100, x, y, w, h, color = (150, 125, 100, 255) ) )
        #chromos.append( QtGsPolyChromosome.create_random(n_poly, 4, x, y, w, h, color = (0, 0, 0, 255) ) )
        
        margin = 80
        xmin = x+margin
        ymin = y+margin
        xmax = x+w-margin
        ymax = y+h-margin
        rect = np.array([ [ [xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin] ] ])
        chromos.append( QtGsPolyChromosome(poly_genes = rect,  
                                           #color_genes = np.array([[255, 0, 0, 255]], dtype=np.uint8), 
                                           #color_genes = np.array([[0, 255, 0, 255]], dtype=np.uint8), 
                                           color_genes = np.array([[0, 0, 255, 255]], dtype=np.uint8), 
                                           z_genes = np.array([1])) )
        
        individual = QtGsIndividual( chromos, img_width, img_height)
        
        environment.individual = individual
        file_name = 'environment.target.png'
        logger.info('saving: {}'.format(file_name))
        environment.target_image.save(file_name)
        
        file_name = 'environment.individual.png'
        logger.info('saving: {}'.format(file_name))
        environment.individual.image.save(file_name)
        
        file_name = 'environment.fitness.png'
        logger.info('saving: {}'.format(file_name))
        environment.fitness_image.save(file_name)
        
        
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
    
    