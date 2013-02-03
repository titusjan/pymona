#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions that work on images.

"""
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.image as mpimg

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

        
# Define dtypes for the different image formats (LE = little endian).
# ARGB32 is slow to render on a painter, use either RGB32 or ARGB32_Premultiplied

DTYPE_RGB32_LE = [('b', np.uint8), ('g', np.uint8), ('r', np.uint8), ('a', np.uint8)]
DTYPE_ARGB32_LE = DTYPE_RGB32_LE


def qimg_to_array(img):
    """ Creates a numpy array from a QImage.
    """
    img_size = img.size()
    buffer = img.constBits()
    #buffer = image.bits()
        
    # Sanity check
    n_bits_buffer = len(buffer) * 8
    n_bits_image  = img_size.width() * img_size.height() * img.depth()
    assert n_bits_buffer == n_bits_image, \
        "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image) 

    if img.format() == QtGui.QImage.Format.Format_RGB32:  
        arr_rgba = np.ndarray(shape=(img_size.width(), img_size.height()), buffer=buffer, dtype=DTYPE_RGB32_LE)
    elif img.format() == QtGui.QImage.Format.Format_ARGB32:  
        arr_rgba = np.ndarray(shape=(img_size.width(), img_size.height()), buffer=buffer, dtype=DTYPE_ARGB32_LE)
    else:
        assert False, "Format not implemented: {}".format(img.format()) 

    return arr_rgba
    
    
def rgba_array_to_depth4(arr_rgba):

    """ Creates (width x height x depth) array, where the depth = 4 (rgba).
    
        This can be used in matplot
    """
    width, height = arr_rgba.shape
    arr4 = np.ndarray(shape=(width, height, 4), dtype = np.uint8)
        
    arr4[:,:,0] = arr_rgba[:]['r']
    arr4[:,:,1] = arr_rgba[:]['g']
    arr4[:,:,2] = arr_rgba[:]['b']
    arr4[:,:,3] = arr_rgba[:]['a']
    
    return arr4
    

def save_rgba_array_fo_file(file_name, arr_rgba):
    """ Saves an rbga array to file
    """
    arr4 = rgba_array_to_depth4(arr_rgba)
    mpimg.imsave(file_name, arr4, vmin=0, vmax=255)        
    

def test():

    img = QtGui.QImage("images/mona_lisa_300x300.png")
    
    arr_rgba = qimg_to_array(img)
    save_rgba_array_fo_file('mona_lisa_out.png', arr_rgba)
    

    
 
def main():

    logging.basicConfig(level = 'DEBUG', 
        #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
        format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        
    logger.info('Started {}'.format(__name__))
    test()
    logger.info('Done {}'.format(__name__))
    

if __name__ == '__main__':
    main()
    
    