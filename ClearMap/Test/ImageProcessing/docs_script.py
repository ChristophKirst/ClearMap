# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 04:29:29 2015

@author: ckirst
"""

import os
import ClearMap.Settings as settings
filename = os.path.join(settings.ClearMapPath, 'Test/Data/ImageAnalysis/cfos-substack.tif');
import ClearMap.Visualization.Plot as plt
import ClearMap.IO as io
data = io.readData(filename, z = (0,30));
plt.plotTiling(data, inverse = True, z = (10,16));


#import ClearMap.ImageProcessing.ImageStatistics as stat
#stat.calculateStatistics(filename, method = 'mean', verbose = True)

import ClearMap.ImageProcessing.BackgroundRemoval as bgr

dataBGR = bgr.removeBackground(data.astype('float'), size=(10,10), verbose = True);
plt.plotTiling(dataBGR, inverse = True, z = (10,16));



from ClearMap.ImageProcessing.Filter.DoGFilter import filterDoG
dataDoG = filterDoG(dataBGR, size=(8,8,4), verbose = True);
plt.plotTiling(dataDoG, inverse = True, z = (10,16));



import os
import ClearMap.Settings as settings
filename = os.path.join(settings.ClearMapPath, 'Test/Data/ImageAnalysis/cfos-substack.tif');
import ClearMap.Visualization.Plot as plt
import ClearMap.IO as io
data = io.readData(filename, z = (0,26));
import ClearMap.ImageProcessing.BackgroundRemoval as bgr
dataBGR = bgr.removeBackground(data.astype('float'), size=(3,3), verbose = True);
#plt.plotTiling(dataBGR, inverse = True, z = (10,16));

from ClearMap.ImageProcessing.Filter.DoGFilter import filterDoG
dataDoG = filterDoG(dataBGR, size=(8,8,4), verbose = True);
#plt.plotTiling(dataDoG, inverse = True, z = (10,16));

from ClearMap.ImageProcessing.MaximaDetection import findExtendedMaxima
dataMax = findExtendedMaxima(dataDoG, hMax = None, verbose = True, threshold = 10);
#plt.plotOverlayLabel(  dataDoG / dataDoG.max(), dataMax.astype('int'), z = (10,16))



from ClearMap.ImageProcessing.MaximaDetection import findCenterOfMaxima
cells = findCenterOfMaxima(data, dataMax);
print cells.shape

plt.plotOverlayPoints(data, cells, z = (10,16))


from ClearMap.ImageProcessing.CellSizeDetection import detectCellShape        
dataShape = detectCellShape(dataDoG, cells, threshold = 15);
plt.plotOverlayLabel(dataDoG / dataDoG.max(), dataShape, z = (10,16))


# find intensities / cell sizes
from ClearMap.ImageProcessing.CellSizeDetection import findCellSize, findCellIntensity

#size of cells        
cellSizes = findCellSize(dataShape, maxLabel = cells.shape[0]);

#intensity of cells
cellIntensities = findCellIntensity(dataBGR, dataShape,  maxLabel = cells.shape[0]);

 
import matplotlib.pyplot as mpl 

mpl.figure()
mpl.plot(cellSizes, cellIntensities, '.')
mpl.xlabel('cell sizes [voxel]')
mpl.ylabel('cell intensities [au]')

 
 

