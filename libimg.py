#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions that work on images.

"""
from __future__ import print_function
from __future__ import division

import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.image as mpimg

from PySide import QtCore, QtGui
from PySide.QtCore import Qt


# Define constants for the depth dimension when an image is converted to a Width x Height x Depth array
# Qt uses ARGB (or BGRA in little endian) when the format is RGB32, ARGB32 or ARGB32_Premultiplied

QT_LITTLE_ENDIAN_MODE = True
assert QT_LITTLE_ENDIAN_MODE, "Big endian mode not tested yet"

if QT_LITTLE_ENDIAN_MODE:
    QT_DEPTH_B = 0
    QT_DEPTH_G = 1
    QT_DEPTH_R = 2
    QT_DEPTH_A = 3
else:
    QT_DEPTH_A = 0
    QT_DEPTH_R = 1
    QT_DEPTH_G = 2
    QT_DEPTH_B = 3
    
# MatPlotLib uses RGBA when saving an image. 
MPL_DEPTH_R = 0
MPL_DEPTH_G = 1
MPL_DEPTH_B = 2
MPL_DEPTH_A = 3


def qt_image_to_array(img):
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
        
    assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())
        
    return np.ndarray(shape  = (img_size.width(), img_size.height(), img.depth()//8), 
                      buffer = buffer, 
                      dtype  = np.uint8)
  


def qt_arr_to_mpl_arr(arr_qt):
    """ Converts array originating from a QT image to an image to use in matplotlib.imsave()
    
        Permutates the depth dimension of a (w,h,d=4) array from ARGB/BGRA to RGBA
    """
    
    """ Saves a (width x height x depth) array to file
    """
    arr_mpl = np.ndarray(shape = arr_qt.shape, dtype = np.uint8)
    
    arr_mpl[:,:,MPL_DEPTH_R] = arr_qt[:,:,QT_DEPTH_R]
    arr_mpl[:,:,MPL_DEPTH_G] = arr_qt[:,:,QT_DEPTH_G]
    arr_mpl[:,:,MPL_DEPTH_B] = arr_qt[:,:,QT_DEPTH_B]
    arr_mpl[:,:,MPL_DEPTH_A] = arr_qt[:,:,QT_DEPTH_A]
    
    return arr_mpl

def save_qt_img_array_fo_file(file_name, arr_qt):
    """ Saves (w,h,d=4) array (with depth in Qt order) to a file
    """
    arr_mpl = qt_arr_to_mpl_arr(arr_qt)
    mpimg.imsave(file_name, arr_mpl, vmin=0, vmax=255)        
    
 
def image_array_average(arr1, arr2):
    """ Returns (arr1-arr2)/2 for unsigned integers
    """
    # First devide by two to prevent overflow
    return arr1 // 2 + arr2 // 2

def image_array_abs_diff(arr1, arr2):
    """ Returns abs(arr1-arr2) for unsigned integers
    """
    diff = np.where( np.greater_equal(arr1, arr2), arr1-arr2, arr2-arr1)
    diff[:,:,QT_DEPTH_A] = 255
    return diff
    
    
def test1():

    #img = QtGui.QImage("images/mona_lisa_300x300.jpg")
    img = QtGui.QImage("images/mona_sister_300x300.jpg")
    
    arr = qt_image_to_array(img)
    save_qt_img_array_fo_file('mona_lisa_out.png', arr)
    

def test():

    img1 = QtGui.QImage("images/mona_lisa_300x300.jpg")
    arr1 = qt_image_to_array(img1)
    img2 = QtGui.QImage("images/mona_sister_300x300.jpg")
    arr2 = qt_image_to_array(img2)
   
    #result = image_array_average(arr1, arr2)
    result = image_array_abs_diff(arr1, arr2) 
    
    save_qt_img_array_fo_file('mona_lisa_out.png', result)
    

    
 
def main():

    logging.basicConfig(level = 'DEBUG', 
        #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
        format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
        
    logger.info('Started {}'.format(__name__))
    test()
    logger.info('Done {}'.format(__name__))
    

if __name__ == '__main__':
    main()
    
    