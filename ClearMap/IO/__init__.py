# -*- coding: utf-8 -*-
"""This sub-package provides routines to read and write data

Two types of data files are discriminated:
    * `Image data`_
    * `Point data`_

The image data are stacks from microscopes obtained by volume imaging, or the results of analysis representing
the visualization of the detected objects for instance.

The point data are lists of cell coordinates or measured intensities for instance. 

Image data
---------- 

Images are represented internally as numpy arrays. ClearMap assumes images
in arrays are arranged as [x,y], [x,y,z] or [x,y,z,c] where x,y,z correspond to 
the x,y,z coordinates as when viewed in an image viewer such as ImageJ. 
The c coordinate is a possible color channel.

.. note:: Many image libraries read images as [y,x,z] or [y,x] arrays!

The ClearMap toolbox supports a range of (volumetric) image formats:

=============== ========================================================== ============================
Format          Descrition                                                 Module
=============== ========================================================== ============================
TIF             tif images and stacks                                      :mod:`~ClearMap.IO.TIF`
RAW / MHD       raw image files with optional mhd header file              :mod:`~ClearMap.IO.RAW`
NRRD            nearly raw raster data files                               :mod:`~ClearMap.IO.NRRD`
IMS             imaris image file                                          :mod:`~ClearMap.IO.Imaris`
reg exp         folder, file list or file pattern of a stack of 2d images  :mod:`~ClearMap.IO.FileList`
=============== ========================================================== ============================

.. note:: ClearMap can read the image data from a Bitplane’s Imaris, but can’t export image data as an Imaris file.

The image format is inferred automatically from the file name extension.

For example to read image data use :func:`~ClearMap.IO.IO.readData`:

    >>> import os
    >>> import ClearMap.IO as io
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath,'Test/Data/Tif/test.tif'); 
    >>> data = io.readData(filename);
    >>> print data.shape
    (20, 50, 10)

To write image data use :func:`~ClearMap.IO.IO.writeData`:

    >>> import os, numpy
    >>> import ClearMap.IO as io
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath,'Test/Data/Tif/test.tif'); 
    >>> data = numpy.random.rand(20,50,10);
    >>> data[5:15, 20:45, 2:9] = 0;
    >>> data = 20 * data;
    >>> data = data.astype('int32');
    >>> res = io.writeData(filename, data);
    >>> print io.dataSize(res);
    (20, 50, 10)
    
Generally, the IO module is designed to work with image sources which can be
either files or already loaded numpy arrays. This is important to enable flexible
parallel processing, without rewriting the data analysis routines. 

For example:

    >>> import numpy
    >>> import ClearMap.IO as io
    >>> data = numpy.random.rand(20,50,10);
    >>> res = io.writeData(None, data);
    >>> print res.shape;
    (20, 50, 10)

Range parameter can be passed in order to only load sub sets of image data,
useful when the images are very large. For example to load a sub-image:

    >>> import os, numpy
    >>> import ClearMap.IO as io
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath,'Test/Data/Tif/test.tif'); 
    >>> res = io.readData(filename, data, x = (0,3), y = (4,6), z = (1,4));
    >>> print res.shape;
    (3, 2, 3)


Point data
----------

ClearMap also supports several data formats for storing arrays of points, such
as cell center coordinates or intensities.

Points are assumed to be an array of coordinates where the first array index
is the point number and the second the spatial dimension, i.e. [i,d]
The spatial dimension can be extended with additional dimensions 
for intensity ,easires or other properties.

Points can also be given as tuples (coordinate arrray, property array).


ClearMap supports the following files formats for point like data:

========= ========================================================== =======================
Format    Description                                                Module
========= ========================================================== =======================
CSV       comma separated values in text file                        :mod:`~ClearMap.IO.CSV`
NPY       numpy binary file                                          :mod:`~ClearMap.IO.NPY`
VTK       vtk point data file                                        :mod:`~ClearMap.IO.VTK`
========= ========================================================== =======================

.. note:: ClearMap can write points data to a pre-existing Bitplane’s Imaris file, but can’t import the points from them.


The point file format is inferred automatically from the file name extension.

For example to read point data use :func:`~ClearMap.IO.IO.readPoints`:

    >>> import os
    >>> import ClearMap.IO as io
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/ImageProcessing/points.txt');
    >>> points = io.readPoints(filename);
    >>> print points.shape
    (5, 3)

and to write it use :func:`~ClearMap.IO.IO.writePoints`:

    >>> import os, numpy
    >>> import ClearMap.IO as io
    >>> import ClearMap.Settings as settings
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/ImageProcessing/points.txt');
    >>> points = numpy.random.rand(5,3);
    >>> io.writePoints(filename, points);


Summary
-------
    - All routines accessing data or data properties accept file name strings or numpy arrays or None
    - Numerical arrays represent data and point coordinates as [x,y,z] or [x,y] 
""" 
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

from ClearMap.IO.IO import * 


