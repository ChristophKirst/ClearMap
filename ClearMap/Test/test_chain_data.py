# -*- coding: utf-8 -*-
"""
Created on Sat Jul 25 16:13:56 2015

@author: ckirst
"""


##############################################################################
# Test Alignment
##############################################################################

import os;

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment, runInitializeElastix

import iDISCO.Alignment.Elastix

basedirectory = '/home/mtllab/Documents/whiskers/shaved/150620-3R';

parameter = Parameter();

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/usr/local/elastix'
    
#moving and reference images
pp = '/home/mtllab/Documents/warping';     
parameter.Alignment.MovingImage = os.path.join(pp, 'half_template_25_right.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'autofluo_resample.tif');
parameter.Alignment.FixedImageMask = None;

#elastix parameter files for alignment
parameter.Alignment.AffineParameterFile  = os.path.join(pp, 'Par0000affine.txt');
parameter.Alignment.BSplineParameterFile = os.path.join(pp, 'Par0000bspline.txt');
#parameter.Alignment.BSplineParameterFile = None;


runInitializeElastix(parameter)
iDISCO.Alignment.Elastix.ElastixSettings.printInfo();

resultDirectory = runAlignment(parameter);

print "Aligned images: result directory: %s" % resultDirectory






##############################################################################
# Test Alignment CFos with Fluorescence to correct for aquisition movements 
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment, runInitializeElastix
from iDISCO.Run import runResampling

import iDISCO.Alignment.Elastix as elx

basedirectory = '/home/mtllab/Documents/whiskers/2ndgroup/C';

parameter = Parameter();


## Resample Fluorescent and CFos images
    
#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (4.0625, 4.0625, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (16, 16, 16);

#Orientation of the Data set wrt reference 
parameter.Resampling.Orientation = (-1,2,3);

#Processes to use for Resampling
parameter.Resampling.Processes = 12;



#Files for Cfos
parameter.Resampling.DataFiles = os.path.join(basedirectory, '150722_0_8xs3-cfos20HFcont_07-48-42/07-48-42_0_8xs3-cfos20HFcont_UltraII_C00_xyz-Table Z\d{4}.ome.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'cfos_resample.tif');

resampledImage = runResampling(parameter);


#Files for flourescent
parameter.Resampling.DataFiles = os.path.join(basedirectory, '150722_0_8xs3-autofluor_10-25-24/10-25-24_0_8xs3-autofluor_UltraII_C00_xyz-Table Z\d{4}.ome.tif')
parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif');

resampledImage = runResampling(parameter);



##############################################################################
# Test Alignment CFos with Fluorescence to correct for acquisition movements 
##############################################################################

import os
import numpy

from iDISCO.Parameter import *
from iDISCO.Run import runAlignment, runInitializeElastix
from iDISCO.Run import runResampling

import iDISCO.Alignment.Elastix as elx

basedirectory = '/home/mtllab/Documents/whiskers/2ndgroup/C';

parameter = Parameter();


## Align 

#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix_cfos_auto');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/usr/local/elastix'
    
#moving and reference images
   
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'cfos_resample.tif');
parameter.Alignment.FixedImageMask = None;


#elastix parameter files for alignment
pp = '/home/mtllab/Documents/warping'; 
parameter.Alignment.AffineParameterFile  = os.path.join(pp, 'Par0000affine_cfos.txt');
#parameter.Alignment.BSplineParameterFile = os.path.join(pp, 'Par0000bspline_cfos.txt');
parameter.Alignment.BSplineParameterFile = None;


runInitializeElastix(parameter)
elx.ElastixSettings.printInfo();

resultDirectory = runAlignment(parameter);

print "Aligned cfos with autofluo: result directory: %s" % resultDirectory






##############################################################################
# Test Transform data auto to cfos
############################################################################## 

from iDISCO.Parameter import *
import iDISCO.Alignment.Elastix as elx
import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

basedirectory = '/home/mtllab/Documents/whiskers/2ndgroup/C';

resultdir = os.path.join(basedirectory, 'elastix_cfos_auto');
transformfile = elx.getTransformParameterFile(resultdir)

# tranform points according to alignment of data and reference 
resamplefile = os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif');
transformdir = os.path.join(basedirectory, 'transform_data_cfos_auto')

elx.initializeElastix('/usr/local/elastix')
elx.ElastixSettings.printInfo()

#elx.transformData(dataresname, alignmentdirectory = resultdir, outdirectory = dataalgname)
elx.transformData(resamplefile, transformparameterfile = transformfile, outdirectory = transformdir)
   








##############################################################################
# Transform Points from Cfos to Autofluo
############################################################################## 

import os

from iDISCO.Parameter import *
from iDISCO.Run import runInitializeElastix, runCellCoordinateTransformationToReference
from iDISCO.Run import runCellCoordinateResampling, runCellCoordinateTransformation

import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

import iDISCO.Analysis.Voxelization as vox;

from iDISCO.Alignment.Resampling import dataSize


basedirectory = '/home/mtllab/Documents/whiskers/2ndgroup/C';

verbose = True;

parameter = Parameter();

##Cells
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells.csv')
#parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'cells_transformed_cfos_to_auto.csv');
parameter.ImageProcessing.CellTransformedCoordinateFile = None;
##Resampling Parameter
#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, '150722_0_8xs3-cfos20HFcont_07-48-42/07-48-42_0_8xs3-cfos20HFcont_UltraII_C00_xyz-Table Z\d{4}.ome.tif')
#parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');


#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (4.0625, 4.0625, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (16, 16, 16);

#Orientation of the Data set wrt reference 
parameter.Resampling.Orientation = (-1,2,3);


##Alignment Parameter
#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix_cfos_auto');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/usr/local/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif');
parameter.Alignment.FixedImage  = os.path.join(basedirectory, 'cfos_resample.tif');
parameter.Alignment.FixedImageMask = None;
  
#elastix parameter files for alignment
#parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, '');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');#
#parameter.Alignment.BSplineParameterFile = None;

runInitializeElastix(parameter);

pts = runCellCoordinateTransformation(parameter);

io.writePoints(os.path.join(basedirectory, 'cells_to_autofluo.csv'), pts);


## Visualize cfos to auto points
parameter.ImageProcessing.CellCoordinateFile = pts;
parameter.ImageProcessing.CellTransformedCoordinateFile = None;

pts2 = runCellCoordinateResampling(parameter)

ds = dataSize(os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif'));

voximg = vox.voxelizePixel(pts2, ds);
io.writeDataStack(os.path.join(basedirectory, 'points_transformed_cfos_to_auto.tif'), voximg)

#pts0 = io.readPoints(os.path.join(basedirectory, 'cells.csv'));


##############################################################################
# Transform Points matched to Autofluorescence to Atlas Reference
############################################################################## 

import os

from iDISCO.Parameter import *
from iDISCO.Run import runInitializeElastix, runCellCoordinateTransformationToReference


import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

import iDISCO.Analysis.Voxelization as vox;


basedirectory = '/home/mtllab/Documents/whiskers/2ndgroup/C';

verbose = True;

parameter = Parameter();

##Cells
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells_to_autofluo.csv')
parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'cells_transformed.csv');
##Resampling Parameter
#Files
parameter.Resampling.DataFiles = os.path.join(basedirectory, 'autofluo_for_cfos_resample.tif');
#parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');


#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (16, 16, 16);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (25, 25, 25);

#Orientation of the Data set wrt reference
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);


##Alignment Parameter
#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/usr/local/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, '150722_0_8xs3-autofluor_10-25-24/10-25-24_0_8xs3-autofluor_UltraII_C00_xyz-Table Z\d{4}.ome.tif');
parameter.Alignment.FixedImage  = '/home/mtllab/Documents/warping/half_template_25_right.tif';
parameter.Alignment.FixedImageMask = None;
  
#elastix parameter files for alignment
#parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, '');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');#
#parameter.Alignment.BSplineParameterFile = None;

runInitializeElastix(parameter)


#pts = io.readPoints(parameter.ImageProcessing.CellCoordinateFile);
#pts = pts[0:10000, :];
#pts[0,:] = [0,0,0];
#pts = pts[:, [1,0,2]];

runCellCoordinateTransformationToReference(parameter)

#pts2 = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
#pts2 = pts2[:,[1,0,2]];


if verbose:
    refdata = io.readData(parameter.Alignment.FixedImage);
    #pts = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
    Plot.plotOverlayPoints(0.1 * refdata, pts2)


refdata.shape

pts2 = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
#pts2 = pts2[:,[1,0,2]];
voximg = vox.voxelizePixel(pts2, refdata.shape);
io.writeDataStack(os.path.join(basedirectory, 'points_transformed_pixel.tif'), voximg)






##############################################################################
# Test Resample Points
############################################################################## 

import os
import numpy;


from iDISCO.Parameter import *
from iDISCO.Run import runResampling
import iDISCO.IO.IO as io
from iDISCO.Visualization import Plot

from iDISCO.Alignment.Resampling import resamplePoints, resamplePointsInverse, dataSize


verbose = False;

basedirectory = '/home/ckirst/Science/Projects/BrainActivityMap/Experiment/FullChainTest/';

parameter = Parameter();

#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (4.0625, 4.0625, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (25, 25, 25);

#Orientation of the Data set wrt reference
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);

#centers
centers = io.readPoints(os.path.join(basedirectory, 'cells.csv'))
print "Center shape: (%d, %d)" % centers.shape


datasize = (2560, 2160, 1728); # takes (y,x,z)
print datasize

rcenters = resamplePoints(centers, datasize, parameter.Resampling.ResolutionData, parameter.Resampling.ResolutionReference, parameter.Resampling.Orientation)
print "Reshaped centers shape: (%d, %d)" % rcenters.shape

if verbose:
    datares = io.readData(os.path.join(basedirectory, 'autofluo_resample.tif'));
    #print "Shape raw: " + str(dataraw.shape)
    print "Shape res: " + str(datares.shape)
    
    #Plot.plotOverlayPoints(dataraw*0.01, centers)er();

    Plot.plotOverlayPoints(datares*0.01, rcenters)
    
io.writePoints(os.path.join(basedirectory, 'cells_resampled.csv'), rcenters)

#save pixel image:
import iDISCO.Analysis.Voxelization as vox;
import iDISCO.IO.IO as io

er();

rdata = io.readData(os.path.join(basedirectory, 'autofluo_resample.tif'));
rcenters = io.readPoints(os.path.join(basedirectory, 'cells_resampled.csv'));
voximg = vox.voxelizePixel(rcenters, rdata.shape);
io.writeDataStack(os.path.join(basedirectory, 'cells_resampled.tif'), voximg.astype('int16'))




##############################################################################
# Transform Points from Raw Data to Reference
############################################################################## 

import os

from iDISCO.Parameter import *
from iDISCO.Run import runInitializeElastix, runCellCoordinateTransformationToReference


import iDISCO.Visualization.Plot as Plot
import iDISCO.IO.IO as io

import iDISCO.Analysis.Voxelization as vox;


basedirectory = '/home/mtllab/Documents/whiskers/shaved/150620-3R';

verbose = True;

parameter = Parameter();

##Cells
parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells.csv')
parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'cells_transformed.csv');
##Resampling Parameter
#Files
parameter.Resampling.DataFiles = '/home/mtllab/Documents/whiskers/shaved/150620-3R/150716_0_8X-autofluor_17-00-34/17-00-34_0_8X-autofluor_UltraII_C00_xyz-Table Z\d{4}.ome.tif';
#parameter.Resampling.ResampledFile = os.path.join(basedirectory, 'Synthetic/test_iDISCO_resample.tif');


#Resolution of the Data (in um / pixel)
parameter.Resampling.ResolutionData = (4.0625, 4.0625, 3);

#Resolution of the Reference / Atlas (in um/ pixel)
parameter.Resampling.ResolutionReference = (25, 25, 25);

#Orientation of the Data set wrt reference
#(-axis will invert the orientation, for other hemisphere use (-1, 2, 3), to exchnge x,y use (2,1,3) etc)
parameter.Resampling.Orientation = (1,2,3);


##Alignment Parameter
#directory of the alignment result
parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#Elastix binary
parameter.Alignment.ElastixDirectory = '/usr/local/elastix'
    
#moving and reference images
parameter.Alignment.MovingImage = os.path.join(basedirectory, 'autofluo_resample.tif');
parameter.Alignment.FixedImage  = '/home/mtllab/Documents/warping/half_template_25_right.tif';
parameter.Alignment.FixedImageMask = None;
  
#elastix parameter files for alignment
#parameter.Alignment.AffineParameterFile  = os.path.join(parameter.Alignment.AlignmentDirectory, '');
#parameter.Alignment.BSplineParameterFile = os.path.join(parameter.Alignment.AlignmentDirectory, 'ElastixParameterBSpline.txt');#
#parameter.Alignment.BSplineParameterFile = None;

runInitializeElastix(parameter)


parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells.csv')
pts = io.readPoints(parameter.ImageProcessing.CellCoordinateFile);
#pts = pts[0:10000, :];
#pts[0,:] = [0,0,0];
#pts = pts[:, [1,0,2]];

parameter.ImageProcessing.CellCoordinateFile = pts;

runCellCoordinateTransformationToReference(parameter)

pts2 = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
#pts2 = pts2[:,[1,0,2]];

if verbose:
    refdata = io.readData(parameter.Alignment.FixedImage);
    #pts = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
    Plot.plotOverlayPoints(0.1 * refdata, pts2)


refdata.shape

pts2 = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);
#pts2 = pts2[:,[1,0,2]];
voximg = vox.voxelizePixel(pts2, refdata.shape);
io.writeDataStack(os.path.join(basedirectory, 'points_transformed_pixel.tif'), voximg)







##############################################################################
# Test VTK 
############################################################################## 

import os

from iDISCO.Parameter import *
import iDISCO.IO.IO as io
import iDISCO.IO.VTK as iovtk


basedirectory = '/home/mtllab/Documents/whiskers/shaved/150620-3R';

##Cells
parameter = Parameter();

parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'cells_transformed.csv');

ptsv = io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);

iovtk.writePoints(os.path.join(basedirectory, 'points_transformed.vtk'), ptsv, labelimage = '/home/mtllab/Documents/warping/annotation_25_right.tif')





##############################################################################
# Test points in original data to tif
############################################################################## 

import os

from iDISCO.Parameter import *
import iDISCO.IO.IO as io

from iDISCO.Alignment.Resampling import dataSize

import iDISCO.Analysis.Voxelization as vox

basedirectory = '/home/mtllab/Documents/whiskers/shaved/150620-3R';

##Cells
parameter = Parameter();

parameter.ImageProcessing.CellCoordinateFile = os.path.join(basedirectory, 'cells.csv');


parameter.DataSource.ImageFile = '/home/mtllab/Documents/whiskers/shaved/150620-3R/150716_0_8X-autofluor_17-00-34/17-00-34_0_8X-autofluor_UltraII_C00_xyz-Table Z\d{4}.ome.tif';


pts = io.readPoints(parameter.ImageProcessing.CellCoordinateFile);


ds = dataSize(cFosFile);
ds = (ds[1], ds[0], ds[2]);

voximg = vox.voxelizePixel(pts, ds);
io.writeDataStack(os.path.join(basedirectory, 'points_pixel.tif'), 5000 * voximg)




##############################################################################
# Test label points 
############################################################################## 

import os

from iDISCO.Parameter import *
import iDISCO.IO.IO as io

import iDISCO.Analysis.Label as lb


basedirectory = '/home/mtllab/Documents/whiskers/shaved/150620-3R';

##Cells
parameter = Parameter();

parameter.ImageProcessing.CellTransformedCoordinateFile = os.path.join(basedirectory, 'cells_transformed.csv');

pts =  io.readPoints(parameter.ImageProcessing.CellTransformedCoordinateFile);


labs = lb.labelPoints(pts, '/home/mtllab/Documents/warping/annotation_25_right.tif');

##
counts = lb.countPointsInRegions(pts, '/home/mtllab/Documents/warping/annotation_25_right.tif');

print counts




##############################################################################
# Test label
############################################################################## 

import iDISCO.Analysis.Label as lbl


#l = [317, 997, 1058, 650]
col = lbl.makeColorPalette()


##############################################################################
# Misc / Test Transform Points
############################################################################## 

import iDISCO.Visualization.Plot as Plot;

import iDISCO.Alignment.Elastix as elx;

import iDISCO.Analysis.Voxelization as vox
import iDISCO.IO.IO as io

elx.initializeElastix('/home/ckirst/programs/elastix')
elx.ElastixSettings.printInfo()

verbose = True;

parameter.Alignment.AlignmentDirectory = os.path.join(basedirectory, 'elastix');

#rcenters = numpy.array([[0,0,0],[0,52,0], [0,0,23], [74,0,0],[74,52,0]]);

#acenters = elx.transformPoints(rcenters, alignmentdirectory = parameter.Alignment.AlignmentDirectory, outdirectory = pointsdir);

#rcenters = io.readPoints(os.path.join(basedirectory, 'cells_resampled.csv'));

rcenters2 = rcenters.copy();
rcenters2 = rcenters2[:, [1,0,2]];
print rcenters2.shape

acenters = elx.transformPoints(rcenters2, alignmentdirectory = parameter.Alignment.AlignmentDirectory);

acenters2 = acenters.copy();
acenters2 = acenters2[:, [1,0,2]];

#print acenters

#rdata = io.readData(os.path.join(basedirectory, 'autofluo_resample.tif'));
rdata = io.readData(os.path.join(basedirectory, 'half_template_25_right.tif'));

voximg = vox.voxelizePixel(acenters2, rdata.shape) * 5000;
io.writeDataStack(os.path.join(basedirectory, 'cells_transformed.tif'), voximg.astype('int16'))







