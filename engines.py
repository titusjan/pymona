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
                    score_rgb, max_score_rgb, addr)  

class Engine(object):

    def __init__(self, target_image):
        """ Engine that executes the evolution

        """
        self._gen_nr = 0
        self._target_image = target_image
        self._target_arr = qt_image_to_array(target_image)
        self._max_score_rgb = max_score_rgb(self._target_arr)
        self._individual = self._create_initial_individual(n_poly=3) # one individual for now
        self._indiv_score, self._fitness_image = self.score_individual(self._individual)
        
        
    def _create_initial_individual(self, n_poly):
    
        rect = get_image_rectangle(self._target_image, margin_relative = 0.25)
        
        chromos = []
        chromos.append( QtGsPolyChromosome.create_random(n_poly, 3, rect) )
        
        return QtGsIndividual(chromos, 
                              self._target_image.width(), 
                              self._target_image.height())
                
 
    def score_individual(self, individual):
        """ Compares the individual with the target image and assigns a score.
        
            The score is between 0 and 1, lower is better.
            Returns: (score, comparison image) tuple.
        """
        
        def log_array_info(name, arr):
            
            row = 150
            col = 100
            logger.debug("{:18s}: id = 0x{:x}, data_addr = 0x{:x}, arr[{},{},:] = {}".format(
                name, id(arr), addr(arr), row, col, arr[row,col,:]))
            
            
        individual_arr = qt_image_to_array(individual.render_image())
        log_array_info("individual_arr", individual_arr)
        log_array_info("self._target_arr", self._target_arr)
        
        fitness_arr = image_array_abs_diff(self._target_arr, individual_arr)
        log_array_info("fitness_arr", fitness_arr)
        
        from libimg import save_qt_img_array_fo_file
        
        score = score_rgb(fitness_arr) / self._max_score_rgb
        fitness_image = array_to_qt_image(fitness_arr)
        
        #save_qt_img_array_fo_file('fitness_arr_after.png', fitness_arr)  # enabling this line makes the bug disappear
        log_array_info("fitness_arr", fitness_arr)
        
        
        return score, fitness_image
        
 
    def next_generation(self):
        
        logger.info("Generation = {:5d}, score = {:8.6f}"
                     .format(self._gen_nr, self._indiv_score))
        
        prev_score = self._indiv_score
        
        cur_individual = self._individual.clone(sigma_vertex = 25.0,
                                                sigma_color  = 10.0,
                                                sigma_z      = 0.0,
                                                min_z        = 0,
                                                max_z        = 1023, 
                                                min_alpha    = 0,
                                                max_alpha    = 255)
        cur_score, cur_fitness_image = self.score_individual(cur_individual)
        
        logger.debug("prev_score {}, cur_score {}".format(prev_score, cur_score))
        
        if cur_score < prev_score:
            logger.debug("using new individual")
            self._indiv_score = cur_score
            self._individual = cur_individual
            self._fitness_image = cur_fitness_image
            #assert False
        else:
            logger.debug("using old individual")
            pass
            #assert False

            
        self._gen_nr += 1


#############
## Testing ##
############# 
    
if __name__ == '__main__':

    import numpy.random
    import os.path
    from libimg import get_image_rectangle, save_qt_img_array_fo_file
    
    def old_run(target_image_name):
        
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
                indiv_image = engine._individual.render_image()
                logger.info('Saving: {}'.format(file_name))
                indiv_image.save(file_name)
                
                logger.info('Saving: {}'.format(file_name))
                engine._individual.image.save(file_name)

                file_name = os.path.join(output_dir, 
                                        'engine.fitness.gen_{:05d}.score_{:08.6f}.png'
                                        .format(gen, engine._indiv_score))
                logger.info('Saving: {}'.format(file_name))
                engine._fitness_image.save(file_name)
                        
 

    
    def run(target_image_name):
        
        numpy.random.seed(2)
        
        logger.info("Loading target image: {}".format(target_image_name))
        assert os.path.exists(target_image_name), "file not found: {}".format(target_image_name)
        target_image = QtGui.QImage(target_image_name).convertToFormat(QtGui.QImage.Format.Format_RGB32)

        output_dir = 'output'
        file_name = os.path.join(output_dir, 'engine.target.png')
        logger.info('Saving: {}. Qimage cachekey: {}'.format(file_name, target_image.cacheKey()))
        target_image.save(file_name)
    
        engine = Engine(target_image)

        n_generations = 1
        for gen in range(n_generations):
            if True or gen % 25 == 0:
                
                file_name = os.path.join(output_dir, 
                                        'engine.individual.gen_{:05d}.score_{:08.6f}.qt.png'
                                            .format(gen, engine._indiv_score))
                indiv_image = engine._individual.render_image()  # Disabling this line also makes the bug disappear
                logger.info('Saving: {}. Qimage cachekey: {}'.format(file_name, indiv_image.cacheKey()))
                indiv_image.save(file_name)
                
                if True: # or setting this to false
                    file_name = os.path.join(output_dir, 
                                            'engine.individual.gen_{:05d}.score_{:08.6f}.mpl.png'
                                                .format(gen, engine._indiv_score))
                    logger.info('Saving: {}'.format(file_name))
                    save_qt_img_array_fo_file(file_name, qt_image_to_array(indiv_image))
                    

                fitness_image = engine._fitness_image
            
                file_name = os.path.join(output_dir, 
                                        'engine.fitness.gen_{:05d}.score_{:08.6f}.qt.png'
                                            .format(gen, engine._indiv_score))
                logger.info('Saving: {}. Qimage cachekey: {}'.format(file_name, fitness_image.cacheKey()))
                fitness_image.save(file_name)
                
                            
                if True:
                    file_name = os.path.join(output_dir, 
                                            'engine.fitness.gen_{:05d}.score_{:08.6f}.mpl.png'
                                                .format(gen, engine._indiv_score))
                    logger.info('Saving: {}'.format(file_name))
                    save_qt_img_array_fo_file(file_name, qt_image_to_array(fitness_image))
            
            #engine.next_generation()  # disabling this makes a difference?
            
                        
 
        
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
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)16s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started...')
        app = QtGui.QApplication(sys.argv)
        run(args.target_image)
        logger.info('Done...')
        

if __name__ == '__main__':
    main()
    
    