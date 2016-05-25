# -*- coding: utf-8 -*-
"""
Routines to run iDISCO alignment and cell detection

Created on Fri Jun 19 12:20:18 2015

@author: ckirst
"""

#import os

from iDISCO.Parameter import *
from iDISCO.IO import IO as io
import iDISCO.ImageProcessing.SpotDetection

try:
    import iDISCO.ImageProcessing.IlastikClassification
    haveIlastik = True;
except:
    haveIlastik = False;

from iDISCO.ImageProcessing.StackProcessing import parallelProcessStack, sequentiallyProcessStack

from iDISCO.Alignment.Elastix import transformPoints, alignData, initializeElastix

from iDISCO.Utils.Timer import Timer

from iDISCO.Alignment.Resampling import resampleData, resamplePoints, resamplePointsInverse, dataSize

from iDISCO.Analysis.Voxelization import voxelize;
    

def runCellDetection(parameter):
    """Detect cells in data"""
    
    timer = Timer();
    
    pp = parameter.StackProcessing;
    ps = parameter.DataSource;
    
    # run segmentation
    if parameter.ImageProcessing.Method == "SpotDetection":
        
        detectCells = iDISCO.ImageProcessing.SpotDetection.detectCells;
        
        centers, intensities = parallelProcessStack(ps.ImageFile, x = ps.XRange, y = ps.YRange, z = ps.ZRange, 
                                                processes = pp.Processes, chunksizemax = pp.ChunkSizeMax, chunksizemin = pp.ChunkSizeMin, chunkoverlap = pp.ChunkOverlap, 
                                                optimizechunks = pp.OptimizeChunks, optimizechunksizeincrease = pp.OptimizeChunkSizeIncrease,
                                                segmentation = detectCells, parameter = parameter.ImageProcessing);        
        
    else:
        if haveIlastik:
            #ilastik does parallel processing so do sequential processing here
            detectCells = iDISCO.ImageProcessing.IlastikClassification.detectCells;
            
            centers, intensities = sequentiallyProcessStack(ps.ImageFile, x = ps.XRange, y = ps.YRange, z = ps.ZRange, 
                                                        chunksizemax = pp.ChunkSizeMax, chunksizemin = pp.ChunkSizeMin, chunkoverlap = pp.ChunkOverlap,
                                                        segmentation = detectCells, parameter = parameter.ImageProcessing);
            
        else:
            raise RuntimeError("No Ilastik installed use SpotDectection instead!");
            
 
    timer.printElapsedTime("Main");
    
    if not parameter.ImageProcessing.Parameter.ThresholdSave is None:
        iid = intensities >  parameter.ImageProcessing.Parameter.ThresholdSave;
        centers = centers[iid,:];

    if not parameter.ImageProcessing.PointFile is None:
        io.writePoints(parameter.ImageProcessing.PointFile, centers);
        
    if not parameter.ImageProcessing.IntensityFile is None:
        io.writePoints(parameter.ImageProcessing.IntensityFile, intensities);

    return centers, intensities;



def runInitializeElastix(parameter):
    """Initialize elastix enviroment"""
    
    ed = parameter.Alignment.ElastixDirectory;
    
    initializeElastix(ed);
    
    return ed;


def runAlignment(parameter):
    """Align data"""
    
    pa = parameter.Alignment;
    
    fi = pa.FixedImage;
    mi = pa.MovingImage;
    
    af = pa.AffineParameterFile;
    bf = pa.BSplineParameterFile;
    
    od = pa.AlignmentDirectory;
    
    alignData(fi, mi, af, bf, od);
        
    return od;
    
    
    
def runResampling(parameter):
    """Resample data"""
    
    rp = parameter.Resampling;
    
    im = rp.Source;
    if im is None:    
        im = parameter.DataSource.ImageFile;
    
    resampleData(im, outputFile = rp.ResampledFile, 
                 resolutionData = rp.ResolutionData, resolutionReference = rp.ResolutionReference,
                 processingDirectory = None, processes = rp.Processes, cleanup = True, orientation = rp.Orientation);
    
    return rp.ResampledFile;
    


def runCellCoordinateResampling(parameter):
    """Transform points by resampling"""
    
    im = parameter.Resampling.DataFiles;
    if im is None:    
        im = parameter.DataSource.ImageFile;
        
    cf = parameter.ImageProcessing.CellCoordinateFile;
    pr = parameter.Resampling;
    
    # downscale points to referenece image size
    points = resamplePoints(cf, im, resolutionData = pr.ResolutionData, resolutionReference = pr.ResolutionReference, orientation = pr.Orientation);
        
    tf = parameter.ImageProcessing.CellTransformedCoordinateFile;
    if tf is None:
        return points;
    else:
        io.writePoints(tf, points);
        return tf;
    

def runCellCoordinateTransformation(parameter):
    """Transform points by resampling applying the elastix transformation and then re-resample again"""
    
    im = parameter.Resampling.DataFiles;
    if im is None:    
        im = parameter.DataSource.ImageFile;
        
    cf = parameter.ImageProcessing.CellCoordinateFile;
    pa = parameter.Alignment;
    pr = parameter.Resampling;
    
    # downscale points to referenece image size
    points = resamplePoints(cf, im, resolutionData = pr.ResolutionData, resolutionReference = pr.ResolutionReference, orientation = pr.Orientation);
    
    # transform points
    points = points[:,[1,0,2]]; # account for (y,x, z) array representaton here
    points = transformPoints(points, alignmentdirectory = pa.AlignmentDirectory, transformparameterfile = None, read = True, tmpfile = None, outdirectory = None, indices = False);
    points = points[:,[1,0,2]]; # account for (y,x, z) array representaton here
    
    # upscale ppints back to original size
    points = resamplePointsInverse(points, im, resolutionData = pr.ResolutionData, resolutionReference = pr.ResolutionReference, orientation = pr.Orientation);
    
    tf = parameter.ImageProcessing.CellTransformedCoordinateFile;
    if tf is None:
        return points;
    else:
        io.writePoints(tf, points);
        return tf;
    
def runCellCoordinateTransformationToReference(parameter):
    """Transform points by resampling and applying the elastix transformation in the reference data"""
    
    im = parameter.Resampling.DataFiles;
    if im is None:    
        im = parameter.DataSource.ImageFile;
    
    cf = parameter.ImageProcessing.CellCoordinateFile;
    pa = parameter.Alignment;
    pr = parameter.Resampling;
    
    # downscale points to referenece image size
    points = resamplePoints(cf, im, resolutionData = pr.ResolutionData, resolutionReference = pr.ResolutionReference, orientation = pr.Orientation);
    
    # transform points
    #points = points[:,[1,0,2]];
    points = transformPoints(points, alignmentdirectory = pa.AlignmentDirectory, transformparameterfile = None, read = True, tmpfile = None, outdirectory = None, indices = True);
    #points = points[:,[1,0,2]];
    
    tf = parameter.ImageProcessing.CellTransformedCoordinateFile;
    if tf is None:
        return points;
    else:
        io.writePoints(tf, points);
        return tf;

    
def runVoxelization(parameter):
    """Voxelize a set of points"""
    
    cf = parameter.ImageProcessing.CellTransformedCoordinateFile;
    if cf is None:
        cf =  parameter.ImageProcessing.CellCoordinateFile;
    
    points = io.readPoints(cf);
    
    pv = parameter.Voxelization;

    si = pv.Size;
    if si is None:
        si = parameter.Alignment.MovingImage;
        if si is None:    
            si = parameter.Resampling.ResampledFile;
            
    if isinstance(si, basestring):
        si = dataSize(si);
        
    print si

    vox = voxelize(points, si, average = pv.AveragingDiameter, mode = pv.Mode);
    
    vf = pv.File;
    if vf is None:
        return vox;
    else:
        io.writeDataStack(vf, vox.astype('int32'));
        return vf;
