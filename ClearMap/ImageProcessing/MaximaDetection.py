# -*- coding: utf-8 -*-
"""
Collection of routines to detect maxima

Used for finding cells or intensity peaks.

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy

#from scipy.ndimage import maximum_filter
import scipy.ndimage.measurements as sm;

#import scipy
#from skimage.filters.rank import tophat
#from skimage.measure import regionprops
#from mahotas import regmin
#from mahotas import locmax
from scipy.ndimage.filters import maximum_filter

from ClearMap.ImageProcessing.GreyReconstruction import reconstruct
from ClearMap.ImageProcessing.Filter.StructureElement import structureElementOffsets
from ClearMap.ImageProcessing.StackProcessing import writeSubStack
#from ClearMap.ImageProcessing.Convolution import convolve

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter;
from ClearMap.Visualization.Plot import plotOverlayLabel




##############################################################################
# Basic Transforms
##############################################################################

   
def hMaxTransform(img, hMax):
    """Calculates h-maximum transform of an image
    
    Arguments:
        img (array): image
        hMax (float or None): h parameter of h-max transform
        
    Returns:
        array: h-max transformed image if h is not None
    """
    
    #seed = img.copy();
    #seed[seed < h] = h; # catch errors for uint subtraction !
    #img = img.astype('float16'); # float32 ? 
    if not hMax is None:
        return reconstruct(img - hMax, img);
    else:
        return img;



def localMax(img, size = 5):
    """Calculates local maxima of an image
        
    Arguments:
        img (array): image
        size (float or None): size of volume to search for maxima
        
    Returns:
        array: mask that is True at local maxima
    """
    
    if size is None:
        return img;
    
    if not isinstance(size, tuple):
       size = (size, size, size);

    #return regmin(-img, regionalMaxStructureElement);
    #return (maximum_filter(img, footprint = regionalMaxStructureElement) == img);
    return (maximum_filter(img, size = size) == img)
    
      
#def regionalMax(img, regionalMaxStructureElement = numpy.ones((3,3,3), dtype = bool)):
#    """Calculates regional maxima of an image."""
#   
#    return regmin(-img, regionalMaxStructureElement);

    
def extendedMax(img, hMax = 0):
    """Calculates extened h maxima of an image
    
    Extended maxima are the local maxima of the h-max transform
   
    Arguments:
        img (array): image
        hMax (float or None): h parameter of h-max transform
        
    Returns:
        array: extended maxima of the image
    """

    #h max transformimport scipy
    if not(hMax is None) and hMax > 0:
        img = hMaxTransform(img, hMax);
        
    #max
    #return regionalMax(img);
    return localMax(img);


##############################################################################
# Maxima Detection 
##############################################################################



def findExtendedMaxima(img, findExtendedMaximaParameter = None, hMax = None, size = 5, threshold = None, save = None, verbose = None,
                       subStack = None,  out = sys.stdout, **parameter):
    """Find extended maxima in an image 
    
    Effectively this routine performs a h-max transfrom, followed by a local maxima search and 
    thresholding of the maxima.
    
    Arguments:
        img (array): image data
        findExtendedMaximaParameter (dict):
            =========== =================== ===========================================================
            Name        Type                Descritption
            =========== =================== ===========================================================
            *hMax*      (float or None)     h parameter for the initial h-Max transform
                                            if None, do not perform a h-max transform
            *size*      (tuple)             size for the structure element for the local maxima filter
            *threshold* (float or None)     include only maxima larger than a threshold
                                            if None keep all localmaxima
            *save*      (str or None)       file name to save result of this operation
                                            if None do not save result to file
            *verbose*   (bool or int)        print / plot information about this step                                             
            =========== =================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: binary image with True pixel at extended maxima
        
    See Also:
        :func:`hMaxTransform`, :func:`localMax`
    """
    
    hMax      = getParameter(findExtendedMaximaParameter, "hMax", hMax);
    size      = getParameter(findExtendedMaximaParameter, "size", size);
    threshold = getParameter(findExtendedMaximaParameter, "threshold", threshold);
    save      = getParameter(findExtendedMaximaParameter, "save", save);
    verbose   = getParameter(findExtendedMaximaParameter, "verbose", verbose);

    if verbose:
        writeParameter(out = out, head = 'Extended Max:', hMax = hMax, size = size, threshold = threshold, save = save);
    
    timer = Timer();
    
    ## extended maxima    
    imgmax = hMaxTransform(img, hMax);
        
    #imgmax = regionalMax(imgmax, regionalMaxStructureElement);
    imgmax = localMax(imgmax, size);
    
    #thresholding    
    if not threshold is None:
        imgmax = numpy.logical_and(imgmax, img >= threshold);
    
    if verbose > 1:
        #plotTiling(img)
        plotOverlayLabel(img * 0.01, imgmax.astype('int64'), alpha = False);
        #plotOverlayLabel(img, imgmax.astype('int64'), alpha = True)     

    if not save is None:#
        writeSubStack(save, imgmax.astype('int8'), subStack = subStack)
        
    if verbose:
        out.write(timer.elapsedTime(head = 'Extended Max') + '\n');
    
    return imgmax



def findCenterOfMaxima(img, imgmax = None, label = None, findCenterOfMaximaParameter = None, save = None, verbose = False,
                       subStack = None, out = sys.stdout, **parameter):
    """Find center of detected maxima weighted by intensity
    
    Arguments:
        img (array): image data
        findCenterOfMaximaParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *save*    (str or None)        saves result of labeling the differnet maxima
                                           if None, do the lableling is not saved
            *verbose* (bool or int)        print / plot information about this step         
            ========= ==================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
    
    Returns:
        array: coordinates of centers of maxima, shape is (n,d) where n is number of maxima and d the dimension of the image
    """
    
    save    = getParameter(findCenterOfMaximaParameter, "save", save);
    verbose = getParameter(findCenterOfMaximaParameter, "verbose", verbose);
    
    if verbose:
        writeParameter(out = out, head = 'Center of Maxima:', save = save);
    
    timer = Timer(); 

    #center of maxima
    if label is None:
        imglab, nlab = sm.label(imgmax);  
    else:
        imglab = label;
        nlab = imglab.max();
       
    #print 'max', imglab.shape, img.shape
    #print imglab.dtype, img.dtype
    
    if not save is None:
        writeSubStack(save, imglab, subStack = subStack);
    
    if nlab > 0:
        centers = numpy.array(sm.center_of_mass(img, imglab, index = numpy.arange(1, nlab)));    
    
        if verbose > 1:  
            #plotOverlayLabel(img * 0.01, imglab, alpha = False);
            #plotTiling(img)
            imgc = numpy.zeros(img.shape);
            for i in range(centers.shape[0]):
                imgc[centers[i,0], centers[i,1], centers[i,2]] = 1;
            plotOverlayLabel(img, imgc, alpha = False);
            #plotOverlayLabel(img, imgmax.astype('int64'), alpha = True)     
    
        #return centers, imglab, mask
        #cintensity = numpy.array([img[centers[i,0], centers[i,1], centers[i,2]] for i in range(centers.shape[0])]);
        
        if verbose:
            out.write(timer.elapsedTime(head = 'Cell Centers'));
        
        #return ( centers, cintensity );
        return centers;
        
    else:
        
        if verbose:
            out.write('Cell Centers: No Cells found !');
            #return ( numpy.zeros((0,3)), numpy.zeros(0) );
        
        #return empty set o coordinates
        return numpy.zeros((0,3));
        
        
        
def findPixelCoordinates(imgmax, subStack = None, verbose = False, out = sys.stdout, **parameter):
    """Find coordinates of all pixel in an image with positive or True value
           
    Arguments:
        img (array): image data
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: coordinates of centers of True pixels, shape is (n,d)  where n is number of maxima and d the dimension of the image
    """
    
    timer = Timer(); 
    
    centers = numpy.nonzero(imgmax);
    centers = numpy.vstack(centers).T;
    
    if verbose:
        out.write(timer.elapsedTime(head = 'Cell Centers') + '\n');
    
    return centers;
 


def findIntensity(img, centers, findIntensityParameter = None, method = None, size = (3,3,3), verbose = False, 
                  out = sys.stdout, **parameter):
    """Find instensity value around centers in the image
    
    Arguments:
        img (array): image data
        findIntensityParameter (dict):
            =========== =================== ===========================================================
            Name        Type                Descritption
            =========== =================== ===========================================================
            *method*    (str, func, None)   method to use to determine intensity (e.g. "Max" or "Mean")
                                            if None take intensities at the given pixels
            *size*      (tuple)             size of the box on which to perform the *method*
            *verbose*   (bool or int)       print / plot information about this step 
            =========== =================== ===========================================================
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: measured intensities 
    """
    
    method  = getParameter(findIntensityParameter, "method", "Max"); 
    size    = getParameter(findIntensityParameter, "size", (3,3,3)); 
    verbose = getParameter(findIntensityParameter, "verbose", verbose); 
     
    if verbose:
        writeParameter(out = out, head = 'Cell Intensities:', method = method, size = size);

    timer = Timer(); 
        
    if centers.shape[0] == 0:
        return numpy.zeros(0);
    
    if method is None:
            return numpy.array([img[centers[i,0], centers[i,1], centers[i,2]] for i in range(centers.shape[0])]);        
    
    isize = img.shape;
    #print isize
    
    offs = structureElementOffsets(size);
    
    if isinstance(method, basestring):
        method = eval('numpy.' + method.lower());


    intensities = numpy.zeros(centers.shape[0], dtype = img.dtype);
    
    for c in range(centers.shape[0]):
        xmin = int(-offs[0,0] + centers[c,0]);
        if xmin < 0:
            xmin = 0;       
        xmax = int(offs[0,1] + centers[c,0]);
        if xmax > isize[0]:
            xmax = isize[0];
            
        ymin = int(-offs[1,0] + centers[c,1]);
        if ymin < 0:
            ymin = 0;       
        ymax = int(offs[1,1] + centers[c,1]);
        if ymax > isize[1]:
            ymax = isize[1];
            
        zmin = int(-offs[2,0] + centers[c,2]);
        if zmin < 0:
            zmin = 0;       
        zmax = int(offs[1,1] + centers[c,2]);
        if zmax > isize[2]:
            zmax = isize[2];
        
        #print xmin, xmax, ymin, ymax, zmin, zmax
        data = img[xmin:xmax, ymin:ymax, zmin:zmax];
        
        intensities[c] = method(data);
    
    if verbose:
        out.write(timer.elapsedTime(head = 'Cell Intensities'));
    
    return intensities;

