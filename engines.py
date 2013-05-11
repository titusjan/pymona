#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Evolution engine

"""
from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger(__name__)

import sys

from PySide import QtCore, QtGui

from chromosomes import QtGsPolyChromosome
from individuals import QtGsIndividual
from libimg import (qt_image_to_array, array_to_qt_image, image_array_abs_diff, 
                    score_rgb, max_score_rgb, addr)  

        
def log_array_info(name, arr):
    row = 150
    col = 100
    logger.debug("{:18s}: id = 0x{:x}, data_addr = 0x{:x}, arr[{},{},:] = {}".format(
        name, id(arr), addr(arr), row, col, arr[row,col,:]))
            

class Engine(object):

    def __init__(self, target_image):
        """ Engine that executes the evolution

        """
        self._max_alpha = 100
        
        self._gen_nr = 0
        self._target_image = target_image
        self._target_arr = qt_image_to_array(target_image)
        self._max_score_rgb = max_score_rgb(self._target_arr)
        self._individual = self._create_initial_individual(n_poly=100) 
        self._indiv_score, self._fitness_image = self.score_individual(self._individual)
        self._score_changed = True
        
        
    def _create_initial_individual(self, n_poly):
        """ Creates a single individual to begin with 
        """
        rect = get_image_rectangle(self._target_image, margin_relative = 0.25)
        
        chromos = []
        chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect, 
                                                         max_alpha = self._max_alpha) )
        
        return QtGsIndividual(chromos, 
                              self._target_image.width(), 
                              self._target_image.height())
                
    
    def score_individual(self, individual):
        """ Compares the individual with the target image and assigns a score.
        
            The score is between 0 and 1, lower is better.
            Returns: (score, comparison image) tuple.
        """
        individual_arr = qt_image_to_array(individual.render_image())
        fitness_arr = image_array_abs_diff(self._target_arr, individual_arr)
        score = score_rgb(fitness_arr) / self._max_score_rgb
        fitness_image = array_to_qt_image(fitness_arr)
        return score, fitness_image
        
 
    def next_generation(self):
        
        #logger.info("Generation = {:5d}, score = {:8.6f}"
        #             .format(self._gen_nr, self._indiv_score))
        
        prev_score = self._indiv_score
        cur_individual = self._individual.clone(sigma_vertex = 5.0,
                                                sigma_color  = 2.0,
                                                sigma_z      = 1.0,
                                                min_z        = 0,
                                                max_z        = 1023, 
                                                min_alpha    = 0,
                                                max_alpha    = self._max_alpha)
        cur_score, cur_fitness_image = self.score_individual(cur_individual)
        
        #logger.debug("prev_score {}, cur_score {}".format(prev_score, cur_score))
        
        if cur_score < prev_score:
            self._score_changed = True
            self._indiv_score = cur_score
            self._individual = cur_individual
            self._fitness_image = cur_fitness_image
        else:
            self._score_changed = False
            pass

        self._gen_nr += 1


#############
## Testing ##
############# 
    
if __name__ == '__main__':

    import numpy.random
    import os.path
    from libimg import get_image_rectangle
    
    def run(target_image_name):
        
        numpy.random.seed(2)
        
        logger.info("Loading target image: {}".format(target_image_name))
        assert os.path.exists(target_image_name), "file not found: {}".format(target_image_name)
        target_image = QtGui.QImage(target_image_name)

        output_dir = 'output'
        file_name = os.path.join(output_dir, 'engine.target.png')
        logger.info('Saving: {}'.format(file_name))
        target_image.save(file_name)
        
        engine = Engine(target_image)

        n_generations = 100000
        for gen in range(n_generations):
            engine.next_generation()
            
            #if gen % 125 == 0:
            if engine._score_changed:
                file_name = os.path.join(output_dir, 
                                        'engine.individual.gen_{:05d}.score_{:08.6f}.png'
                                        .format(gen, engine._indiv_score))
                indiv_image = engine._individual.render_image()
                logger.info('Saving: {}'.format(file_name))
                indiv_image.save(file_name)
                
                fitness_image = engine._fitness_image
            
                file_name = os.path.join(output_dir, 
                                        'engine.fitness.gen_{:05d}.score_{:08.6f}.qt.png'
                                            .format(gen, engine._indiv_score))
                #logger.info('Saving: {}'.format(file_name))
                fitness_image.save(file_name)
                
        
    def main():
    
        import argparse
    
        parser = argparse.ArgumentParser(description='Stand alone run of the evolution engine.')
        
        parser.add_argument('target_image', metavar='TARGET_IMAGE',
                           help='The target image that the evolution is aiming at')

        parser.add_argument('-l', '--log-level', dest='log_level', default = 'info', 
            help    = "Log level. Default: 'info'", 
            choices = ('debug', 'info', 'warn', 'error', 'critical'))
        
        args = parser.parse_args()    
            
        logging.basicConfig(level = args.log_level.upper(), stream = sys.stderr, 
            format='%(asctime)s: %(filename)16s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started...')
        app = QtGui.QApplication(sys.argv)
        run(args.target_image)
        logger.info('Done...')
        

if __name__ == '__main__':
    main()
    
    