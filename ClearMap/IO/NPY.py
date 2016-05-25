# -*- coding: utf-8 -*-
"""
Interface to write binary files for point like data

The interface is based on the numpy library.

Example:
    >>> import os, numpy
    >>> import ClearMap.Settings as settings
    >>> import ClearMap.IO.NPY as npy
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/Data/NPY/points.npy');
    >>> points = npy.readPoints(filename);
    >>> print points.shape
    (5, 3)

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


import numpy

import ClearMap.IO as io;

def writePoints(filename, points, **args):
    numpy.save(filename, points)
    return filename


def readPoints(filename, **args):
    points = numpy.load(filename);
    return io.pointsToRange(points, **args);


def test():    
    """Test NPY module"""
    
    import os, numpy
    import ClearMap.IO.NPY as self
    reload(self)
    
    fn = os.path.split(self.__file__);
    fn = os.path.join(fn[0], '../Test/Data/NPY/points.npy');
    
    points = numpy.random.rand(5,3);
    self.writePoints(fn, points);  
    print "Wrote points to " + fn;
    print "Points:"
    print points
    
    points2 = self.readPoints(fn);
    print "Read points: "
    print points2
    
    print "Difference: " + str(numpy.abs(points-points2).max())
    

if __name__ == "__main__":
    
    test();
    
