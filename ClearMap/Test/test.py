# -*- coding: utf-8 -*-
"""
Processing Brain Samples - Test Image Processing Parameters

Created on Thu Jun  4 14:37:06 2015

@author: ckirst
"""


import os
import numpy
import sys

# path to illastik installation
sys.path.insert(1, '/home/ckirst/programs/ilastik-05')

from iDISCO.Parameter import *
from iDISCO.IO import IO as io
from iDISCO.Visualization import Plot as plt
from iDISCO.ImageProcessing import SpotDetection as ip

verbose = True;

##############################################################################
# Test Spot Detection
##############################################################################

parameter = Parameter();

basedirectory = iDISCOPath()

### Data Source 

#raw data from microscope used for cell detection (ims or tif)
parameter.DataSource.ImageFile = os.path.join(basedirectory, 'Test/Data/OME/16-17-27_0_8X-s3-20HF_UltraII_C00_xyz-Table Z\d{4}.ome.tif')

parameter.DataSource.ImageFile = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims'

#image ranges
parameter.DataSource.XRange = all;
parameter.DataSource.YRange = all;
parameter.DataSource.ZRange = (100,120);

# load data

data = io.readData(parameter.DataSource.ImageFile, x = parameter.DataSource.XRange, y = parameter.DataSource.YRange, z = parameter.DataSource.ZRange, resolution = 0);
print "Loaded data from " + parameter.DataSource.ImageFile;
print "Data size is: " + str(data.shape)

# visualize

if verbose:
    plt.plotTiling(15*data)


### Process using Spot Detection

# radius for background removal
parameter.ImageProcessing.Parameter.Background = (15,15);

img = ip.removeBackground(data, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

# size of differeence of gaussian filter
parameter.ImageProcessing.Parameter.Dog = (7, 7, 11);

img = ip.dogFilter(img, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

# h value for h max detection
parameter.ImageProcessing.Parameter.HMax = 20;

imgmax = ip.findExtendedMaxima(img, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

centers, intensities = ip.findCenterOfMaxima(img, imgmax, parameter = parameter.ImageProcessing, verbose =  verbose);


# intensity threshold for final cells to be saved
parameter.ImageProcessing.Parameter.ThresholdSave = 30;

iid = intensities > parameter.ImageProcessing.Parameter.ThresholdSave ;
centersSave = centers[iid,:];

if verbose:
    imgc = numpy.zeros(img.shape);
    for i in range(centersSave.shape[0]):
        imgc[centersSave[i,0], centersSave[i,1], centersSave[i,2]] = 1;
    plt.plotOverlayLabel(img * 0.01, imgc, alpha = False);



# result file for cell coordinates (csv, vtk or ims)
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'Test/ImageProcessing/cells.csv');

io.writePoints(parameter.ImageProcessing.CellCoordinateFile, centersSave);







##############################################################################
# Test Ilastik
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.IO import IO as io
from iDISCO.Visualization import Plot as plt
from iDISCO.ImageProcessing import SpotDetection as ip

from iDISCO.ImageProcessing import IlastikClassification as ip

parameter = Parameter();
parameter.ImageProcessing.Parameter = IlastikParameter()

basedirectory = iDISCOPath()

verbose = True;

### Data Source 

#raw data from microscope used for cell detection (ims or tif)
parameter.DataSource.ImageFile = os.path.join(basedirectory, 'Test/Data/OME/16-17-27_0_8X-s3-20HF_UltraII_C00_xyz-Table Z\d{4}.ome.tif')

#image ranges
parameter.DataSource.XRange = (1400,1600);
parameter.DataSource.YRange = (1400,1600);
parameter.DataSource.ZRange = all;


# load data
data = io.readData(parameter.DataSource.ImageFile, x = parameter.DataSource.XRange, y = parameter.DataSource.YRange, z = parameter.DataSource.ZRange, resolution = 0);
print "Loaded data from " + parameter.DataSource.ImageFile;
print "Data size is: " + str(data.shape)

# visualize
if verbose:
    plt.plotTiling(15*data)


#rescale data
import math

parameter.ImageProcessing.Parameter.Rescale  =  1.0 / math.pow(2,16) * math.pow(2,8) * 10;

dataw = ip.rescaleToIlastik(data, parameter.ImageProcessing);
print dataw.dtype
print dataw.max()


# radius for background removal
parameter.ImageProcessing.Parameter.Background = (15,15);

img = ip.removeBackground(data, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

# save to train classifier in ilastik
io.OME.writeData(dataw, os.path.join(basedirectory, "Test/Data/Ilastik/image"))


### Process using Ilastik

# radius for background removal
parameter.ImageProcessing.Parameter.Background = (15,15);

#classifier file
parameter.ImageProcessing.Parameter.Classifier = os.path.join(basedirectory, "Test/Ilastik/classifier.h5");

centers, intensities = ip.detectCells(data, verbose = verbose, parameter = parameter.ImageProcessing);


# intensity threshold for final cells to be saved
parameter.ImageProcessing.Parameter.ThresholdSave = 30;

iid = intensities > parameter.ImageProcessing.Parameter.ThresholdSave ;
centersSave = centers[iid,:];

if verbose:
    imgc = numpy.zeros(img.shape);
    for i in range(centersSave.shape[0]):
        imgc[centersSave[i,0], centersSave[i,1], centersSave[i,2]] = 1;
    plt.plotOverlayLabel(img * 0.01, imgc, alpha = False);


# result file for cell coordinates (csv, vtk or ims)
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'Test/ImageProcessing/cells.csv');

io.writePoints(parameter.ImageProcessing.CellCoordinateFile, centersSave);






##############################################################################
# Test Resampling / Make Reference
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import runResampling

basedirectory = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_07/'

parameter = Parameter();


#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43/21-00-43_0_8X-autofluo_UltraII_C00_xyz-Table Z\d{4}.ome.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43_resample.tif');
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.XResolutionData = 4.0625;
parameter.Resampling.YResolutionData = 4.0625;
parameter.Resampling.ZResolutionData = 3;

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.XResolutionReference = 25;    
parameter.Resampling.YResolutionReference = 25;
parameter.Resampling.ZResolutionReference = 10;

#Orientation of the Data set wrt reference 
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = None;

#Processes to use for Resmapling
parameter.Resampling.Processes = 4;

resampledImage = runResampling(parameter);

print "Resampled image saved as %s" % resampledImage








##############################################################################
# Test Alignment
##############################################################################

import os

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment, runInitializeElastix

import iDISCO.Alignment.Elastix

basedirectory = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_07/'

parameter = Parameter();

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43_reference.tif');
parameter.Alignment.FixedImageMask = None;
  
  
#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');


runInitializeElastix(parameter)
iDISCO.Alignment.Elastix.ElastixSettings.printInfo();

resultDirectory = runAlignment(parameter);

print "Aligned images: result directory: %s" % resultDirectory




##############################################################################
# Test Detect Points
############################################################################## 

import os

from iDISCO.Parameter import *
from iDISCO.Run import runCellDetection

verbose = True;

parameter = Parameter();

basedirectory = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_07/'

### Data Source 

#raw data from microscope used for cell detection (ims or tif)
parameter.DataSource.ImageFile = os.path.join(basedirectory, '150630_0_8X-cfos_18-32-28/18-32-28_0_8X-cfos_UltraII_C00_xyz-Table Z\d{4}.ome.tif')

#image ranges
parameter.DataSource.XRange = all;
parameter.DataSource.YRange = all;
parameter.DataSource.ZRange = all;

# radius for background removal
parameter.ImageProcessing.Parameter.Background = (15,15);

# size of differeence of gaussian filter
parameter.ImageProcessing.Parameter.Dog = (7, 7, 11);

# h value for h max detection
parameter.ImageProcessing.Parameter.HMax = 20;

# intensity threshold for final cells to be saved
parameter.ImageProcessing.Parameter.ThresholdSave = None;

# result file for cell coordinates (csv, vtk or ims)
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells.csv');
parameter.ImageProcessing.CellIntensityFile = os.path.join(basedirectory, 'intensities.csv');

runCellDetection(parameter)


  
 
##############################################################################
# Test Transform Points
############################################################################## 


import os

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment

basedirectory = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_07/'

parameter = Parameter();

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix/'
   
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, '150701_0_8X-autofluo_21-00-43_reference.tif');
parameter.Alignment.FixedImageMask = None;
  
  
#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');

runInitializeElastix(parameter);

resultDirectory = runAlignment(parameter);

print "Aligned images: result directory: %s" % resultDirectory








##############################################################################
# Test Full Chain
##############################################################################

parameter = Parameter();

basedirectory = iDISCOPath()










### Data Source 

#raw data from microscope used for cell detection (ims or tif)
parameter.DataSource.ImageFile = os.path.join(basedirectory, 'Test/Data/OME/16-17-27_0_8X-s3-20HF_UltraII_C00_xyz-Table Z\d{4}.ome.tif')

parameter.DataSource.ImageFile = '/run/media/ckirst/ChristophsBackuk4TB/Data/Science/Projects/BrainActiityMap/Experiment/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims'

#image ranges
parameter.DataSource.XRange = all;
parameter.DataSource.YRange = all;
parameter.DataSource.ZRange = (100,120);

# load data

data = io.readData(parameter.DataSource.ImageFile, x = parameter.DataSource.XRange, y = parameter.DataSource.YRange, z = parameter.DataSource.ZRange, resolution = 0);
print "Loaded data from " + parameter.DataSource.ImageFile;
print "Data size is: " + str(data.shape)

# visualize

if verbose:
    plt.plotTiling(15*data)


### Process using Spot Detection

# radius for background removal
parameter.ImageProcessing.Parameter.Background = (15,15);

img = ip.removeBackground(data, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

# size of differeence of gaussian filter
parameter.ImageProcessing.Parameter.Dog = (7, 7, 11);

img = ip.dogFilter(img, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

# h value for h max detection
parameter.ImageProcessing.Parameter.HMax = 20;

imgmax = ip.findExtendedMaxima(img, parameter = parameter.ImageProcessing, verbose =  verbose);
print img.dtype
print img.shape

centers, intensities = ip.findCenterOfMaxima(img, imgmax, parameter = parameter.ImageProcessing, verbose =  verbose);


# intensity threshold for final cells to be saved
parameter.ImageProcessing.Parameter.ThresholdSave = 30;

iid = intensities > parameter.ImageProcessing.Parameter.ThresholdSave ;
centersSave = centers[iid,:];

if verbose:
    imgc = numpy.zeros(img.shape);
    for i in range(centersSave.shape[0]):
        imgc[centersSave[i,0], centersSave[i,1], centersSave[i,2]] = 1;
    plt.plotOverlayLabel(img * 0.01, imgc, alpha = False);



# result file for cell coordinates (csv, vtk or ims)
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'Test/ImageProcessing/cells.csv');

io.writePoints(parameter.ImageProcessing.CellCoordinateFile, centersSave);
