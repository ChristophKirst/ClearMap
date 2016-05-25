# -*- coding: utf-8 -*-
"""
Interface to write csv files of cell coordinates / intensities

The module utilizes the csv file writer/reader from numpy.

Example:
    >>> import os, numpy
    >>> import ClearMap.IO.CSV as csv
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/ImageProcessing/points.txt');
    >>> points = numpy.random.rand(5,3);
    >>> csv.writePoints(filename, points);
    >>> points2 = csv.readPoints(filename);
    >>> print points2.shape
    (5, 3)
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import numpy

import ClearMap.IO as io;


def writePoints(filename, points, **args):
    """Write point data to csv file
    
    Arguments:
        filename (str): file name
        points (array): point data
    
    Returns:
        str: file name
    """
    
    numpy.savetxt(filename, points, delimiter=',', newline='\n', fmt='%.5e')
    return filename


def readPoints(filename, **args):
    """Read point data to csv file
    
    Arguments:
        filename (str): file name
        **args: arguments for :func:`~ClearMap.IO.pointsToRange`
    
    Returns:
        str: file name
    """
    
    points = numpy.loadtxt(filename, delimiter=',');
    return io.pointsToRange(points, **args);


def test():    
    """Test CSV module"""
    import os
    import ClearMap.IO.CSV as self
    reload(self)
    
    fn = os.path.split(self.__file__);
    fn = os.path.join(fn[0], '../Test/ImageProcessing/points.txt');
    
    points = numpy.random.rand(5,3);
    self.writePoints(fn, points);  
    print "Write points to " + fn;
    print "Points:"
    print points
    
    points2 = self.readPoints(fn);
    print "Read points: "
    print points2
    
    print "Difference: " + str(numpy.abs(points-points2).max())
    

if __name__ == "__main__":
    
    test();
    
