# -*- coding: utf-8 -*-
"""
Linear filter module

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


def filterLinear(img, filterLinearParameter = None, ftype = None, size = None, sigma = None, sigma2 = None, save = None, 
                 subStack = None, verbose = False, out = sys.stdout, **parameter):
    """Applies a linear filter to the image
    
    Arguments:
        img (array): image data
        filterLinearParameter (dict):
            ========= ==================== ================================================================
            Name      Type                 Descritption
            ========= ==================== ================================================================
            *ftype*   (str or None)        the type of the filter, see :ref:`FilterTypes`
                                           if None do ot perform any fitlering
            *size*    (tuple or None)      size for the filter 
                                           if None, do not perform filtering
            *sigma*   (tuple or None)      std of outer Guassian, if None autmatically determined from size
            *sigma2*  (tuple or None)      std of inner Guassian, if None autmatically determined from size
            *save*    (str or None)        file name to save result of this operation
                                           if None dont save to file 
            *verbose* (bool or int)        print progress information       
            ========= ==================== ================================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: filtered image
        
    Note:
        Converts image to float32 type if filter is active!
    """
    
    timer = Timer();  
    
    ftype   = getParameter(filterLinearParameter, "ftype",  ftype);
    size    = getParameter(filterLinearParameter, "size",   size);
    sigma   = getParameter(filterLinearParameter, "sigma",  sigma);
    sigma2  = getParameter(filterLinearParameter, "sigma2", sigma2);
    save    = getParameter(filterLinearParameter, "save",   save);
    verbose = getParameter(filterLinearParameter, "verbose",verbose);

    if verbose:
        writeParameter(out = out, head = 'Linear Filter:', ftype = ftype, size = size, sigma = sigma, sigma2 = sigma2, save = save);

    if ftype is None:
        return img;
    
    #DoG filter
    img = img.astype('float32'); # always convert to float for downstream processing
        
    if not size is None:
        fil = filterKernel(ftype = ftype, size = size, sigma = sigma, sigma2 = sigma2);
        fil = fil.astype('float32');
        #img = correlate(img, fdog);
        #img = scipy.signal.correlate(img, fdog);
        img = correlate(img, fil);
        #img = convolve(img, fdog, mode = 'same');
        img[img < 0] = 0;
    
    if verbose > 1:
        plotTiling(img);
    
    if not save is None:
        writeSubStack(save, img, subStack = subStack);
    
    if verbose:
        out.write(timer.elapsedTime(head = 'Linear Filter') + '\n');
    
    return img