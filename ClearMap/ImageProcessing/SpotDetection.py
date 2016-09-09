# -*- coding: utf-8 -*-
"""
Functions to detect spots in images

The main routine :func:`detectCells` uses a difference of gaussian filter (see 
:mod:`~ClearMap.ImageProcessing.Filter`) followed by a peak detection step.

Example:

    >>> import os
    >>> import ClearMap.IO as io  
    >>> import ClearMap.Settings as settings
    >>> import ClearMap.ImageProcessing.SpotDetection as sd
    >>> fn = os.path.join(settings.ClearMapPath, 'Test/Data/Synthetic/test_iDISCO_\d{3}.tif');
    >>> img = io.readData(fn);
    >>> img = img.astype('int16'); # converting data to smaller integer types can be more memory efficient!
    >>> res = sd.detectSpots(img, dogSize = (5,5,5), flatfield = None, threshold = 5, cellShapeThreshold = 1);
    >>> print 'Found %d cells !' % res[0].shape[0]
    Illumination: flatfield          : None
    Illumination: illuminationScaling: True
    Illumination: background         : None
    Background: backgroundSize: (15, 15)
    Background: elapsed time: 0:00:00
    DoG: dogSize: (5, 5, 5)
    DoG: elapsed time: 0:00:00
    Extended Max: threshold   : 5
    Extended Max: localMaxSize: 5
    Extended Max: hMax        : None
    Extended Max: elapsed time: 0:00:00
    Cell Centers: elapsed time: 0:00:00
    Cell Shape: cellShapeThreshold: 1
    Cell Shape:: elapsed time: 0:00:00
    Cell Size:: elapsed time: 0:00:00
    Cell Intensity: cellIntensityMethod: Max
    Cell Intensity:: elapsed time: 0:00:00
    Cell Intensity: cellIntensityMethod: Max
    Cell Intensity:: elapsed time: 0:00:00
    Cell Intensity: cellIntensityMethod: Max
    Cell Intensity:: elapsed time: 0:00:00
    Found 38 cells !
    
After execution this example inspect the result of the cell detection in 
the folder 'Test/Data/CellShape/cellshape\_\\d{3}.tif'.
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy


from ClearMap.ImageProcessing.IlluminationCorrection import correctIllumination
from ClearMap.ImageProcessing.BackgroundRemoval import removeBackground
from ClearMap.ImageProcessing.Filter.DoGFilter import filterDoG
from ClearMap.ImageProcessing.MaximaDetection import findExtendedMaxima, findPixelCoordinates, findIntensity, findCenterOfMaxima
from ClearMap.ImageProcessing.CellSizeDetection import detectCellShape, findCellSize, findCellIntensity

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter


##############################################################################
# Spot detection
##############################################################################

def detectSpots(img, detectSpotsParameter = None, correctIlluminationParameter = None, removeBackgroundParameter = None,
                filterDoGParameter = None, findExtendedMaximaParameter = None, detectCellShapeParameter = None,
                verbose = False, out = sys.stdout, **parameter):
    """Detect Cells in 3d grayscale image using DoG filtering and maxima detection
    
    Effectively this function performs the following steps:
        * illumination correction via :func:`~ClearMap.ImageProcessing.IlluminationCorrection.correctIllumination`
        * background removal via :func:`~ClearMap.ImageProcessing.BackgroundRemoval.removeBackground`
        * difference of Gaussians (DoG) filter via :func:`~ClearMap.ImageProcessing.Filter.filterDoG`
        * maxima detection via :func:`~ClearMap.ImageProcessing.MaximaDetection.findExtendedMaxima`
        * cell shape detection via :func:`~ClearMap.ImageProcessing.CellSizeDetection.detectCellShape`
        * cell intensity and size measurements via: :func:`~ClearMap.ImageProcessing.CellSizeDetection.findCellIntensity`,
          :func:`~ClearMap.ImageProcessing.CellSizeDetection.findCellSize`. 
    
    Note: 
        Processing steps are done in place to save memory.
        
    Arguments:
        img (array): image data
        detectSpotParameter: image processing parameter as described in the individual sub-routines
        verbose (bool): print progress information
        out (object): object to print progress information to
        
    Returns:
        tuple: tuple of arrays (cell coordinates, raw intensity, fully filtered intensty, illumination and background corrected intensity [, cell size])
    """

    timer = Timer();
    
    # normalize data -> to check
    #img = img.astype('float');
    #dmax = 0.075 * 65535;
    #ids = img > dmax;
    #img[ids] = dmax;
    #img /= dmax; 
    #out.write(timer.elapsedTime(head = 'Normalization'));
    #img = dataset[600:1000,1600:1800,800:830];
    #img = dataset[600:1000,:,800:830];
    
    # correct illumination
    correctIlluminationParameter = getParameter(detectSpotsParameter, "correctIlluminationParameter", correctIlluminationParameter);
    img1 = img.copy();
    img1 = correctIllumination(img1, correctIlluminationParameter = correctIlluminationParameter, verbose = verbose, out = out, **parameter)   

    # background subtraction in each slice
    #img2 = img.copy();
    removeBackgroundParameter = getParameter(detectSpotsParameter, "removeBackgroundParameter", removeBackgroundParameter);
    img2 = removeBackground(img1, removeBackgroundParameter = removeBackgroundParameter, verbose = verbose, out = out, **parameter)   
    
    # mask
    #timer.reset();
    #if mask == None: #explicit mask
    #    mask = img > 0.01;
    #    mask = binary_opening(mask, self.structureELement('Disk', (3,3,3)));
    #img[img < 0.01] = 0; # masking in place  # extended maxima
    #out.write(timer.elapsedTime(head = 'Mask'));    
    
    #DoG filter
    filterDoGParameter = getParameter(detectSpotsParameter, "filterDoGParameter", filterDoGParameter);
    dogSize = getParameter(filterDoGParameter, "size", None);
    #img3 = img2.copy();    
    img3 = filterDoG(img2, filterDoGParameter = filterDoGParameter, verbose = verbose, out = out, **parameter);
    
    # normalize    
    #    imax = img.max();
    #    if imax == 0:
    #        imax = 1;
    #    img /= imax;
    
    # extended maxima
    findExtendedMaximaParameter = getParameter(detectSpotsParameter, "findExtendedMaximaParameter", findExtendedMaximaParameter);
    hMax = getParameter(findExtendedMaximaParameter, "hMax", None);
    imgmax = findExtendedMaxima(img3, findExtendedMaximaParameter = findExtendedMaximaParameter, verbose = verbose, out = out, **parameter);
    
    #center of maxima
    if not hMax is None:
        centers = findCenterOfMaxima(img, imgmax, verbose = verbose, out = out, **parameter);
    else:
        centers = findPixelCoordinates(imgmax, verbose = verbose, out = out, **parameter);
    
    #cell size detection
    detectCellShapeParameter = getParameter(detectSpotsParameter, "detectCellShapeParameter", detectCellShapeParameter);
    cellShapeThreshold = getParameter(detectCellShapeParameter, "threshold", None);
    if not cellShapeThreshold is None:
        
        # cell shape via watershed
        imgshape = detectCellShape(img2, centers, detectCellShapeParameter = detectCellShapeParameter, verbose = verbose, out = out, **parameter);
        
        #size of cells        
        csize = findCellSize(imgshape, maxLabel = centers.shape[0], out = out, **parameter);
        
        #intensity of cells
        cintensity = findCellIntensity(img, imgshape,  maxLabel = centers.shape[0], verbose = verbose, out = out, **parameter);

        #intensity of cells in background image
        cintensity2 = findCellIntensity(img2, imgshape,  maxLabel = centers.shape[0], verbose = verbose, out = out, **parameter);
    
        #intensity of cells in dog filtered image
        if dogSize is None:
            cintensity3 = cintensity2;
        else:
            cintensity3 = findCellIntensity(img3, imgshape,  maxLabel = centers.shape[0], verbose = verbose, out = out, **parameter);
        
        if verbose:
            out.write(timer.elapsedTime(head = 'Spot Detection') + '\n');
        
        #remove cell;s of size 0
        idz = csize > 0;
                       
        return ( centers[idz], numpy.vstack((cintensity[idz], cintensity3[idz], cintensity2[idz], csize[idz])).transpose());        
        
    
    else:
        #intensity of cells
        cintensity = findIntensity(img, centers, verbose = verbose, out = out, **parameter);

        #intensity of cells in background image
        cintensity2 = findIntensity(img2, centers, verbose = verbose, out = out, **parameter);
    
        #intensity of cells in dog filtered image
        if dogSize is None:
            cintensity3 = cintensity2;
        else:
            cintensity3 = findIntensity(img3, centers, verbose = verbose, out = out, **parameter);

        if verbose:
            out.write(timer.elapsedTime(head = 'Spot Detection') + '\n');
    
        return ( centers, numpy.vstack((cintensity, cintensity3, cintensity2)).transpose());
        



def test():
    """Test Spot Detection Module"""
    import os
    import ClearMap.ImageProcessing.SpotDetection as self
    reload(self)
    import ClearMap.IO as io  
    import ClearMap.Settings as settings
    
    basedir = settings.ClearMapPath;
    #fn = '/home/ckirst/Science/Projects/BrainActivityMap/Data/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims';
    fn = os.path.join(basedir, 'Test/Data/Synthetic/label_iDISCO_\d{3}.tif');
    fn = os.path.join(basedir, 'Test/Data/OME/16-17-27_0_8X-s3-20HF_UltraII_C00_xyz-Table Z\d{4}.ome.tif');
    #fn = '/run/media/ckirst/ChristophsBackuk4TB/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims';
    #fn = '/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 - Copy.ims';
    #fn = '/home/ckirst/Science/Projects/BrainActivityMap/iDISCO_2015_04/test for spots added spot.ims'

    img = io.readData(fn);
    #img = dataset[0:500,0:500,1000:1008];
    #img = dataset[600:1000,1600:1800,800:830];
    #img = dataset[500:1500,500:1500,800:809]; 
    img = img.astype('int16');
    
    #m = sys.modules['iDISCO.ImageProcessing.SpotDetection']
    #c = self.detectCells(img);
    
    c = self.detectCells(img, dogSize = None, cellShapeThreshold = 1, cellShapeFile = '/home/ckirst/Science/Projects/BrainActivityMap/Analysis/iDISCO/Test/Data/CellShape/cellshape_\d{3}.tif');
    
    print 'done, found %d cells !' % c[0].shape[0]


    #test intensities:
    import numpy;
    x = numpy.random.rand(30,30,10);
    centers = numpy.array([[0,0,0], [29,29,9]]);
    i = self.findIntensity(x, centers, boxSize = (1,1,1));
    print i


if __name__ == '__main__':
    test();
    
    
    
    
