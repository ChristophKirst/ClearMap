# -*- coding: utf-8 -*-
"""
Created on Sun Jul 19 11:42:52 2015

Test Transformation with Elastix - Points vs Data

Notes:

- Elastix provides transform T: fixed -> moving
- for alignment use fixed = data and moving = atlas / reference
- result.mdh in elastix directory is T^(-1) moving, i.e. has size of fixed image
- result of transformix on points is T fixed
- transforming data with transformix uses T^(-1)
- transformix points are (x,y,z) as displayed e.g. by imagej
- array representation uses (y,x,z)
- points detected here are thus (y,x,z) coordinates


@author: ckirst
"""


##############################################################################
# Test Resampling / Make Reference
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import runResampling

import shutil

basedirectory = os.path.join(iDISCOPath(), 'Test');

parameter = Parameter();

#Resampled Data

#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (5, 5, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (12, 15, 5);

#Orientation of the Data set wrt reference 
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchange x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);

#Processes to use for Resampling
parameter.Resampling.Processes = 4;

resampledImage = runResampling(parameter);

print "Resampled image saved as %s" % resampledImage


# Reference

#shutil.copyfile(resampledImage, os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif'))
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');
parameter.Resampling.ResolutionReference = (10, 17, 5);
resampledImage = runResampling(parameter);



##############################################################################
# Test Alignment
##############################################################################

import os

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment, runInitializeElastix

import iDISCO.Alignment.Elastix

basedirectory = os.path.join(iDISCOPath(), 'Test');

parameter = Parameter();

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'Synthetic/elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix'
    
#moving and reference images> points transform according to: fixed to moving (i.e. resample to reference!)
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');
parameter.Alignment.FixedImageMask = None;  
  
#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');
parameter.Alignment.BSplineParameterFile = None;


runInitializeElastix(parameter)
iDISCO.Alignment.Elastix.ElastixSettings.printInfo();

resultDirectory = runAlignment(parameter);

print "Aligned images: result directory: %s" % resultDirectory



##############################################################################
# Test Transform Points
############################################################################## 

import iDISCO.Visualization.Plot as Plot;

import iDISCO.Alignment.Elastix as elx;

import iDISCO.Analysis.Voxelization as vox
import iDISCO.IO.IO as io

elx.initializeElastix('/home/ckirst/programs/elastix')
elx.ElastixSettings.printInfo()

verbose = True;

parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'Synthetic/elastix');

rcenters = numpy.array([[0,0,0],[0,52,0], [0,0,23], [74,0,0],[74,52,0]]);

#acenters = elx.transformPoints(rcenters, alignmentdirectory = parameter.Alignment.AlignmentDirectory, outdirectory = pointsdir);
acenters = elx.transformPoints(rcenters, alignmentdirectory = parameter.Alignment.AlignmentDirectory);

print acenters





##############################################################################
# Test Transform data
############################################################################## 

from iDISCO.Parameter import *
import iDISCO.Alignment.Elastix as elx
import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

basedirectory = os.path.join(iDISCOPath(), 'Test');

verbose = True;

resultdir = os.path.join(basedirectory, 'Synthetic/elastix');
transformfile = elx.getTransformParameterFile(resultdir)

# tranform points according to alignment of data and reference 
resamplefile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');
transformdir = os.path.join(basedirectory, 'Synthetic/transformix')

elx.initializeElastix('/home/ckirst/programs/elastix')
elx.ElastixSettings.printInfo()

#elx.transformData(dataresname, alignmentdirectory = resultdir, outdirectory = dataalgname)
elx.transformData(resamplefile, transformparameterfile = os.path.join(basedirectory, 'Synthetic/elastix/TransformParameters.0.txt'), outdirectory = transformdir)
   


##############################################################################
# Transform Points from Raw Data to Reference
############################################################################## 

import os

from iDISCO.Parameter import *
from iDISCO.Run import runInitializeElastix, runCellCoordinateTransformationToReference


import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

basedirectory = os.path.join(iDISCOPath(), 'Test');

verbose = True;

parameter = Parameter();

##Cells
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'Synthetic/cells.csv');
parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'Synthetic/cells_transformed.csv');
##Resampling Parameter
#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (5, 5, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (12, 15, 5);

#Orientation of the Data set wrt reference 
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);


##Alignment Parameter
#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'Synthetic/elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');
parameter.Alignment.FixedImageMask = None;
  
#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');
parameter.Alignment.BSplineParameterFile = None;

runInitializeElastix(parameter)

runCellCoordinateTransformationToReference(parameter)

if verbose:
    refdata = io.readData(parameter.Alignment.FixedImage);
    pts = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
    Plot.plotOverlayPoints(0.01 * refdata, pts)




##############################################################################
# Test Voxelization
##############################################################################

import os

from iDISCO.Parameter import *
from iDISCO.Run import runVoxelization

import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

basedirectory = os.path.join(iDISCOPath(), 'Test');

verbose = True;

parameter = Parameter();


#Points
parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'Synthetic/cells_transformed.csv');

#Reference file
parameter.Alignment.FixedImage = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');

##Voxelization
#Size of averaging window
parameter.Voxelization.AveragingDiameter = (15,15,15);  #Radius of the sphere
    
#Image size
parameter.Voxelization.Size = None;  #None extract from data
    
#Mode
parameter.Voxelization.Mode = 'Spherical';
    
#Output File
parameter.Voxelization.File = os.path.join(basedirectory, 'Synthetic/points_voxelized.tif');

runVoxelization(parameter);


if verbose:
    #voxdata = io.readData(parameter.Alignment.FixedImage);
    voxdata = io.readData(parameter.Voxelization.File);
    points  = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile)
    Plot.plotOverlayPoints(voxdata.astype('float') / voxdata.max(), points)









##############################################################################
# Test Full Chain
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import *
import iDISCO.Visualization.Plot as Plot

verbose = True;

basedirectory = os.path.join(iDISCOPath(), 'Test');

parameter = Parameter();


## Resampling to prepare alignment

#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (5, 5, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (12, 15, 5);

#Orientation of the Data set wrt reference 
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);

#Processes to use for Resmapling
parameter.Resampling.Processes = 4;


## Alignment

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'Synthetic/elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/home/ckirst/programs/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'Synthetic/test_iDISCO_reference.tif');
parameter.Alignment.FixedImageMask = None;

#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterAffine.txt');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');
parameter.Alignment.BSplineParameterFile = None;

#initialize elastix
runInitializeElastix(parameter)
iDISCO.Alignment.Elastix.ElastixSettings.printInfo();


## Cell Detection

#raw data from microscope used for cell detection (ims or tif)
parameter.DataSource.ImageFile = os.path.join(basedirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')

#image ranges
parameter.DataSource.XRange = all;
parameter.DataSource.YRange = all;
parameter.DataSource.ZRange = all;

# radius for background removal
parameter.ImageProcessing.Parameter.Background = (20,20);

# size of differeence of gaussian filter
parameter.ImageProcessing.Parameter.Dog = (8, 8, 6);

# h value for h max detection
parameter.ImageProcessing.Parameter.HMax = 0.5;
parameter.ImageProcessing.Parameter.Threshold = 0.5;

# intensity threshold for final cells to be saved
parameter.ImageProcessing.Parameter.ThresholdSave = None;

# result files for cell coordinates (csv, vtk or ims)
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'Synthetic/cells.csv');
parameter.ImageProcessing.CellIntensityFile = os.path.join(basedirectory, 'Synthetic/intensities.csv');
parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'Synthetic/cells_transformed.csv');


## Stack Processing Parameter
    
#max number of parallel processes
parameter.StackProcessing.Processes = 2;
   
#chunk sizes
parameter.StackProcessing.ChunkSizeMax = 100;
parameter.StackProcessing.ChunkSizeMin = 30;
parameter.StackProcessing.ChunkOverlap = 15;

#optimize chunk size and number to number of processes
parameter.StackProcessing.OptimizeChunks = True;
    
#increase chunk size for optimizaition (True, False or all = choose automatically)
parameter.StackProcessing.OptimizeChunkSizeIncrease = all;



##Voxelization

#Size of averaging window
parameter.Voxelization.AveragingDiameter = (15,15,15);  #Radius of the sphere
    
#Image size
parameter.Voxelization.Size = None;  #None extract from data
    
#Mode
parameter.Voxelization.Mode = 'Spherical';
    
#Output File
parameter.Voxelization.File = os.path.join(basedirectory, 'Synthetic/points_voxelized.tif');



##Processing

resampledImage = runResampling(parameter);

print "Resampled image saved as %s" % resampledImage

resultDirectory = runAlignment(parameter);

print "Aligned images: result directory: %s" % resultDirectory

runCellDetection(parameter)

print "Cell detection done!"

runCellCoordinateTransformationToReference(parameter)

print "Cell transformation to reference done!"

if verbose:
    refdata = io.readData(parameter.Alignment.FixedImage);
    pts = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
    Plot.plotOverlayPoints(0.01 * refdata, pts)


runVoxelization(parameter);

print "Voxelization done!"

if verbose:
    #voxdata = io.readData(parameter.Alignment.FixedImage);
    voxdata = io.readData(parameter.Voxelization.File);
    points  = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile)
    Plot.plotOverlayPoints(voxdata.astype('float') / voxdata.max(), points)









##############################################################################
# Test Resampling / Make Reference
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import runResampling

import shutil

basedirectory = os.path.join(iDISCOaPath(), 'Test');

parameter = Parameter();


#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, 'Data/Synthetic/test_iDISCO_\d{3}.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (5, 5, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (12, 15, 5);

#Orientation of the Data set wrt reference 
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchange x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);

#Processes to use for Resampling
parameter.Resampling.Processes = 4;

resampledImage = runResampling(parameter);

print "Resampled image saved as %s" % resampledImage







# voxelize result

voximg = vox.voxelizePixel(acenters, referencedata.shape);
io.writeDataStack(os.path.join(basedirectory, 'Synthetic/points_transformed_pixel.tif'), 5000* voximg)


if verbose:
    transformdata = io.readData(os.path.join(transformdir, 'result.mhd'));
    referencedata = io.readData(os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif'))
    Plot.plotOverlayPoints(transformdata * 0.01, acenters);
    Plot.plotOverlayPoints(referencedata * 0.01, acenters);







