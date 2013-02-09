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

# Define constants for the depth dimension when an image is converted to a Width x Height x Depth array
# Qt uses ARGB (or BGRA in little endian) when the format is RGB32, ARGB32 or ARGB32_Premultiplied

QT_LITTLE_ENDIAN_MODE = True
assert QT_LITTLE_ENDIAN_MODE, "Big endian mode not tested yet"

if QT_LITTLE_ENDIAN_MODE:
    QT_DEPTH_B = 0
    QT_DEPTH_G = 1
    QT_DEPTH_R = 2
    QT_DEPTH_A = 3
    QT_SLICE_RGB = slice(0, 3)
else:
    QT_DEPTH_A = 0
    QT_DEPTH_R = 1
    QT_DEPTH_G = 2
    QT_DEPTH_B = 3
    QT_SLICE_RGB = slice(1, 4)
    
# MatPlotLib uses RGBA when saving an image. 
MPL_DEPTH_R = 0
MPL_DEPTH_G = 1
MPL_DEPTH_B = 2
MPL_DEPTH_A = 3


def qt_image_to_array(img):
    """ Creates a numpy array from a QImage.
    """
    assert type(img) == QtGui.QImage, "img must be a QtGui.QImage object" 
    img_size = img.size()
    buffer = img.constBits()
        
    # Sanity check
    n_bits_buffer = len(buffer) * 8
    n_bits_image  = img_size.width() * img_size.height() * img.depth()
    assert n_bits_buffer == n_bits_image, \
        "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image) 
        
    assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())
        
    return np.ndarray(shape  = (img_size.width(), img_size.height(), img.depth()//8), 
                      buffer = buffer, 
                      dtype  = np.uint8)



def array_to_qt_image(arr, format = None):
    """ Creates QImage from a numpy array.
    
        If format is not set it will default to QtGui.QImage.Format.Format_RGB32
    """
    assert type(arr) == np.ndarray, "arr must be a numpy array"
    if format == None:
        format = QtGui.QImage.Format.Format_RGB32
        
    assert arr.dtype == np.uint8, "Array must be of type np.uint8"
    assert arr.ndim == 3, "Array must be width x height x 4 array"
    arr_width, arr_height, arr_depth = arr.shape
    assert arr_depth == 4, "Array depth must be 4. Got: {}".format(arr_depth)
    buffer = arr.data
        
    qimg = QtGui.QImage(buffer, arr_width, arr_height, format)
    return qimg


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
    

def score_rgb(arr):
    return np.sum(arr[:,:,QT_SLICE_RGB])
    
    
def render_qgraphics_scene(qgraphics_scene, width, height, format = None):
    """ Renders a graphics scene to an qimage of width by height
    """
    if format is None:
        format = QtGui.QImage.Format.Format_RGB32  # ARGB32 is slow!
        
    image = QtGui.QImage(width, height, format) 
    painter = QtGui.QPainter(image)
    qgraphics_scene.render(painter, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
    painter.end() # make sure the painter is inactive before it is destroyed
    return image
    
    

#############
## Testing ##
############# 
    

if __name__ == '__main__':

    def test1():
    
        #img = QtGui.QImage("images/mona_lisa_300x300.jpg")
        img = QtGui.QImage("images/mona_sister_300x300.jpg")
        
        arr = qt_image_to_array(img)
        save_qt_img_array_fo_file('mona_lisa_out.png', arr)
        
    
    def test():
        
        img1 = QtGui.QImage("images/mona_lisa_300x300.jpg")
        arr1 = qt_image_to_array(img1)
        sum1 = score_rgb(arr1)
        img2 = QtGui.QImage("images/mona_sister_300x300.jpg")
        arr2 = qt_image_to_array(img2)
        sum2 = score_rgb(arr2)   
        
        max_sum = (arr1[:,:,QT_SLICE_RGB].size) * 255 # Width * Height * 3 * 255 
        
        print ("Sum arr1 = {}, arr2 = {}, Avg = {}".format(sum1, sum2, (sum1+sum2)/2) )
        print ("Rel sum arr1 = {:5.3f}, arr2 = {:5.3f}, Avg = {:5.3f}"
            .format(sum1/max_sum, sum2/max_sum, (sum1+sum2)/2/max_sum) )
        
        avg = image_array_average(arr1, arr2)
        diff = image_array_abs_diff(arr1, arr2) 
        
        sum_avg  = score_rgb(avg)
        sum_diff = score_rgb(diff)
        
        # Avg sum may not be the same because of the integer division
        print ("Sum avg = {}, diff = {}".format(sum_avg, sum_diff))
        print ("Rel sum avg = {:5.3f}, diff = {:5.3f}".format(sum_avg/max_sum, sum_diff/max_sum))
        
        save_qt_img_array_fo_file('mona_lisa_out.png', diff)
        
        qimg_diff = array_to_qt_image(diff)
        qimg_diff.save('mona_lisa_qt_out.png')
        


    def main():
    
        logging.basicConfig(level = 'DEBUG', 
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started {}'.format(__name__))
        test()
        logger.info('Done {}'.format(__name__))


if __name__ == '__main__':
    main()
    
    