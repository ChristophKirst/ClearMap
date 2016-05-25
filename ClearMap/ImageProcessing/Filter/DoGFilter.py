# -*- coding: utf-8 -*-
"""
DoG filter module

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys

from scipy.ndimage.filters import correlate
#from scipy.signal import fftconvolve

from ClearMap.ImageProcessing.Filter.FilterKernel import filterKernel

from ClearMap.ImageProcessing.StackProcessing import writeSubStack

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter
from ClearMap.Visualization.Plot import plotTiling


##############################################################################
# Image processing steps in spot detection
##############################################################################


def filterDoG(img, filterDoGParameter = None,  size = None, sigma = None, sigma2 = None, save = None, verbose = None,
              subStack = None, out = sys.stdout, **parameter):
    """Difference of Gaussians (DoG) filter step
    
    Arguments:
        img (array): image data
        filterDoGParameter (dict):
            ========= ==================== ================================================================
            Name      Type                 Descritption
            ========= ==================== ================================================================
            *size*    (tuple or None)      size for the DoG filter 
                                           if None, do not correct for any background
            *sigma*   (tuple or None)      std of outer Guassian, if None autmatically determined from size
            *sigma2*  (tuple or None)      std of inner Guassian, if None autmatically determined from size
            *save*    (str or None)        file name to save result of this operation
                                           if None dont save to file 
            *verbose* (bool or int)        print progress information                            
            ========= ==================== ================================================================
        subStack (dict or None): sub-stack information 
        out (object): object to write progress info to
        
    Returns:
        array: DoG filtered image
    """
    
    timer = Timer();  
    
    dogSize  = getParameter(filterDoGParameter, "size",  size);
    dogSigma = getParameter(filterDoGParameter, "sigma", sigma);
    dogSigma2= getParameter(filterDoGParameter, "sigma2",sigma2);
    dogSave  = getParameter(filterDoGParameter, "save",  save);
    verbose  = getParameter(filterDoGParameter, "verbose",  verbose);
    
    if verbose:
        writeParameter(out = out, head = 'DoG:', size = dogSize, sigma = dogSigma, sigma2 = dogSigma2, save = dogSave);
    #DoG filter
    img = img.astype('float32'); # always convert to float for downstream processing
        
    if not dogSize is None:
        fdog = filterKernel(ftype = 'DoG', size = dogSize, sigma = dogSigma, sigma2 = dogSigma2);
        fdog = fdog.astype('float32');
        #img = correlate(img, fdog);
        #img = scipy.signal.correlate(img, fdog);
        img = correlate(img, fdog);
        #img = convolve(img, fdog, mode = 'same');
        img[img < 0] = 0;
    
    if verbose > 1:
        plotTiling(img);
    
    if not dogSave is None:
        writeSubStack(dogSave, img, subStack = subStack);
    
    if verbose:
        out.write(timer.elapsedTime(head = 'DoG') + '\n');
    
    return img
