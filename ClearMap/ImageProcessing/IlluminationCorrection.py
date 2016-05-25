# -*- coding: utf-8 -*-
"""
Illumination correction toolbox.

The module provides a function to correct illumination/vignetting systematic
variations in intensity.

The intensity image :math:`I(x)` given a flat field :math:`F(x)` and 
a background :math:`B(x)` the image is corrected to :math:`C(x)` as:
     
.. math:
   C(x) = \\frac{I(x) - B(x)}{F(x) - B(x)}

The module also has functionality to create flat field corections from measured 
intensity changes in a single direction, useful e.g. for lightsheet images,
see e.g. :func:`flatfieldLineFromRegression`.

References: 
    Fundamentals of Light Microscopy and Electronic Imaging, p. 421

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy
import os

import matplotlib.pyplot as plt

from scipy.optimize import curve_fit

import ClearMap.IO as io

from ClearMap.ImageProcessing.StackProcessing import writeSubStack

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter

from ClearMap.Visualization.Plot import plotTiling

from ClearMap.Settings import ClearMapPath


DefaultFlatFieldLineFile = os.path.join(ClearMapPath, "Data/lightsheet_flatfield_correction.csv");
"""Default file of points along the illumination changing line for the flat field correction

See Also:
    :func:`correctIllumination`
"""


def correctIllumination(img, correctIlluminationParameter = None, flatfield = None, background = None, scaling = None, save = None, verbose = False, 
                        subStack = None, out = sys.stdout, **parameter):
    """Correct illumination variations
    
     The intensity image :math:`I(x)` given a flat field :math:`F(x)` and 
     a background :math:`B(x)` the image is corrected to :math:`C(x)` as:
     
     .. math:
         C(x) = \\frac{I(x) - B(x)}{F(x) - B(x)}
         
     If the background is not given :math:`B(x) = 0`. 
     
     The correction is done slice by slice assuming the data was collected with 
     a light sheet microscope.
     
     The image is finally optionally scaled.
  
    Arguments:
        img (array): image data
        findCenterOfMaximaParameter (dict):
            ============ ==================== ===========================================================
            Name         Type                 Descritption
            ============ ==================== ===========================================================
            *flatfield*  (str, None or array) flat field intensities, if None d onot correct image for
                                              illumination, if True the 
            *background* (str, None or array) background image as file name or array
                                              if None background is assumed to be zero
            *scaling*    (str or None)        scale the corrected result by this factor
                                              if 'max'/'mean' scale to keep max/mean invariant
            *save*       (str or None)        save the corrected image to file
            *verbose*    (bool or int)        print / plot information about this step 
            ============ ==================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
    
    Returns:
        array: illumination corrected image
        
        
    References: 
        Fundamentals of Light Microscopy and Electronic Imaging, p 421        
        
    See Also:
        :const:`DefaultFlatFieldLineFile`
    """  
    
    flatfield  = getParameter(correctIlluminationParameter, "flatfield",  flatfield);
    background = getParameter(correctIlluminationParameter, "background", background);
    scaling    = getParameter(correctIlluminationParameter, "scaling",    scaling);
    save       = getParameter(correctIlluminationParameter, "save",       save);
    verbose    = getParameter(correctIlluminationParameter, "verbose",    verbose);

    if verbose:    
        if flatfield is None or isinstance(flatfield, str) or flatfield is True:
            fld = flatfield;
        else:
            fld = "image of size %s" % str(flatfield.shape);
    
        if background is None or isinstance(background, str):
            bkg = background;
        else:
            bkg = "image of size %s" % str(background.shape);
        
        writeParameter(out = out, head = 'Illumination correction:', flatfield = fld, background = bkg, scaling = scaling, save = save);  
    
    
    print subStack;
 
    if not subStack is None:
        x = subStack["x"];
        y = subStack["y"];
    else:
        x = all;
        y = all;
    
    #print "sizes", x, y, img.shape
 
    #read data  
 
    timer = Timer(); 
 
    if flatfield is None:
        return img;
        
    elif flatfield is True:
        # default flatfield correction
    
        if subStack is None:    
            flatfield = flatfieldFromLine(DefaultFlatFieldLineFile, img.shape[0]);
        else:
            dataSize = io.dataSize(subStack["source"]);
            flatfield = flatfieldFromLine(DefaultFlatFieldLineFile, dataSize[0]);
            
    elif isinstance(flatfield, str):
        # point or image file
        if io.isPointFile(flatfield):
            if subStack is None:    
                flatfield = flatfieldFromLine(flatfield, img.shape[0]);
            else:
               dataSize = io.dataSize(subStack["source"]);
               flatfield = flatfieldFromLine(flatfield, dataSize[0]);
        else:
            flatfield = io.readData(flatfield);
    
    ffmean = flatfield.mean();    
    ffmax = flatfield.max();

    #correct for subset
    flatfield = io.readData(flatfield, x = x, y = y);   
    
    background = io.readData(background, x = x, y = y);
    
    if flatfield.shape != img[:,:,0].shape:
        raise RuntimeError("correctIllumination: flatfield does not match image size: %s vs %s" % (flatfield.shape,  img[:,:,0].shape));
    
    #convert to float for scaling
    dtype = img.dtype;
    img = img.astype('float32');
    flatfield = flatfield.astype('float32');
    
    # illumination correction in each slice
    if background is None:
        for z in range(img.shape[2]):
            img[:,:,z] = img[:,:,z] / flatfield;
    else:
        if background.shape != flatfield.shape:
            raise RuntimeError("correctIllumination: background does not match image size: %s vs %s" % (background.shape,  img[:,:,0].shape));        
        background = background.astype('float32');

        flatfield = (flatfield - background);
        for z in range(img.shape[2]):
            img[:,:,z] = (img[:,:,z] - background) / flatfield;
    
        
    # rescale
    if scaling is True:
        scaling = "mean";
    
    if isinstance(scaling, str):
        if scaling.lower() == "mean":
            # scale back by average flat field correction:
            sf = ffmean;
        elif scaling.lower() == "max":
            sf = ffmax;
        else:
            raise RuntimeError('Scaling not "Max" or "Mean" but %s' % scaling);
    else:
        sf = scaling;
      
    if verbose:
         writeParameter(out = out, head = 'Illumination correction:',  scaling = sf);
    
        
    
    if not sf is None:
        img = img * sf;
        img = img.astype(dtype);
    
    
    #write result for inspection
    if not save is None:
        writeSubStack(save, img, subStack = subStack);    
    
    #plot result for inspection
    if verbose > 1:
        plotTiling(img);
    
    if verbose:
        out.write(timer.elapsedTime(head = 'Illumination correction') + '\n');    
    
    return img 
    


def flatfieldFromLine(line, xsize):
    """Creates a 2d flat field image from a 1d line of estimated intensities
    
    Arguments:
        lines (array): array of intensities along y axis
        xsize (int): size of image in x dimension
    
    Returns:
        array: full 2d flat field 
    """
    
    line = io.readPoints(line);

    flatfield = numpy.zeros((xsize, line.size));
    for i in range(xsize):
        flatfield[i,:] = line;
    
    return flatfield;



def flatfieldLineFromRegression(data, sink = None, method = 'polynomial', reverse = None, verbose = False):
    """Create flat field line fit from a list of positions and intensities
    
    The fit is either to be assumed to be a Gaussian:
    
    .. math:
        I(x) = a \\exp^{- (x- x_0)^2 / (2 \\sigma)) + b"
        
    or follows a order 6 radial polynomial
        
    .. math:
        I(x) = a + b (x- x_0)^2 + c (x- x_0)^4 + d (x- x_0)^6
    
    Arguments:
        data (array): intensity data as vector of intensities or (n,2) dim array of positions d=0 and intensities measurements d=1:-1 
        sink (str or None): destination to write the result of the fit
        method (str): method to fit intensity data, 'Gaussian' or 'Polynomial'
        reverse (bool): reverse the line fit after fitting
        verbose (bool): print and plot information for the fit
        
    Returns:
        array: fitted intensities on points
    """
    
    data = io.readPoints(data);

    # split data
    if len(data.shape) == 1:
        x = numpy.arange(0, data.shape[0]);
        y = data;
    elif len(data.shape) == 2:
        x = data[:,0]
        y = data[:,1:-1];
    else:
        raise RuntimeError('flatfieldLineFromRegression: input data not a line or array of x,i data');
    
    #calculate mean of the intensity measurements
    ym = numpy.mean(y, axis = 1);

    if verbose:
        plt.figure()
        for i in range(1,data.shape[1]):
            plt.plot(x, data[:,i]);
        plt.plot(x, ym, 'k');
    
    
    if method.lower() == 'polynomial':
        ## fit r^6
        mean = sum(ym * x)/sum(ym)

        def f(x,m,a,b,c,d):
            return a + b * (x-m)**2 + c * (x-m)**4 + d * (x-m)**6;
        
        popt, pcov = curve_fit(f, x, ym, p0 = (mean, 1, 1, 1, .1));
        m = popt[0]; a = popt[1]; b = popt[2];
        c = popt[3]; d = popt[4];

        if verbose:
            print "polynomial fit: %f + %f (x- %f)^2 + %f (x- %f)^4 + %f (x- %f)^6" % (a, b, m, c, m, d, m);

        def fopt(x):
            return f(x, m = m, a = a, b = b, c = c, d = d);
        
        flt = map(fopt, range(0, int(x[-1])));
    
    else: 
        ## Gaussian fit
        
        mean = sum(ym * x)/sum(ym)
        sigma = sum(ym * (x-mean)**2)/(sum(ym))
        
        def f(x, a, m, s, b):
            return a * numpy.exp(- (x - m)**2 / 2 / s) + b;
            
        
        popt, pcov = curve_fit(f, x, ym, p0 = (1000, mean, sigma, 400));
        a = popt[0]; m = popt[1]; s = popt[2]; b = popt[3];

        if verbose:
            print "Gaussian fit: %f exp(- (x- %f)^2 / (2 %f)) + %f" % (a, m, s, b);

        def fopt(x):
            return f(x, a = a, m = m, s = s, b = b);
    
    if reverse:
        flt.reverse();
    
    if verbose:
        plt.plot(x, flt);
        plt.title('flatfieldLineFromRegression')
    
    return io.writePoints(sink, flt);

