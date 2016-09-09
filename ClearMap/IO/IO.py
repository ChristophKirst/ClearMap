# -*- coding: utf-8 -*-
"""
IO interface to read microscope and point data

This is the main module to distribute the reading and writing of individual data formats to the specialized sub-modules.

See :mod:`ClearMap.IO` for details.

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
self = sys.modules[__name__];

import os
import re
import numpy
import importlib
import shutil

pointFileExtensions = ["csv", "txt", "npy", "vtk", "ims"];
"""list of extensions supported as a point data file"""

pointFileTypes = ["CSV", "NPY", "VTK", "Imaris"];
"""list of point data file types"""

pointFileExtensionToType = {"csv" : "CSV", "txt" : "CSV", "npy" : "NPY", "vtk" : "VTK", "ims" : "Imaris"};
"""map from point file extensions to point file types"""


dataFileExtensions = ["tif", "tiff", "mhd", "raw", "ims", "nrrd"];
"""list of extensions supported as a image data file"""

dataFileTypes = ["FileList", "TIF", "RAW", "NRRD", "Imaris"]
"""list of image data file types"""

dataFileExtensionToType = { "tif" : "TIF", "tiff" : "TIF", "raw" : "RAW", "mhd" : "RAW", "nrrd": "NRRD", "ims" : "Imaris"}
"""map from image file extensions to image file types"""


##############################################################################
# Basic file queries
##############################################################################

def fileExtension(filename):
    """Returns file extension if exists
    
    Arguments:
        filename (str): file name
        
    Returns:
        str: file extension or None
    """
    
    if not isinstance(filename, basestring):
        return None;
    
    fext = filename.split('.');
    if len(fext) < 2:
        return None;
    else:
        return fext[-1];
        
    
def isFile(source):
    """Checks if filename is a real file, returns false if it is directory or regular expression
    
    Arguments:
        source (str): source file name
        
    Returns:
        bool: true if source is a real file   
    """
    
    if not isinstance(source, basestring):
        return False;
  
    if os.path.exists(source):
        if os.path.isdir(source):
            return False;
        else:
            return True;
    else:
        return False;
    

def isFileExpression(source):
    """Checks if filename is a regular expression denoting a file list
    
    Arguments:
        source (str): source file name
        
    Returns:
        bool: true if source is regular expression with a digit label
    """    
    
    if not isinstance(source, basestring):
        return False;
    
    if isFile(source):
        return False;
    else:
        searchRegex = re.compile('.*\\\\d\{(?P<digit>\d)\}.*').search
        m = searchRegex(source);
        if m is None:
            return False;
        else:
            return True;
  

    """Checks if a file is a valid point data file
     
    Arguments:
        source (str): source file name
        
    Returns:
        bool: true if source is a point data file
    """     
    
    if not isinstance(source, basestring):
        return False;
    
    fext = fileExtension(source);
    if fext in pointFileExtensions:
        return True;
    else:
        return False;

        
def isDataFile(source):
    """Checks if a file is a valid image data file
     
    Arguments:
        source (str): source file name
        
    Returns:
        bool: true if source is an image data file
    """   
    
    if not isinstance(source, basestring):
        return False;    
    
    fext = fileExtension(source);
    if fext in dataFileExtensions:
        return True;
    else:
        return False;

          
def createDirectory(filename):
    """Creates the directory of the file if it does not exists
     
    Arguments:
        filename (str): file name
        
    Returns:
        str: directory name
    """       
    
    dirname, fname = os.path.split(filename);
    if not os.path.exists(dirname):
        os.makedirs(dirname);
    
    return dirname;


def pointFileNameToType(filename):
    """Returns type of a point file
    
    Arguments:
        filename (str): file name
        
    Returns:
        str: point data type in :const:`pointFileTypes`
    """       
    
    #if not self.isFile(filename):
    #    raise RuntimeError("Cannot find point file %s" % filename);
    #else:
    fext = fileExtension(filename);
    if fext in pointFileExtensions:
        return pointFileExtensionToType[fext];
    else:
       raise RuntimeError("Cannot determine type of point file %s with extension %s" % (filename, fext));     


def dataFileNameToType(filename):
    """Returns type of a image data file
    
    Arguments:
        filename (str): file name
        
    Returns:
        str: image data type in :const:`dataFileTypes`
    """      
    
    if isFileExpression(filename):
        return "FileList";
    else:
        fext = fileExtension(filename);
        if fext in dataFileExtensions:
            return dataFileExtensionToType[fext];
        else:
           raise RuntimeError("Cannot determine type of data file %s with extension %s" % (filename, fext));


def dataFileNameToModule(filename):
    """Return the module that handles io for a data file
        
    Arguments:
        filename (str): file name
        
    Returns:
        object: sub-module that handles a specific data type
    """          
    
    ft = dataFileNameToType(filename);
    return importlib.import_module("ClearMap.IO." + ft);


def pointFileNameToModule(filename):
    """Return the module that handles io for a point file
        
    Arguments:
        filename (str): file name
        
    Returns:
        object: sub-module that handles a specific point file type
    """ 

    ft = pointFileNameToType(filename);
    return importlib.import_module("ClearMap.IO." + ft);



##############################################################################
# Data Sizes and Ranges
##############################################################################

    
def dataSize(source, x = all, y = all, z = all, **args):
    """Returns array size of the image data needed when read from file and reduced to specified ranges
       
    Arguments:
        source (array or str): source data
        x,y,z (tuple or all): range specifications, ``all`` is full range
        
    Returns:
        tuple: size of the image data after reading and range reduction
    """ 
    
    if isinstance(source, basestring):
        mod = dataFileNameToModule(source);
        return mod.dataSize(source, x = x, y = y, z = z, **args);
    elif isinstance(source, numpy.ndarray):
        return dataSizeFromDataRange(source.shape, x = x, y = y, z = z);
    elif isinstance(source, tuple):
        return dataSizeFromDataRange(source, x = x, y = y, z = z);
    else:
        raise RuntimeError("dataSize: argument not a string, tuple or array!");
            
    
def dataZSize(source, z = all, **args):
    """Returns size of the array in the third dimension, None if 2D data
           
    Arguments:
        source (array or str): source data
        z (tuple or all): z-range specification, ``all`` is full range
        
    Returns:
        int: size of the image data in z after reading and range reduction
    """ 
      
    if isinstance(source, basestring):
        mod = dataFileNameToModule(source);
        return mod.dataZSize(source, z = z, **args);
    elif isinstance(source, numpy.ndarray):
        if len(source.shape) > 2: 
            return toDataSize(source.shape[2], r = z);
        else:
            return None;
    elif isinstance(source, tuple):
        if len(source) > 2: 
            return toDataSize(source[2], r = z);
        else:
            return None;
    else:
        raise RuntimeError("dataZSize: argument not a string, tuple or array!");        


def toDataRange(size, r = all):
    """Converts range r to numeric range (min,max) given the full array size
       
    Arguments:
        size (tuple): source data size
        r (tuple or all): range specification, ``all`` is full range
        
    Returns:
        tuple: absolute range as pair of integers
    
    See Also:
        :func:`toDataSize`, :func:`dataSizeFromDataRange`
    """     

    if r is all:
        return (0,size);
    
    if isinstance(r, int) or isinstance(r, float):
        r = (r, r +1);
      
    if r[0] is all:
        r = (0, r[1]);
    if r[0] < 0:
        if -r[0] > size:
            r = (0, r[1]);
        else:
            r = (size + r[0], r[1]);
    if r[0] > size:
        r = (size, r[1]);
        
    if r[1] is all:
        r = (r[0], size);
    if r[1] < 0:
        if -r[1] > size:
            r = (r[0], 0);
        else:
            r = (r[0], size + r[1]);
    if r[1] > size:
        r = (r[0], size);
    
    if r[0] > r[1]:
        r = (r[0], r[0]);
    
    return r;

        
def toDataSize(size, r = all):
    """Converts full size to actual size given range r
    
    Arguments:
        size (tuple): data size
        r (tuple or all): range specification, ``all`` is full range
        
    Returns:
        int: data size
    
    See Also:
        :func:`toDataRange`, :func:`dataSizeFromDataRange`
    """
    dr = toDataRange(size, r = r);
    return int(dr[1] - dr[0]);


def dataSizeFromDataRange(dataSize, x = all, y = all, z = all, **args):
    """Converts full data size to actual size given ranges for x,y,z
    
    Arguments:
        dataSize (tuple): data size
        x,y,z (tuple or all): range specifications, ``all`` is full range
        
    Returns:
        tuple: data size as tuple of integers
    
    See Also:
        :func:`toDataRange`, :func:`toDataSize`
    """    
    
    dataSize = list(dataSize);
    n = len(dataSize);
    if n > 0:
        dataSize[0] = toDataSize(dataSize[0], r = x);
    if n > 1:
        dataSize[1] = toDataSize(dataSize[1], r = y);
    if n > 2:
        dataSize[2] = toDataSize(dataSize[2], r = z);
    
    return tuple(dataSize);




def dataToRange(data, x = all, y = all, z = all, **args):
    """Reduces data to specified ranges
    
    Arguments:
        data (array): full data array
        x,y,z (tuple or all): range specifications, ``all`` is full range
        
    Returns:
        array: reduced data
    
    See Also:
        :func:`dataSizeFromDataRange`
    """  
    dsize = data.shape;
    d = len(dsize);
    rr = [];
    if d > 0:
        rr.append(toDataRange(dsize[0], r = x));
    if d > 1:
        rr.append(toDataRange(dsize[1], r = y));
    if d > 2:
        rr.append(toDataRange(dsize[2], r = z));
    if d > 4:
        raise RuntimeError('dataToRange: dimension %d to big' % d);
    
    if d == 1:
        return data[rr[0][0] : rr[0][1]];
    elif d == 2:
        return data[rr[0][0] : rr[0][1], rr[1][0] : rr[1][1]];
    elif d == 3:
        return data[rr[0][0] : rr[0][1], rr[1][0] : rr[1][1], rr[2][0] : rr[2][1]];
    elif d == 4:
        return data[rr[0][0] : rr[0][1], rr[1][0] : rr[1][1], rr[2][0] : rr[2][1], :];   
    else:
        raise RuntimeError('dataToRange dealing with images of dimension %d not supported' % d);
            




##############################################################################
# Read / Write Data
##############################################################################


def readData(source, **args):
    """Read data from one of the supported formats
    
    Arguments:
        source (str, array or None): full data array, if numpy array simply reduce its range
        x,y,z (tuple or all): range specifications, ``all`` is full range
        **args: further arguments specific to image data format reader
    
    Returns:
        array: data as numpy array
    
    See Also:
        :func:`writeData`
    """  
    
    if source is None:
        return None;   
    elif isinstance(source, basestring):
        mod = dataFileNameToModule(source);
        return mod.readData(source, **args);
    elif isinstance(source, numpy.ndarray ):
        return dataToRange(source, **args);
    else:
        raise RuntimeError('readData: cannot infer format of the requested data/file.');


def writeData(sink, data, **args):
    """Write data to one of the supported formats
    
    Arguments:
        sink (str, array or None): the destination for the data, if None the data is returned directly
        data (array or None): data to be written
        **args: further arguments specific to image data format writer
    
    Returns:
        array, str or None: data or file name of the written data
    
    See Also:
        :func:`readData`
    """ 
    
    if sink is None: #dont write to disk but return the data
        return data;
    
    mod = dataFileNameToModule(sink);    
    return mod.writeData(sink, data, **args);





def copyFile(source, sink):
    """Copy a file from source to sink
    
    Arguments:
        source (str): file name of source
        sink (str): file name of sink
    
    Returns:
        str: name of the copied file
    
    See Also:
        :func:`copyData`, :func:`convertData`
    """ 
    
    shutil.copy(source, sink);
    return sink;

def copyData(source, sink):
    """Copy a data file from source to sink, which can consist of multiple files
    
    Arguments:
        source (str): file name of source
        sink (str): file name of sink
    
    Returns:
        str: name of the copied file
    
    See Also:
        :func:`copyFile`, :func:`convertData`
    """     
    
    mod = dataFileNameToModule(source);
    return mod.copyData(source, sink);


def convertData(source, sink, **args):
    """Transforms data from source format to sink format
    
    Arguments:
        source (str): file name of source
        sink (str): file name of sink
    
    Returns:
        str: name of the copied file
        
    Warning:
        Not optimized for large image data sets
    
    See Also:
        :func:`copyFile`, :func:`copyData`
    """      

    if source is None:
        return None;   
    
    elif isinstance(source, basestring):
        if sink is None:        
            return readData(source, **args);
        elif isinstance(sink, basestring):
            if args == {} and dataFileNameToType(source) ==dataFileNameToType(sink):
                return copyData(source, sink);
            else:
                data = readData(source, **args);
                return writeData(sink, data);
        else:
            raise RuntimeError('transformData: unknown sink!');
            
    elif isinstance(source, numpy.ndarray):
        if sink is None:
            return dataToRange(source, **args);
        elif isinstance(sink,  basestring):
            data = dataToRange(source, **args);
            return writeData(sink, data);
        else:
            raise RuntimeError('transformData: unknown sink!');
 
 
def toMultiChannelData(*args):
    """Concatenate single channel arrays to one multi channel array
    
    Arguments:
        *args (arrays): arrays to be concatenated
    
    Returns:
        array: concatenated multi-channel array
    """
    
    data = numpy.array(args);
    return data.rollaxis(data, 0, data.ndim);





##############################################################################
# Read / Write Points
##############################################################################


def pointsToCoordinates(points):
    """Converts a (coordiantes, properties) tuple to the coordinates only
    
    Arguments:
        points (array or tuple): point data to be reduced to coordinates
    
    Returns:
        array: coordiante data
        
    Notes:
        Todo: Move this to a class that handles points and their meta data
    """
    
    if isinstance(points, tuple):
        return points[0];
    else:
        return points;
    

        
def pointsToProperties(points):
    """Converts a (coordiante, properties) tuple to the properties only
    
    Arguments:
        points (array or tuple): point data to be reduced to properties
    
    Returns:
        array: property data
        
    Notes:
        Todo: Move this to a class that handles points and their meta data
    """    
    
    if isinstance(points, tuple) and len(points) > 1:
        return points[1];
    else:
        return None;
        
def pointsToCoordinatesAndProperties(points):
    """Converts points in various formats to a (coordinates, properties) tuple
    
    Arguments:
        points (array or tuple): point data to be converted to (coordinates, properties) tuple
    
    Returns:
        tuple: (coordinates, properties) tuple
        
    Notes:
        Todo: Move this to a class that handles points and their meta data
    """  
    
    if isinstance(points, tuple):
        if len(points) == 0:
            return (None, None);
        elif len(points) == 1:
            return (points[0], None);
        elif len(points) == 2:
            return points;
        else:
            raise RuntimeError('points not a tuple of 0 to 2 elements!');
    else:
        return (points, None);


def pointsToCoordinatesAndPropertiesFileNames(filename, propertiesPostfix = '_intensities', **args):
    """Generates a tuple of filenames to store coordinates and properties data separately
    
    Arguments:
        filename (str): point data file name
        propertiesPostfix (str): postfix on file name to indicate property data
    
    Returns:
        tuple: (file name, file name for properties)
        
    Notes:
        Todo: Move this to a class that handles points and their meta data
    """  
    
    if isinstance(filename, basestring):
        return (filename, filename[:-4] + propertiesPostfix + filename[-4:])
    elif isinstance(filename, tuple):
        if len(filename) == 1:
            if filename[0] is None:
                return (None, None);
            elif isinstance(filename[0], basestring):
                return (filename[0], filename[0][:-4] + propertiesPostfix + filename[0][-4:]);
            else:
                raise RuntimeError('pointsFilenames: invalid filename specification!');
        elif len(filename) == 2:
            return filename;
        else:
            raise RuntimeError('pointsFilenames: invalid filename specification!');
    elif filename is None:
        return (None, None)
    else:
        raise RuntimeError('pointsFilenames: invalid filename specification!');




def pointShiftFromRange(dataSize, x = all, y = all, z = all, **args):
    """Calculate shift of points given a specific range restriction
    
    Arguments:
        dataSize (str): data size of the full image
        x,y,z (tuples or all): range specifications
    
    Returns:
        tuple: shift of points from original origin of data to origin of range reduced data
    """      
    
    if isinstance(dataSize, basestring):
        dataSize = self.dataSize(dataSize);
    dataSize = list(dataSize);
    
    d = len(dataSize);
    rr = [];
    if d > 0:
        rr.append(toDataRange(dataSize[0], r = x));
    if d > 1:
        rr.append(toDataRange(dataSize[1], r = y));
    if d > 2:
        rr.append(toDataRange(dataSize[2], r = z));
    if d > 3 or d < 1:
        raise RuntimeError('shiftFromRange: dimension %d to big' % d);
    
    return [r[0] for r in rr];



def pointsToRange(points, dataSize = all, x = all, y = all, z = all, shift = False,  **args):
    """Restrict points to a specific range
    
    Arguments:
        points (array or str): point source
        dataSize (str): data size of the full image
        x,y,z (tuples or all): range specifications
        shift (bool): shift points to relative coordinates in the reduced image
    
    Returns:
        tuple: points reduced in range and optionally shifted to the range reduced origin
    """      
    

    if x is all and y is all and z is all:
        return points;

    istuple = isinstance(points, tuple);    
    (points, properties) = pointsToCoordinatesAndProperties(points);
    
    if points is None:
        if istuple:
            return (points, properties);
        else:
            return points;

    if not isinstance(points, numpy.ndarray):
        raise RuntimeError('pointsToRange: points not None or numpy array!');
        
        
    d = points.shape[1];
    
    if dataSize is all:
        dataSize = points.max(axis=0);
    elif isinstance(dataSize, basestring):
        dataSize = self.dataSize(dataSize);
    
    rr = [];
    if d > 0:
        rr.append(self.toDataRange(dataSize[0], r = x));
    if d > 1:
        rr.append(self.toDataRange(dataSize[1], r = y));
    if d > 2:
        rr.append(self.toDataRange(dataSize[2], r = z));
    if d > 3 or d < 1:
        raise RuntimeError('pointsToRange: dimension %d to big' % d);
    
    #ids = numpy.zeros(n, dtype = 'bool');
    if d > 0:
        ids = numpy.logical_and(points[:,0] >= rr[0][0], points[:,0] < rr[0][1]);
    if d > 1:
        ids = numpy.logical_and(numpy.logical_and(ids, points[:,1] >= rr[1][0]), points[:,1] < rr[1][1]);
    if d > 2:
        ids = numpy.logical_and(numpy.logical_and(ids, points[:,2] >= rr[2][0]), points[:,2] < rr[2][1]);
        
    points = points[ids, :];
        
    if shift:
        sh = [r[0] for r in rr];
        points = points - sh;
    
    if not properties is None:
        properties = properties[ids];
    
    if istuple:
        return (points, properties);
    else:
        return points;




def readPoints(source, **args):
    """Read a list of points from csv or vtk
    
    Arguments:
        source (str, array, tuple or None): the data source file
        **args: further arguments specific to point data format reader
    
    Returns:
        array or tuple or None: point data of source
    
    See Also:
        :func:`writePoints`
    """ 
    
    istuple = isinstance(source, tuple);

    if source is None:
        source = (None, None);
    elif isinstance(source, numpy.ndarray):
        source = (source, None);
    elif isinstance(source, basestring):
        source = (source, None);
    elif isinstance(source, tuple):
        if len(source) == 0:
            source = (None, None);
        elif len(source) == 1: 
            if source[0] is None:
                source = (None, None);
            elif isinstance(source[0], numpy.ndarray):
                source = (source[0], None);
            elif isinstance(source[0], basestring):
                source = pointsToCoordinatesAndPropertiesFileNames(source, **args);
            else:
                raise RuntimeError('readPoints: cannot infer format of the requested data/file.');       
        elif len(source) == 2:
            if not((source[0] is None or isinstance(source[0], basestring) or isinstance(source[0], numpy.ndarray)) and 
                   (source[1] is None or isinstance(source[1], basestring) or isinstance(source[0], numpy.ndarray))):
               raise RuntimeError('readPoints: cannot infer format of the requested data/file.');
        else:
            raise RuntimeError('readPoints: cannot infer format of the requested data/file.');
    else:
        raise RuntimeError('readPoints: cannot infer format of the requested data/file.'); 
           
    if source[0] is None:
        points = None;
    elif isinstance(source[0], numpy.ndarray):
        points = source[0];
    elif isinstance(source[0], basestring):
        mod = self.pointFileNameToModule(source[0]);
        points = mod.readPoints(source[0]);

    if source[1] is None:
        properties = None;
    elif isinstance(source[1], numpy.ndarray):
        properties = source[1];
    elif isinstance(source[1], basestring):
        mod = self.pointFileNameToModule(source[1]);
        properties = mod.readPoints(source[1]);
        
    if istuple:
        return self.pointsToRange((points, properties), **args);
    else:
        return self.pointsToRange(points, **args);


def writePoints(sink, points, **args):
    """Write a list of points to csv, vtk or ims files
    
    Arguments:
        sink (str or None): the destination for the point data
        points (array or tuple or None): the point data, optionally as (coordinates, properties) tuple
        **args: further arguments specific to point data format writer
    
    Returns:
        str or array or tuple or None: point data of source
    
    See Also:
        :func:`readPoints`
    """ 
    
    #todo: make clean independent of return of two results -> io.wrtiePoints -> take care of pairs: (points,intensities)
    istuple = isinstance(sink, tuple);    
    
    if sink is None:
        sink = (None, None);
    elif isinstance(sink, basestring):
        sink = (sink, None);
    elif isinstance(sink, tuple):
        if len(sink) == 0:
            sink = (None, None);
        elif len(sink) == 1:
            if sink[0] is None:
                sink = (None, None);
            elif isinstance(sink, basestring):
                sink = pointsToCoordinatesAndPropertiesFileNames(sink, **args);
            else:
                raise RuntimeWarning('sink not well defined!')
        elif len(sink) == 2:
            if not((sink[0] is None or isinstance(sink[0], basestring)) and (sink[1] is None or isinstance(sink[1], basestring))):
                raise RuntimeWarning('sink not well defined!')
        else:
            raise RuntimeWarning('sink not well defined!')
    else:
        raise RuntimeWarning('sink not well defined!')

    
    (points, properties) = pointsToCoordinatesAndProperties(points); 
    if sink[0] is None:
        retpoints = points;
    else:
        mod = self.pointFileNameToModule(sink[0]);
        retpoints = mod.writePoints(sink[0], points);
    
    if sink[1] is None:
        retproperties = properties;
    else:
        mod = self.pointFileNameToModule(sink[1]);
        retproperties = mod.writePoints(sink[1], properties);
        
    if istuple:
        return (retpoints, retproperties);
    else:
        return retpoints;
    



def writeTable(filename, table):
    """Writes a numpy array with column names to a csv file.
    
    Arguments:
        filename (str): filename to save table to
        table (annotated array): table to write to file
        
    Returns:
        str: file name
    """
    with open(filename,'w') as f:
        for sublist in table:
            f.write(', '.join([str(item) for item in sublist]));
            f.write('\n');
        f.close();

    return filename;

