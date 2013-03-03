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
#from environments import QtImgEnvironment
from libimg import (qt_image_to_array, array_to_qt_image, image_array_abs_diff, 
                    score_rgb, max_score_rgb)  

class Engine(object):

    def __init__(self, target_image):
        """ Engine that executes the evolution

        """
        self._gen_nr = 0
        self._target_image = target_image
        self._target_arr = qt_image_to_array(target_image)
        self._max_score_rgb = max_score_rgb(self._target_arr)
        self._individual = self._initial_individual() # one indiv for now
        self._indiv_score, self._fitness_image = self.score_individual(self._individual)
        
        
    def _initial_individual(self):
    
        rect = get_image_rectangle(self._target_image, margin_relative = 0.25)
        
        chromos = []
        n_poly = 100
        chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect) )
        
        return QtGsIndividual(chromos, 
                              self._target_image.width(), 
                              self._target_image.height())
                
 
    def score_individual(self, individual):
        """ Compares the individual with the target image and assigns a score.
        
            The score is between 0 and 1, lower is better.
            Returns: (score, comparison image) tuple.
        """
    
        individual_arr = qt_image_to_array(individual.image)
        fitness_arr = image_array_abs_diff(self._target_arr, individual_arr)
        score = score_rgb(fitness_arr) / self._max_score_rgb
        fitness_image = array_to_qt_image(fitness_arr)
        return score, fitness_image
        
 
    def next_generation(self):
        
        logger.info("Generation = {:5d}, score = {:8.6f}"
                     .format(self._gen_nr, self._indiv_score))
        
        prev_score = self._indiv_score
        
        cur_individual = self._individual.clone()
        cur_score, cur_fitness_image = self.score_individual(cur_individual)
        
        #logger.debug("prev_score {}, cur_score {}".format(prev_score, cur_score))
        
        if cur_score < prev_score:
            logger.debug("using new individual")
            self._indiv_score = cur_score
            self._individual = cur_individual
            self._fitness_image = cur_fitness_image
        else:
            #logger.debug("using old individual")
            pass

            
        self._gen_nr += 1


#############
## Testing ##
############# 
    
if __name__ == '__main__':

    import sys, os.path
    import numpy as np
    from libimg import get_image_rectangle
    
    def run(target_image_name):
        
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
            
            if gen % 100 == 0:
                file_name = os.path.join(output_dir, 
                                        'engine.individual.gen_{:05d}.score_{:08.6f}.png'
                                            .format(gen, engine._indiv_score))
                logger.info('Saving: {}'.format(file_name))
                engine._individual.image.save(file_name)

                file_name = os.path.join(output_dir, 
                                        'engine.fitness.gen_{:05d}.score_{:08.6f}.png'
                                            .format(gen, engine._indiv_score))
                logger.info('Saving: {}'.format(file_name))
                engine._fitness_image.save(file_name)
                        
 
        
    def main():
    
        import argparse
    
        parser = argparse.ArgumentParser(description='Stand alone run of the evolution engine.')
        
        parser.add_argument('target_image', metavar='TARGET_IMAGE',
                           help='The target image that the evolution is aiming at')

        parser.add_argument('-l', '--log-level', dest='log_level', default = 'info', 
            help    = "Log level. Default: 'info'", 
            choices = ('debug', 'info', 'warn', 'error', 'critical'))
        
        args = parser.parse_args()    
            
        logging.basicConfig(level = args.log_level.upper(), stream = sys.stdout, 
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)16s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started...')
        app = QtGui.QApplication(sys.argv)
        run(args.target_image)
        logger.info('Done...')
        

if __name__ == '__main__':
    main()
    
    