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

class Environment(object):  # Abstract base class
    pass
    

class QtGsEnvironment(Environment):

    def __init__(self):
        """ Qt grapics scene environment.
        
            An environment that can make a QGraphicsScene of itself
        """
        self._graphics_scene = QtGui.QGraphicsScene(None)
        print (self._graphics_scene)
        
    

def test():
    app = QtGui.QApplication(sys.argv)
    environment = QtGsEnvironment()
    
    
def main():

    logging.basicConfig(level = 'DEBUG', 
        #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
        format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        
    logger.info('Started...')
    test()
    logger.info('Done...')
    

if __name__ == '__main__':
    main()
    
    