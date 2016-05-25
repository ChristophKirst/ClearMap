# -*- coding: utf-8 -*-
"""
Converts point data into voxel image data for visulaization and analysis
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import numpy
import math

import pyximport;
pyximport.install(setup_args={"include_dirs":numpy.get_include()}, reload_support=True)

import ClearMap.IO as io
import ClearMap.Analysis.VoxelizationCode as vox

def voxelize(points, dataSize = None, sink = None, voxelizeParameter = None,  method = 'Spherical', size = (5,5,5), weights = None):
    """Converts a list of points into an volumetric image array
    
    Arguments:
        points (array): point data array
        dataSize (tuple): size of final image
        sink (str, array or None): the location to write or return the resulting voxelization image, if None return array
        voxelizeParameter (dict):
            ========== ==================== ===========================================================
            Name       Type                 Descritption
            ========== ==================== ===========================================================
            *method*   (str or None)        method for voxelization: 'Spherical', 'Rectangular' or 'Pixel'
            *size*     (tuple)              size parameter for the voxelization
            *weights*  (array or None)      weights for each point, None is uniform weights                          
            ========== ==================== ===========================================================      
    Returns:
        (array): volumetric data of smeared out points
    """
    
    if dataSize is None:
        dataSize = tuple(int(math.ceil(points[:,i].max())) for i in range(points.shape[1]));
    elif isinstance(dataSize, basestring):
        dataSize = io.dataSize(dataSize);
    
    points = io.readPoints(points);
        
    if method.lower() == 'spherical':
        if weights is None:
            data = vox.voxelizeSphere(points.astype('float'), dataSize[0], dataSize[1], dataSize[2], size[0], size[1], size[2]);
        else:
            data = vox.voxelizeSphereWithWeights(points.astype('float'), dataSize[0], dataSize[1], dataSize[2], size[0], size[1], size[2], weights);
           
    elif method.lower() == 'rectangular':
        if weights is None:
            data = vox.voxelizeRectangle(points.astype('float'), dataSize[0], dataSize[1], dataSize[2], size[0], size[1], size[2]);
        else:
            data = vox.voxelizeRectangleWithWeights(points.astype('float'), dataSize[0], dataSize[1], dataSize[2], size[0], size[1], size[2], weights);
    
    elif method.lower() == 'pixel':
        data = voxelizePixel(points, dataSize, weights);
        
    else:
        raise RuntimeError('voxelize: mode: %s not supported!' % method);
    
    return io.writeData(sink, data);


def voxelizePixel(points,  dataSize = None, weights = None):
    """Mark pixels/voxels of each point in an image array
    
    Arguments:
        points (array): point data array
        dataSize (tuple or None): size of the final output data, if None size is determined by maximal point coordinates
        weights (array or None): weights for each points, if None weights are all 1s.
    
    Returns:
        (array): volumetric data with with points marked in voxels
    """
    
    if dataSize is None:
        dataSize = tuple(int(math.ceil(points[:,i].max())) for i in range(points.shape[1]));
    elif isinstance(dataSize, basestring):
        dataSize = io.dataSize(dataSize);
    
    if weights is None:
        vox = numpy.zeros(dataSize, dtype=numpy.int16);
        for i in range(points.shape[0]):
            if points[i,0] > 0 and points[i,0] < dataSize[0] and points[i,1] > 0 and points[i,1] < dataSize[1] and points[i,2] > 0 and points[i,2] < dataSize[2]:
                vox[points[i,0], points[i,1], points[i,2]] += 1;
    else:
        vox = numpy.zeros(dataSize, dtype=weights.dtype);
        for i in range(points.shape[0]):
            if points[i,0] > 0 and points[i,0] < dataSize[0] and points[i,1] > 0 and points[i,1] < dataSize[1] and points[i,2] > 0 and points[i,2] < dataSize[2]:
                vox[points[i,0], points[i,1], points[i,2]] += weights[i];
    
    return  vox;



def test():
    """Test voxelization module"""
    
    import iDISCO.Analysis.Voxelization as self
    reload(self)
    
    import iDISCO.Analysis.VoxelizationCode as vox
    import numpy
    
    
    points = numpy.random.rand(200,3) * 10;
    
    #use cython code
    vi = vox.voxelizeSphere(points, 20,20,20, 5,5,5);
    
    import iDISCO.Visualization.Plot as Plot

    Plot.plotTiling(vi)
    
    #use voxelize
    vi = self.voxelize(points, dataSize = (20,20,20), average = (5,5,5));
    
    Plot.plotTiling(vi)
    
    
    #weighted voxelization 
    points = numpy.random.rand(10,3) * 10;    
    weights = numpy.random.rand(10);
    
    #use voxelize
    vi = self.voxelize(points, dataSize = (20,20,20), average = (5,5,5));
    viw =  self.voxelize(points, dataSize = (20,20,20), average = (5,5,5), weights = weights);
    
    Plot.plotTiling(vi)
    Plot.plotTiling(viw)
    
   
if __name__ == "__main__":
    test();