#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Functions that work on images.

    The matplotlib functionality is purely for debugging puproses.

"""
from __future__ import print_function
from __future__ import division

import copy, sys
import logging
logger = logging.getLogger(__name__)

import numpy as np
import matplotlib.image as mpimg

from PySide import QtCore, QtGui

# Define constants for the depth dimension when an image is converted to a Width x Height x Depth array
# Qt uses ARGB (or BGRA in little endian) when the format is RGB32, ARGB32 or ARGB32_Premultiplied

QT_LITTLE_ENDIAN_MODE = True
assert QT_LITTLE_ENDIAN_MODE, "Big endian mode not tested yet"
# TODO: look at QImage.InvertMode

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

def share_data(arr1, arr2):
    """ Returns True if arr1 and arr2 share a data buffer"""
    return addr(arr1) == addr(arr2)


def addr(arr):
    """ Returns pointer to memmory addres.
    
        Is not the same as arr.data
    """
    return arr.__array_interface__['data'][0]
    
    
def offset(arr, idx):
    """ Returns the offset of arr[idx[0], idx[1], ...]
    
        idx must be np.ndarray
    """
    offset = sum(arr.strides * idx)
    return offset + addr(arr)
    
    
def qt_image_buffer_repr(img):
    """ Repr function of the buffer of a Qimage.
    
        This contains the actual addres of the buffer after 'ptr'
    """
    return repr(img.constBits())


def qt_image_to_array(img, share_memory=False):
    """ Creates a numpy array from a QImage.
    
        If share_memory is True, the numpy array and the QImage is shared.
        Be careful: make sure the numpy array is destroyed before the image, 
        otherwise the array will point to unallocated memory!!
    """
    assert type(img) == QtGui.QImage, "img must be a QtGui.QImage object" 
    assert img.format() == QtGui.QImage.Format.Format_RGB32, \
        "img format must be QImage.Format.Format_RGB32, got: {}".format(img.format())
        
    img_size = img.size()
    buffer = img.constBits()
    #logger.debug("qt_image_to_array: buffer: {}".format(repr(buffer)))
    #buffer = img.bits() 
    #buffer = img.scanLine(0)
        
    # Sanity check
    n_bits_buffer = len(buffer) * 8
    n_bits_image  = img_size.width() * img_size.height() * img.depth()
    assert n_bits_buffer == n_bits_image, \
        "size mismatch: {} != {}".format(n_bits_buffer, n_bits_image) 
        
    assert img.depth() == 32, "unexpected image depth: {}".format(img.depth())

    # Note the different width height parameter order!
    arr = np.ndarray(shape  = (img_size.height(), img_size.width(), img.depth()//8),
                     buffer = buffer, 
                     dtype  = np.uint8)

    #logger.debug("qt_image_to_array, arr address: 0x{:x}".format(addr(arr)))
    if share_memory:
        assert False, "Not yet properly tested"
        return arr
    else:
        cpy = copy.deepcopy(arr)
        #logger.debug("qt_image_to_array, deepcopy(arr) address: 0x{:x}".format(addr(cpy)))
        return cpy


def array_to_qt_image(arr, share_memory=True, format = None):
    """ Creates QImage from a numpy array.

        If share_memory is True, the numpy array and the QImage is shared.
        Be carefull: make sure the image is destroyed before the numpy array , 
        otherwise the image will point to unallocated memory!!
    
        If format is not set it will default to QtGui.QImage.Format.Format_RGB32
    """
    logger.debug("--array_to_qt_image")
    assert type(arr) == np.ndarray, "arr must be a numpy array"
    if format == None:
        format = QtGui.QImage.Format.Format_RGB32
        
    assert arr.dtype == np.uint8, "Array must be of type np.uint8"
    assert arr.ndim == 3, "Array must be width x height x 4 array"
    
    # Note the different width/height parameter order!        
    arr_height, arr_width, arr_depth = arr.shape
    assert arr_depth == 4, "Array depth must be 4. Got: {}".format(arr_depth)
    
    if share_memory:
        buf = arr.data
        #assert False, "Not yet properly tested"
    else:
        #buf = copy.deepcopy(arr).data # gaat dit goed? Moeten we een np.copy gebruiken? 
                                       # flags anders? bijv readonly, updateifcopy
                                      
                                       # TODO write arr address here. SAve the deepcopy
        cpy = copy.deepcopy(arr)
        #logger.debug("arr address: 0x{:x}".format(addr(arr)))
        #logger.debug("cpy address: 0x{:x}".format(addr(cpy)))
        buf = cpy.data # probeer de buffer te vullen om zo te achterhalen of hij gebruikt wordt
        # hij wordt waarschijnlijk overscheven door de volgende image.render(). voeg een poly toe aan de scene om te checken.
        
        #logging.debug("buffer type: {}, size: {}, buf[0]: {!r}".format(type(buf), len(buf), buf[0]))
        #print(repr(buf)) # wat betekend offset 0 at 0x104ccc770>? Kijk naar QT images data sharing
        #memview = memoryview(buf)
        #logger.debug("bufsize: {}".format(len(memview) * memview.itemsize))
        
    qimg = QtGui.QImage(buf, arr_width, arr_height, format) 
    return qimg



def qt_arr_to_mpl_arr(arr_qt):
    """ Converts array originating from a QT image to an image to use in matplotlib.imsave()
    
        Permutates the depth dimension of a (w,h,d=4) array from ARGB/BGRA to RGBA
    """
    
    """ Saves a (width x height x depth) array to file
    """
    assert arr_qt.ndim == 3, "arr_qt should be 3 dimensional"
    assert arr_qt.shape[2] == 4, "arr_qt shape should be (width, height, 4)"
    assert arr_qt.dtype == np.uint8, "arr_qt should be of type np.uint8"
    arr_mpl = np.ndarray(shape = arr_qt.shape, dtype = np.uint8)
    logger.debug("qt_arr_to_mpl_arr, arr_mpl : 0x{:x}".format(addr(arr_mpl)))
    
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
    # First divide by two to prevent overflow
    return arr1 // 2 + arr2 // 2


def image_array_abs_diff_8bit(arr1, arr2):
    """ Returns abs(arr1-arr2) for unsigned integers
    """
    logger.debug("image_array_abs_diff_8bit")
    assert arr1.shape == arr2.shape, "array shapes not equal"
    logger.debug("id(arr1.data): 0x{:x}".format(addr(arr1))) 
    logger.debug("id(arr2.data): 0x{:x}".format(addr(arr2))) 

    
    assert share_data(arr1, arr2) is False, "arr1 and arr2 share a data buffer"
    # Note: this debug info can only be used if the arrays are in MPL order
    #mpimg.imsave('/Users/titusjan/Temp/python/arr1_before.8bit.png', arr1, vmin=0, vmax=255)      
    #mpimg.imsave('/Users/titusjan/Temp/python/arr2_before.8bit.png', arr2, vmin=0, vmax=255)      

    diff = np.where( np.greater_equal(arr1, arr2), arr1-arr2, arr2-arr1)
    diff[:,:,QT_DEPTH_A] = 255

    #mpimg.imsave('/Users/titusjan/Temp/python/arr1_after.8bit.png', arr1, vmin=0, vmax=255)      
    #mpimg.imsave('/Users/titusjan/Temp/python/arr2_after.8bit.png', arr2, vmin=0, vmax=255)      
    #mpimg.imsave('/Users/titusjan/Temp/python/diff.8bit.png', diff, vmin=0, vmax=255)      

    assert share_data(diff, arr1) is False, "Sanity check failed: diff and arr1 share a databuffer"
    assert share_data(diff, arr2) is False, "Sanity check failed: diff and arr2 share a databuffer"
    assert arr1.base is None, "arr1 base should be None"
    assert arr2.base is None, "arr2 base should be None"
    assert diff.base is None, "diff base should be None"
    
    return diff
    

def image_array_abs_diff_16bit(arr1, arr2):
    """ Returns abs(arr1-arr2) for unsigned integers
    """
    logger.debug("image_array_abs_diff_16bit")
    diff = np.abs(arr1.astype(np.int16) - arr2.astype(np.int16)).astype(np.uint8)
    diff[:,:,QT_DEPTH_A] = 255
    return diff
    
image_array_abs_diff = image_array_abs_diff_8bit    
#image_array_abs_diff = image_array_abs_diff_16bit    
    

def score_rgb(arr):
    " The total pixel value in the RGB channels"
    return np.sum(arr[:,:,QT_SLICE_RGB])
    
def max_score_rgb(arr):
    " The maximum possible total pixel value in the RGB channels (= width * height * 3 * 255)"
    return arr[:,:,QT_SLICE_RGB].size * 255
    
    
def render_qgraphics_scene(qgraphics_scene, width, height, format = None):
    """ Renders a graphics scene to an qimage of width by height
    """
    if format is None:
        format = QtGui.QImage.Format.Format_RGB32  # ARGB32 is slow!
        
    image = QtGui.QImage(width, height, format)        
    #image = QtGui.QImage(width, height, QtGui.QImage.Format.Format_RGB32) # TODO use format parameter
    painter = QtGui.QPainter(image)
    logger.debug("render_qgraphics_scene image buffer: {}".format(qt_image_buffer_repr(image)))
    qgraphics_scene.render(painter, aspectRatioMode = QtCore.Qt.IgnoreAspectRatio)
    painter.end() # make sure the painter is inactive before it is destroyed
    return image
    
    
def get_image_rectangle(image, margin_relative = 0.0):
    """ Gets the image rectangle as a (x, y, width, height) tuple.
        
        Adds a relative margin to the rectangle
    """
    x_margin = margin_relative * image.width()
    y_margin = margin_relative * image.height()

    return (-x_margin, -y_margin, 
            image.width() + 2*x_margin, image.height() + 2*y_margin)

#############
## Testing ##
############# 
    

if __name__ == '__main__':

 
    def test():
        
        #img1 = QtGui.QImage("images/mona_lisa_300x300.jpg")
        #img1 = QtGui.QImage("images/dots.png").convertToFormat(QtGui.QImage.Format.Format_RGB32)
        #img1 = QtGui.QImage("output/engine.individual.gen_00000.score_0.396956.mpl.png").convertToFormat(QtGui.QImage.Format.Format_RGB32)  # this works
        img1 = QtGui.QImage("output/engine.individual.gen_00000.score_0.396956.qt.png").convertToFormat(QtGui.QImage.Format.Format_RGB32)    # this too
        arr1 = qt_image_to_array(img1)
        sum1 = score_rgb(arr1)
        save_qt_img_array_fo_file('libimg.source_manual.png', arr1)

        img1.save('libimg.source_manual.qt.png')        
        
        
        #img2 = QtGui.QImage("images/mona_sister_300x300.jpg")
        #img2 = QtGui.QImage("images/target_manual.png").convertToFormat(QtGui.QImage.Format.Format_RGB32)
        img2 = QtGui.QImage("individual.png").convertToFormat(QtGui.QImage.Format.Format_RGB32)
        arr2 = qt_image_to_array(img2)
        sum2 = score_rgb(arr2)   
        save_qt_img_array_fo_file('libimg.target_manual.png', arr2)
        
        max_sum = (arr1[:,:,QT_SLICE_RGB].size) * 255 # Width * Height * 3 * 255 
        
        print ("Sum arr1 = {}, arr2 = {}, Avg = {}".format(sum1, sum2, (sum1+sum2)/2) )
        print ("Rel sum arr1 = {:5.3f}, arr2 = {:5.3f}, Avg = {:5.3f}"
            .format(sum1/max_sum, sum2/max_sum, (sum1+sum2)/2/max_sum) )
        
        avg = image_array_average(arr1, arr2)
        #diff = image_array_abs_diff(arr1, arr2) 
        diff = image_array_abs_diff_8bit(arr1, arr2) 
        
        sum_avg  = score_rgb(avg)
        sum_diff = score_rgb(diff)
        
        # Avg sum may not be the same because of the integer division
        print ("Sum avg = {}, diff = {}".format(sum_avg, sum_diff))
        print ("Rel sum avg = {:5.3f}, diff = {:5.3f}".format(sum_avg/max_sum, sum_diff/max_sum))
        
        save_qt_img_array_fo_file('libimg.mpl.png', diff)
        
        qimg_diff = array_to_qt_image(diff)
        qimg_diff.save('libimg.qt.png')
        


    def main():
    
        logging.basicConfig(level = 'DEBUG', 
            #format='%(filename)20s:%(lineno)-4d : %(levelname)-7s: %(message)s')
            format='%(asctime)s: %(filename)20s:%(lineno)-4d : %(levelname)-6s: %(message)s')
            
        logger.info('Started {}'.format(__name__))
        test()
        logger.info('Done {}'.format(__name__))


if __name__ == '__main__':
    main()
    
    