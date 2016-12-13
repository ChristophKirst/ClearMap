# -*- coding: utf-8 -*-
"""
Functions to remove background in images

The main routine subtracts a morphological opening from the original image 
for background removal.
    
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy

import cv2 

from ClearMap.ImageProcessing.Filter.StructureElement import structureElement
from ClearMap.ImageProcessing.StackProcessing import writeSubStack

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter

from ClearMap.Visualization.Plot import plotTiling

import ClearMap.IO as io


def removeBackground(img, removeBackgroundParameter = None, size = None, save = None, verbose = False,
                     subStack = None, out = sys.stdout, **parameter):
    """Remove background via subtracting a morphological opening from the original image 
    
    Background removal is done z-slice by z-slice.
    
    Arguments:
        img (array): image data
        removeBackGroundParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *size*    (tuple or None)      size for the structure element of the morphological opening
                                           if None, do not correct for any background
            *save*    (str or None)        file name to save result of this operation
                                           if None dont save to file
            *verbose* (bool or int)        print / plot information about this step                                 
            ========= ==================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: background corrected image
    """
    
    size = getParameter(removeBackgroundParameter, "size", size);
    save = getParameter(removeBackgroundParameter, "save", save);    
    verbose = getParameter(removeBackgroundParameter, "verbose", verbose);   
    
    if verbose:
        writeParameter(out = out, head = 'Background Removal:', size = size, save = save);    
    
    if size is None:    
        return img;
        
    img = io.readData(img);
    
    # change type to float in order to prevent 
    dtype = img.dtype;
    img = numpy.array(img, dtype = float);
    
    timer = Timer();
    # background subtraction in each slice
    se = structureElement('Disk', size).astype('uint8');
    for z in range(img.shape[2]):
         #img[:,:,z] = img[:,:,z] - grey_opening(img[:,:,z], structure = structureElement('Disk', (30,30)));
         #img[:,:,z] = img[:,:,z] - morph.grey_opening(img[:,:,z], structure = self.structureELement('Disk', (150,150)));
         img[:,:,z] = img[:,:,z] - cv2.morphologyEx(img[:,:,z], cv2.MORPH_OPEN, se)
    
    img[img < 0] = 0;
    img = numpy.array(img, dtype = dtype);
    
    if not save is None:
        writeSubStack(save, img, subStack = subStack)

    if verbose > 1:
        plotTiling(10*img);

    if verbose:
        out.write(timer.elapsedTime(head = 'Background') + '\n');
    
    return img
