# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 11:42:52 2015

Test Processing Chain with Synthetic Data

@author: ckirst
"""



##############################################################################
# Test Resampling / Make Reference
##############################################################################

import os

import iDISCO.Settings as settings

from iDISCO.Alignment.Resampling import resampleData

baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

## Parameter for resampling data
resamplingParameter = {
    
    #Data source and output file
    "source" : os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif'),
    "sink"   : os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif'),
    
    #Resolution of the raw data (in um / pixel) as (x,y,z)
    "resolutionSource" : (5, 5, 3),

    #Resolution of the Reference / Atlas (in um/ pixel) as (x,y,z)
    "resolutionSink" : (12, 15, 5),

    #Orientation of the Data set wrt reference as (x=1,y=2,z=3)
    #(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
    "orientation" : (1,2,3),
    
    #number of processes to use in parallel:
    "processes" : 4,
    };


resampledImage = resampleData(**resamplingParameter)
print "Resampled image saved as %s" % resampledImage


# create reference for further tests
#import shutil
#shutil.copyfile(resampledImage, os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif'))
resamplingParameter["sink"] = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif');
resamplingParameter["resolutionSink"] = (12, 12, 5);
referenceImage = resampleData(**resamplingParameter);
print "Reference image saved as %s" % referenceImage


# use None as sink to get the numpy array
resamplingParameter["sink"] = None
referenceImage = resampleData(**resamplingParameter);
referenceImage.shape

#import iDISCO.IO.IO as io
#io.writeData(os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif'), referenceImage.astype('int16'))


##############################################################################
# Test Alignment
##############################################################################

import os

import iDISCO.Settings as settings

from iDISCO.Alignment.Elastix import alignData

baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

alignmentDirectory = os.path.join(baseDirectory, 'Synthetic/elastix');

alignmentParameter = {            
    #moving and reference images
    "movingImage" : os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif'),
    "fixedImage"  : os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif'),
    
    #elastix parameter files for alignment
    "affineParameterFile"  : os.path.join(alignmentDirectory, 'ElastixParameterAffine.txt'),
    "bSplineParameterFile" : None,
    
    #directory of the alignment result
    "resultDirectory" : alignmentDirectory
    };



result = alignData(**alignmentParameter);

print "Aligned images: result directory: %s" % result




##############################################################################
# Test Detect Points
############################################################################## 

import os

import iDISCO.Settings as settings

from iDISCO.ImageProcessing.CellDetection import detectCells
from iDISCO.Utils.ParameterTools import joinParameter

baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

## Parameter for processing a stack in parallel
stackProcessingParameter = {
    #max number of parallel processes
    "processes" : 4,
   
    #chunk sizes
    "chunkSizeMax" : 25,
    "chunkSizeMin" : 20,
    "chunkOverlap" : 10,

    #optimize chunk size and number to number of processes
    "chunkOptimization" : True,
    
    #increase chunk size for optimizaition (True, False or all = automatic)
    "chunkOptimizationSize" : all
      
    };


## Paramters for cell detection using spot detection alorithm 
spotDetectionParameter = {
    # background correctoin: None or (x,y) which is size of disk for gray scale opening
    "backgroundSize" : (20,20),
    
    # spot Detection via Difference of Gaussians (DoG) filter: (x,y,z) size
    #"dogSize" : (8, 8, 6),
    'dogSize' : None,
    
    # h of h-max transform
    "hMax" : 0.15,
    
    # intensity detection   
    "intensityMethod"  : 'Max',  #None -> intensity of pixel of center, alternatively string of numpy array method that returns a single number
    "intensitySize"    : (3,3,3),  # size of box in (x,y,z) to include in intensity determination
    
    # threshold for min intensity at center to be counted as cell (should be similar to the h max)
    "threshold" : 0.15,
    
    # data and range
    "source" : os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif'),
    #"x" : all,
    #"y" : all,
    #"z" : all,
    
    # file names to save coordinates and intensities result, (None, None) = return numpy array
    "sink" : (os.path.join(baseDirectory, 'Synthetic/cells.csv'), os.path.join(baseDirectory, 'Synthetic/intensities.csv')),
    #"sink" : (None,  None),
    
    
    #write labeled image:
    "cellMaskFile" :   os.path.join(baseDirectory, 'Synthetic/Label/label_iDISCO_\d{3}.tif'),   
    
    #some debug / quality check output
    #"verbose" : True,
    #"processMethod" : "sequential"  #  plotting during image processing only in sequential mode !
    };



allParameter = joinParameter(stackProcessingParameter, spotDetectionParameter, {'x' : (100,160), 'y' : (10,140), 'z' : (2,38)})
#allParameter = joinParameter(stackProcessingParameter, spotDetectionParameter, {'x' : all, 'y' : all, 'z' : all})

result = detectCells(**allParameter);
print result

verbose = True;
if verbose:
    import iDISCO.IO.IO as io
    import iDISCO.Visualization.Plot as plot   
    
    dataraw = io.readData(spotDetectionParameter["source"]);
    dataraw[dataraw > 50] = 50;
    dataraw = dataraw.astype('float') / dataraw.max();
    points  = io.readPoints(spotDetectionParameter["sink"][0]);
    plot.plotOverlayPoints(dataraw, points, pointColor = [1,0,0]);


dataraw = io.readData(spotDetectionParameter["source"], x = (100,160), y = (10,140), z =  (2,38));
io.writeData( os.path.join(baseDirectory, 'Synthetic/raw.tif'), dataraw)

##############################################################################
# Test Resample Points
############################################################################## 

import os

import iDISCO.Settings as settings
import iDISCO.IO.IO as io
import iDISCO.Visualization.Plot as plot

from iDISCO.Alignment.Resampling import resamplePoints, resamplePointsInverse

verbose = True;

baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

files = os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif');

dataSize = io.dataSize(files);
print dataSize


resamplingParameter = {
    #Resolution of the raw data (in um / pixel) as (x,y,z)
    "resolutionSource" : (5, 5, 3),

    #Resolution of the Reference / Atlas (in um/ pixel) as (x,y,z)
    "resolutionSink"   : (12, 15, 5),

    #Orientation of the Data set wrt reference as (x=1,y=2,z=3)
    #(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
    "orientation" : (1,2,3),
    
    #number of processes to use in parallel:
    "processes" : 4,     
    };


#centers
points = io.readPoints(os.path.join(baseDirectory, 'Synthetic/cells.csv'));
print "points shape: (%d, %d)" % points.shape

respoints = resamplePoints(points, dataSize, shiftPoints = True, **resamplingParameter);
print "Reshaped centers shape: (%d, %d)" % respoints.shape

if verbose:
    dataraw = io.readData(os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif'));
    datares = io.readData(os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif'));
    print "Shape raw: " + str(dataraw.shape)
    print "Shape res: " + str(datares.shape)
    
    plot.plotOverlayPoints(dataraw*0.01, points);
    plot.plotOverlayPoints(datares*0.01, respoints);


#check inverse:
resipoints = resamplePointsInverse(respoints, dataSize, **resamplingParameter);
diff = points - resipoints;
print (diff.max(), diff.min());




##############################################################################
# Test Transform Points on Corners
############################################################################## 

import numpy

import iDISCO.Alignment.Elastix as elx;

verbose = True;

# directory in with elastix alignment result 
transformDirectory  =  os.path.join(baseDirectory, 'Synthetic/elastix');

#result diectory to write transformed points to (None = read back as array)
resultDirectory    = os.path.join(baseDirectory, 'Synthetic/transformix')

#define (y,x,z) coordinates for testing
points = numpy.array([[0,0,0],[74,0,0],[0,52,0],[0,0,23],[74,52,0]]);

#acenters = elx.transformPoints(rcenters, alignmentdirectory = parameter.Alignment.AlignmentDirectory, outdirectory = pointsdir);
pointsa = elx.transformPoints(points, resultDirectory = resultDirectory, transformDirectory = transformDirectory);

print pointsa



##############################################################################
# Test Transform Reference to Resampled Data
############################################################################## 

import os

import iDISCO.Settings as settings

import iDISCO.IO.IO as io
import iDISCO.Alignment.Elastix as elx

import iDISCO.Visualization.Plot as plot

baseDirectory = os.path.join(settings.IDISCOPath,  'Test');

verbose = True;

transformDirectory = os.path.join(baseDirectory, 'Synthetic/elastix');
transformFile      = elx.getTransformParameterFile(transformDirectory)

# tranform points according to alignment of data and reference 
resampleFile    = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif');
referenceFile    = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif');

resultDirectory = os.path.join(baseDirectory, 'Synthetic/transformix')

#elx.transformData(dataresname, alignmentdirectory = resultdir, outdirectory = dataalgname)
resultFile = elx.transformData(referenceFile, transformDirectory = transformDirectory, resultDirectory = resultDirectory)

if verbose:
    resampledata  = io.readData(resampleFile);
    referencedata = io.readData(referenceFile);
    transformdata = io.readData(resultFile);

    print resampledata.shape
    print referencedata.shape
    print transformdata.shape    

    plot.plotTiling(0.01 * resampledata)
    plot.plotTiling(0.01 * referencedata)
    plot.plotTiling(0.01 * transformdata)    



##############################################################################
# Transform Points from Raw Data to Reference
############################################################################## 

import os

import iDISCO.Settings as settings
import iDISCO.Visualization.Plot as plot
import iDISCO.IO.IO as io

from iDISCO.Alignment.Elastix import transformPoints
from iDISCO.Alignment.Resampling import resamplePoints

baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

verbose = True;

## Data sources
dataFile = os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')

## Cell coordinates source
pointsFile = os.path.join(baseDirectory, 'Synthetic/cells.csv')

## Cell transformed cordinate resilt file
transformedPointsFile = os.path.join(baseDirectory, 'Synthetic/cells_transformed_to_reference.csv')

## Parameter for resampling data
resamplingParameter = {
   
    #Resolution of the raw data (in um / pixel) as (x,y,z)
    "resolutionSource" : (5, 5, 3),

    #Resolution of the Reference / Atlas (in um/ pixel) as (x,y,z)
    "resolutionSink" : (12, 15, 5),

    #Orientation of the Data set wrt reference as (x=1,y=2,z=3)
    #(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
    "orientation" : (1,2,3)   
    };

alignmentDirectory = os.path.join(baseDirectory, 'Synthetic/elastix');

    
# downscale points to referenece image size
points = resamplePoints(pointsFile, dataFile, **resamplingParameter);
    
# transform points
points = transformPoints(points, transformDirectory = alignmentDirectory, indices = False, resultDirectory = None);

# save
io.writePoints(transformedPointsFile, points);

if verbose:
    refdata = io.readData(os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif'));
    plot.plotOverlayPoints(0.01 * refdata, points)








##############################################################################
# Test Voxelization
##############################################################################

import os

import iDISCO.Settings as settings
import iDISCO.IO.IO as io
import iDISCO.Visualization.Plot as plot

from iDISCO.Analysis.Voxelization import voxelize


baseDirectory = os.path.join(settings.IDISCOPath, 'Test');

verbose = True;


## Parameter to calculate density voxelization
voxelizationParameter = {
    #Method to voxelize
    "voxelizationMethod" : 'Spherical', # Spherical,'Rectangular, Gaussian'
       
    # Define bounds of the volume to be voxelized
    "voxelizationSize" : (5,5,5),  

    # Voxelization weigths (e/g intensities)
    "voxelizationWeights" : None
    };


#Points
transformedPointsFile = os.path.join(baseDirectory, 'Synthetic/cells_transformed_to_reference.csv')

#Reference file
referenceFile = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif');

#voxelization file 
voxelizationFile = None;

voxdata = voxelize(transformedPointsFile, dataSize = referenceFile, sink = voxelizationFile, **voxelizationParameter)

if verbose:
    #voxdata = io.readData(parameter.Alignment.FixedImage);
    voxdata = io.readData(voxdata);
    points  = io.readPoints(transformedPointsFile)
    plot.plotOverlayPoints(voxdata.astype('float') / voxdata.max(), points)



## with weights
import numpy

points  = io.readPoints(transformedPointsFile)

voxelizationParameter["voxelizationSize"]    = (9,9,9);
voxelizationParameter["voxelizationWeights"] = numpy.random.rand(points.shape[0]);

voxdata = voxelize(transformedPointsFile, dataSize = referenceFile, sink = voxelizationFile, **voxelizationParameter)

if verbose:
    #voxdata = io.readData(parameter.Alignment.FixedImage);
    voxdata = io.readData(voxdata);
    points  = io.readPoints(transformedPointsFile)
    plot.plotOverlayPoints(voxdata.astype('float') / voxdata.max(), points)













## old stuff


###############################################################################
## Test Full Chain
###############################################################################
#
#import os
#import numpy
#
#from iDISCO.Parameter import *
#from iDISCO.Run import *
#import iDISCO.Visualization.Plot as Plot
#
#verbose = True;
#
#baseDirectory = os.path.join(iDISCOPath(), 'Test');
#
#parameter = Parameter();
#
#
### Resampling to prepare alignment
#
##Files
#parameter.Resampling.DataFiles = os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
#parameter.Resampling.ResampledFile = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif');
#    
##Resolution of the Data (in um / pixel)
#parameter.Resampling.ResolutionData = (5, 5, 3);
#
##Resolution of the Reference / Atlas (in um/ pixel)
#parameter.Resampling.ResolutionReference = (12, 15, 5);
#
##Orientation of the Data set wrt reference 
##(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
#parameter.Resampling.Orientation = (1,2,3);
#
##Processes to use for Resmapling
#parameter.Resampling.Processes = 4;
#
#
### Alignment
#
##directory of the alignment result
#parameter.Alignment.AlignmentDirectory = os.path.join(baseDirectory, 'Synthetic/elastix');
#
##Elastix binary
#parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix'
#    
##moving and reference images
#parameter.Alignment.MovingImage = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_resample.tif');
#parameter.Alignment.FixedImage  = os.path.join(baseDirectory, 'Synthetic/test_iDISCO_reference.tif');
#parameter.Alignment.FixedImageMask = None;
#
##elastix parameter files for alignment
#parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
##parameter.Alignment.BSplineParameterFile = os.path.join(pbasedirectoryarameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');
#parameter.Alignment.BSplineParameterFile = None;
#
##initialize elastix
#runInitializeElastix(parameter)
#iDISCO.Alignment.Elastix.ElastixSettings.printInfo();
#
#
### Cell Detection
#
##raw data from microscope used for cell detection (ims or tif)
#parameter.DataSource.ImageFile = os.path.join(baseDirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
#
##image ranges
#parameter.DataSource.XRange = all;
#parameter.DataSource.YRange = all;
#parameter.DataSource.ZRange = all;
#
## radius for background removal
#parameter.ImageProcessing.Parameter.Background = (20,20);
#
## size of differeence of gaussian filter
#parameter.ImageProcessing.Parameter.Dog = (8, 8, 6);
#
## h value for h max detection
#parameter.ImageProcessing.Parameter.HMax = 0.5;
#parameter.ImageProcessing.Parameter.Threshold = 0.5;
#
## intensity threshold for final cells to be saved
#parameter.ImageProcessing.Parameter.ThresholdSave = None;
#
## result files for cell coordinates (csv, vtk or ims)
#parameter.ImageProcessing.CellCoordinateFile = os.path.join(baseDirectory, 'Synthetic/cells.csv');
#parameter.ImageProcessing.CellIntensityFile = os.path.join(baseDirectory, 'Synthetic/intensities.csv');
#parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(baseDirectory, 'Synthetic/cells_transformed.csv');
#
#
### Stack Processing Parameter
#    
##max number of parallel processes
#parameter.StackProcessing.Processes = 2;
#   
##chunk sizes
#parameter.StackProcessing.ChunkSizeMax = 100;
#parameter.StackProcessing.ChunkSizeMin = 30;
#parameter.StackProcessing.ChunkOverlap = 15;
#
##optimize chunk size and number to number of processes
#parameter.StackProcessing.OptimizeChunks = True;
#    
##increase chunk size for optimizaition (True, False or all = choose automatically)
#parameter.StackProcessing.OptimizeChunkSizeIncrease = all;
#
#
#
###Voxelization
#
##Size of averaging window
#parameter.Voxelization.AveragingDiameter = (15,15,15);  #Radius of the sphere
#    
##Image size
#parameter.Voxelization.Size = None;  #None extract from data
#    
##Mode
#parameter.Voxelization.Mode = 'Spherical';
#    
##Output File
#parameter.Voxelization.File = os.path.join(baseDirectory, 'Synthetic/points_voxelized.tif');
#
#
#
###Processing
#
#resampledImage = runResampling(parameter);
#
#print "Resampled image saved as %s" % resampledImage
#
#resultDirectory = runAlignment(parameter);
#
#print "Aligned images: result directory: %s" % resultDirectory
#
#runCellDetection(parameter)
#
#print "Cell detection done!"
#
#runCellCoordinateTransformationToReference(parameter)
#
#print "Cell transformation to reference done!"
#
#if verbose:
#    refdata = io.readData(parameter.Alignment.FixedImage);
#    pts = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
#    Plot.plotOverlayPoints(0.01 * refdata, pts)
#
#
#runVoxelization(parameter);
#
#print "Voxelization done!"
#
#if verbose:
#    #voxdata = io.readData(parameter.Alignment.FixedImage);
#    voxdata = io.readData(parameter.Voxelization.File);
#    points  = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile)
#    Plot.plotOverlayPoints(voxdata.astype('float') / voxdata.max(), points)
#









