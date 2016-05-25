# -*- coding: utf-8 -*-
"""
ClearMap default parameter module.

This module defines default parameter used by various sub-packages.

See Also:
   :mod:`~ClearMap.Settings`
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


import os
import ClearMap.Settings as settings

#from ClearMap.Utils.ParameterTools import joinParameter

##############################################################################
# Image Processing
##############################################################################

correctIlluminationParameter = {
    "flatfield" : True,  # (str, True or None)  flat field intensities, if None d onot correct image for illumination, if True the 
    "background" : None, # (str, None or array) background image as file name or array, if None background is assumed to be zero
    "scaling" :  "Mean", # (str or None)        scale the corrected result by this factor, if 'max'/'mean' scale to keep max/mean invariant
    "save" : None,       # (str or None)        save the corrected image to file
    "verbose" : False    # (bool or int)        print / plot information about this step 
}

removeBackgroundParameter = {
    "size" : (15,15),  # size for the structure element of the morphological opening
    "save" : None,     # file name to save result of this operation
    "verbose" : False  # print / plot information about this step       
}


filterDoGParameter = {
    "size" :  (7, 7, 11),  # (tuple or None)      size for the DoG filter if None, do not correct for any background
    "sigma" : None,        # (tuple or None)      std of outer Guassian, if None autmatically determined from size
    "sigma2": None,        # (tuple or None)      std of inner Guassian, if None autmatically determined from size
    "save"  : None,        # (str or None)        file name to save result of this operation if None dont save to file 
    "verbose" : False      # (bool or int)        print / plot information about this step
}

findExtendedMaximaParameter = {
    "hMax" : 20,            # (float or None)     h parameter for the initial h-Max transform, if None, do not perform a h-max transform
    "size" : 5,             # (tuple)             size for the structure element for the local maxima filter
    "threshold" : 0,        # (float or None)     include only maxima larger than a threshold, if None keep all localmaxima
    "save"  : None,         # (str or None)       file name to save result of this operation if None dont save to file 
    "verbose" : False       # (bool or int)       print / plot information about this step
}

findIntensityParameter = {
    "method" : 'Max',       # (str, func, None)   method to use to determine intensity (e.g. "Max" or "Mean") if None take intensities at the given pixels
    "size" :  (3,3,3)       # (tuple)             size of the box on which to perform the *method*
}

detectCellShapeParameter = {
    "threshold" : 700,     # (float or None)      threshold to determine mask, pixel below this are background if None no mask is generated
    "save"  : None,        # (str or None)        file name to save result of this operation if None dont save to file 
    "verbose" : False      # (bool or int)        print / plot information about this step if None take intensities at the given pixels
}

## Paramters for cell detection using spot detection algorithm 
detectCellParameter = {
    "correctIlluminationParameter" : correctIlluminationParameter,
    "removeBackgroundParameter"    : removeBackgroundParameter,
    "filterDoGParameter"           : filterDoGParameter,
    "findExtendedMaximaParameter"  : findExtendedMaximaParameter,
    "findIntensityParameter"       : findIntensityParameter,
    "detectCellShapeParameter"     : detectCellShapeParameter
}


"""
dict: Paramters for cell detection using the spot detection algorithm
   
See Also:
   :const:`IlastikParameter`, :const:`StackProcessingParameter`
"""     

## Paramters for cell detection using Ilastik classification 
IlastikParameter = {
    #ilastic classifier to use
    "classifier" : os.path.join(settings.ClearMapPath, '/Test/Ilastik/classifier.h5'),
    
    # Rescaling of images
    "rescale" : None,
    
    # Background correctoin: None or (y,x) which is size of disk for gray scale opening
    "backgroundSize" : (15,15)
    };
"""
dict: Paramters for cell detection using Ilastik classification

   * "classifier": ilastic classifier to use
     
   * "rescale": rescale images before classification
    
   * "backgroundSize": Background correctoin: None or (y,x) which is size of disk for gray scale opening

See Also:
   :const:`SpotDetectionParameter`, :const:`StackProcessingParameter`
"""

## Parameter for processing a stack in parallel
processStackParameter = {
    #max number of parallel processes
    "processes" : 2,
   
    #chunk sizes
    "chunkSizeMax" : 100,
    "chunkSizeMin" : 30,
    "cChunkOverlap" : 15,

    #optimize chunk size and number to number of processes
    "chunkOptimization" : True,
    
    #increase chunk size for optimizaition (True, False or all = automatic)
    "chunkOptimizationSize" : all
    };
"""
dict: Parameter for processing an image stack in parallel
    *  "processes": max number of parallel processes

    * "chunkSizeMax" : maximal chunk size in z 
    * "chunkSizeMin" : minimal chunk size in z,
    * "chunkOverlap" : overlap between two chunks,

    * "chunkOptimization": optimize chunk size and number to number of processes
    * "chunkOptimizationSize": increase chunk size for optimizaition (True, False or all = automatic)

See Also:
   :const:`SpotDetectionParameter`, :const:`IlastikParameter`
"""

##############################################################################
# Alignment / Morphin / Resmapling
##############################################################################

## Parameter for Elastix alignment
AlignmentParameter = {
    #directory of the alignment result
    "alignmentDirectory" : None,
            
    #moving and reference images
    "movingImage" : os.path.join(settings.ClearMapPath, '/Test/Data/Elastix/150524_0_8X-s3-20HFautofluor_18-51-1-warpable.tif'),
    "fixedImage"  : os.path.join(settings.ClearMapPath, '/Test/Data/Elastix/OstenRefARA_v2_lowerHalf.tif'),
    "fixedImageMask" : None,
    
    #elastix parameter files for alignment
    "affineParameterFile"  : os.path.join(settings.ClearMapPath, '/Test/Elastix/ElastixParameterAffine.txt'),
    "bSplineParameterFile" : os.path.join(settings.ClearMapPath, '/Test/Elastix/ElastixParameterBSpline.txt'),
    };
"""
dict: Parameter for Elastix alignment

  * "alignmentDirectory" : directory to save the alignment result
              
  * "movingImage": image to be aligned 
  * "fixedImage":  reference image
  
  * "affineParameterFile": elastix parameter files for affine alignment
  * "bSplineParameterFile" : elastix parameter files for non-linear alignment

See Also:
   :mod:`~ClearMap.Alignment.Elastix`
"""

## Parameter for resampling data
ResamplingParameter = {
    
    #Data source and output file
    "source" : None,
    "sink"   : None,
    
    #Resolution of the raw data (in um / pixel) as (x,y,z)
    "resolutionSource" : (4.0625, 4.0625, 3),

    #Resolution of the Reference / Atlas (in um/ pixel) as (x,y,z)
    "resolutionSink" : (25, 25, 25),

    #Orientation of the Data set wrt reference as (x=1,y=2,z=3)
    #(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
    "orientation" : None
    };
"""
dict: Parameter for resampling data

    * "source" : data source file
    * "sink"   : data output file
    
    "resolutionSource": resolution of the raw data (in um / pixel) as (x,y,z)

    "resolutionSink" : resolution of the reference / atlas image (in um/ pixel) as (x,y,z)

    "orientation" : Orientation of the data set wrt reference as (x=1,y=2,z=3) 
     (-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
  
See Also:
   :mod:`~ClearMap.Alignment.Resampling`
"""


##############################################################################
# Analysis
##############################################################################

## Parameter to calculate density voxelization
VoxelizationParameter = {
    #Method to voxelize
    "method" : 'Spherical', # Spherical,'Rectangular, Gaussian'
       
    # Define bounds of the volume to be voxelized
    "voxelizationSize" : (1,1,1),  
    };
"""
dict: Parameter to calculate density voxelization

    * "method": Method to voxelize: 'Spherical','Rectangular, 'Gaussian'
    * "voxelizationSize": max size of the volume to be voxelized
    
See Also:
   :mod:`~ClearMap.Analysis.voxelization`
"""



