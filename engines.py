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
from environments import QtImgEnvironment


class Engine(object):

    def __init__(self, environment):
        """ Engine that executes the evolutoin

        """
        self._gen_nr = 0
        self._environment = environment
        self._individual = self._initial_individual() # one indiv for now
        self._environment.individual = self._individual
        self._current_score = self._environment.fitness_score
        
        
    def _initial_individual(self):
    
        target_img = self._environment.target_image
        
        rect = get_image_rectangle(target_img, margin_relative = 0.25)
        
        chromos = []
        n_poly = 250
        chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect) )
        
        return QtGsIndividual(chromos, target_img.width(), target_img.height())
                
 
    def next_generation(self):
        
        logger.info("Generation = {:5d}, score = {:8.6f}"
                     .format(self._gen_nr, self._environment.fitness_score))
        
        new_individual = self._individual.clone()

        self._environment.individual = new_individual
        new_score = self._environment.fitness_score 
        old_score = self._current_score
        
        if new_score < old_score:
            logger.debug("using new individual")
            self._current_score = new_score
        else:
            # place back old individual ( this must be implemented different)
            logger.debug("using old individual")
            self._environment.individual = self._individual
            self._current_score = self._environment.fitness_score
            
        self._individual = self._environment.individual

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
        target_image = QtGui.QImage(target_image_name)
        environment = QtImgEnvironment(target_image)

        output_dir = 'output'
        file_name = os.path.join(output_dir, 'engine.target.png')
        logger.info('Saving: {}'.format(file_name))
        environment.target_image.save(file_name)
        
        engine = Engine(environment)
        
        n_generations = 100000
        for gen in range(n_generations):
            engine.next_generation()
            
            if gen % 100 == 0:
                file_name = os.path.join(output_dir, 
                                        'engine.individual.gen_{:05d}.score_{:08.6f}.png'
                                            .format(gen, engine._current_score))
                logger.info('Saving: {}'.format(file_name))
                environment.individual.image.save(file_name)

                file_name = os.path.join(output_dir, 
                                        'engine.fitness.gen_-{:05d}.score_{:08.6f}.png'
                                            .format(gen, engine._current_score))
                logger.info('Saving: {}'.format(file_name))
                environment.fitness_image.save(file_name)
                        
 
        
    def main():
    
        import argparse
    
        parser = argparse.ArgumentParser(description='Stand alone run of the evolution engine.')
        parser.add_argument('target_image', metavar='TARGET_IMAGE', nargs='?',
                           help='The target image that the evolution is aiming at')

        parser.add_argument('-l', '--log-level', dest='log_level', default = 'info', 
            help    = "Log level. Default: 'info'", 
            choices = ('debug', 'info', 'warn', 'error', 'critical'))
        
        args = parser.parse_args()    
            
        logging.basicConfig(level = args.log_level.upper(),
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)16s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started...')
        app = QtGui.QApplication(sys.argv)
        run(args.target_image)
        logger.info('Done...')
        

if __name__ == '__main__':
    main()
    
    