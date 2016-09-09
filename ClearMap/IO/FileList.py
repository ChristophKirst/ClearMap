# -*- coding: utf-8 -*-
"""
Interface to read/write image stacks saved as a list of files

The filename is given as regular expression as described 
`here <https://docs.python.org/2/library/re.html>`_.

It is assumd that there is a single digit like regular expression in the file
name, i.e. ``\\d{4}`` indicates a placeholder for an integer with four digits using traling 0s
and ``\\d{}`` would jus asume an integer with variable size.

For example: ``/test\d{4}.tif`` or  ``/test\d{}.tif``
    
Examples:
    >>> import os, numpy
    >>> import ClearMap.Settings as settings
    >>> import ClearMap.IO.FileList as fl
    >>> filename = os.path.join(settings.ClearMapPath, 'Test/Data/FileList/test\d{4}.tif')  
    >>> data = numpy.random.rand(20,50,10);
    >>> data = data.astype('int32');
    >>> fl.writeData(filename, data);
    >>> img = fl.readData(filename);  
    >>> print img.shape
    (20, 50, 10)
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import numpy
import os
import re
import natsort

import ClearMap.IO as io


def readFileList(filename):
    """Returns list of files that match the regular expression
    
    Arguments:
        filename (str): file name as regular expression
    
    Returns:
        str, list: path of files, file names that match the regular expression
    """
    
    #get path        
    (fpath, fname) = os.path.split(filename)
    fnames = os.listdir(fpath);
    #fnames = [os.path.join(fpath, x) for x in fnames];
    
    searchRegex = re.compile(fname).search    
    fl = [ l for l in fnames for m in (searchRegex(l),) if m]  
    
    if fl == []:
        raise RuntimeError('no files found in ' + fpath + ' match ' + fname + ' !');
    
    #fl.sort();
    return fpath, natsort.natsorted(fl);
    

def splitFileExpression(filename, fileext = '.tif'):
    """Split the regular expression at the digit place holder

    Arguments:
        filename (str): file name as regular expression
        fileext (str or None): file extension to use if filename is a fileheader only

    Returns:
        tuple: file header, file extension, digit format
    """

    #digits with fixed width trailing zeros
    searchRegex = re.compile('.*\\\\d\{(?P<digit>\d)\}.*').search
    m = searchRegex(filename);

    if not m is None:
        digits = int(m.group('digit'));
        searchRegex = re.compile('.*(?P<replace>\\\\d\{\d\}).*').search
        m = searchRegex(filename);
        fs = filename.split(m.group('replace'));
        if not len(fs) == 2:
            raise RuntimeError('FileList: no file extension or more than a single placeholder for z indexing found!');
        fileheader = fs[0];
        fileext    = fs[1];

        digitfrmt = "%." + str(digits) + "d";

    else:
      #digits without trailing zeros \d* or
      searchRegex = re.compile('.*\\\\d\*.*').search
      m = searchRegex(filename);

      if not m is None:
        searchRegex = re.compile('.*(?P<replace>\\\\d\*).*').search
        m = searchRegex(filename);
        fs = filename.split(m.group('replace'));
        if not len(fs) == 2:
            raise RuntimeError('FileList: no file extension or more than a single placeholder for z indexing found!');
        fileheader = fs[0];
        fileext    = fs[1];

        digitfrmt = "%d";

      else:
        #digits without trailing zeros \d{} or
        searchRegex = re.compile('.*\\\\d\{\}.*').search
        m = searchRegex(filename);

        if not m is None:
          searchRegex = re.compile('.*(?P<replace>\\\\d\{\}).*').search
          m = searchRegex(filename);
          fs = filename.split(m.group('replace'));
          if not len(fs) == 2:
              raise RuntimeError('FileList: no file extension or more than a single placeholder for z indexing found!');
          fileheader = fs[0];
          fileext    = fs[1];

          digitfrmt = "%d";

        else: #fileheader is given
          digits = 4;
          fileheader = filename;
          #fileext    = '.tif';

          digitfrmt = "%." + str(digits) + "d";

    return (fileheader, fileext, digitfrmt);


def fileExpressionToFileName(filename, z):
    """Insert a number into the regular expression

    Arguments:
        filename (str): file name as regular expression
        z (int or str): z slice index or string to insert

    Returns:
        str: file name
    """

    (fileheader, fileext, digitfrmt) = splitFileExpression(filename);
    if isinstance(z, str):
       return fileheader + z + fileext;
    else:
      return fileheader + (digitfrmt % z) + fileext;


def dataSize(filename, **args):
    """Returns size of data stored as a file list
    
    Arguments:
        filename (str): file name as regular expression
        x,y,z (tuple): data range specifications
    
    Returns:
        tuple: data size
    """
    
    fp, fl = readFileList(filename);
    nz = len(fl);
    
    d2 = io.dataSize(os.path.join(fp, fl[0]));
    if not len(d2) == 2:
        raise RuntimeError("FileList: importing multiple files of dim %d not supported!" % len(d2));
    
    dims = d2 + (nz,);
    return io.dataSizeFromDataRange(dims, **args);
   
   
def dataZSize(filename, z = all, **args):
    """Returns size of data stored as a file list
    
    Arguments:
        filename (str): file name as regular expression
        z (tuple): z data range specification
    
    Returns:
        int: z data size
    """
    
    fp, fl = readFileList(filename);
    nz = len(fl);
    return io.toDataSize(nz, r = z);



def readDataFiles(filename, x = all, y = all, z = all, **args):
    """Read data from individual images assuming they are the z slices

    Arguments:
        filename (str): file name as regular expression
        x,y,z (tuple): data range specifications
    
    Returns:
        array: image data
    """   
    
    fpath, fl = readFileList(filename);
    nz = len(fl);
    
    #read first image to get data size and type
    rz = io.toDataRange(nz, r = z);
    sz = io.toDataSize(nz, r = z);
    fn = os.path.join(fpath, fl[rz[0]]); 
    img = io.readData(fn, x = x, y = y);
    nxy = img.shape;
    data = numpy.zeros(nxy + (sz,), dtype = img.dtype);
    data[:,:,0] = img;


    for i in range(rz[0]+1, rz[1]):
        fn = os.path.join(fpath, fl[i]);    
        data[:,:,i-rz[0]] = io.readData(fn, x = x, y = y);
    
    return data;





     
def readData(filename, **args):
    """Read image stack from single or multiple images
    
    Arguments:
        filename (str): file name as regular expression
        x,y,z (tuple): data range specifications
    
    Returns:
        array: image data
    """
    
    if os.path.exists(filename):
         return io.readData(filename, **args);
    else:
         return readDataFiles(filename, **args);



def writeData(filename, data, startIndex = 0):
    """Write image stack to single or multiple image files
    
    Arguments:
        filename (str): file name as regular expression
        data (array): image data
        startIndex (int): index of first z-slice
    
    Returns:
        str: file name as regular expression
    """
    
    #create directory if not exsits
    io.createDirectory(filename); 

    #check for the \d{xx} part of the regular expression -> if not assume file header    
    (fileheader, fileext, digitfrmt) = splitFileExpression(filename);

    d = len(data.shape);
    if d == 2:
        fname = fileheader + (digitfrmt % startIndex) + fileext;
        io.writeData(fname, data);
        return fname;
    else:
        nz = data.shape[2];
        for i in range(nz):
            fname = fileheader + (digitfrmt % (i + startIndex)) + fileext;
            io.writeData(fname, data[:,:,i]);
        return filename;


def copyData(source, sink):
    """Copy a data file from source to sink when for entire list of files
    
    Arguments:
        source (str): file name pattern of source
        sink (str): file name pattern of sink
    
    Returns:
        str: file name patttern of the copy
    """ 
    
    (fileheader, fileext, digitfrmt) = splitFileExpression(sink);
    
    fp, fl = readFileList(source);
    
    for i in range(len(fl)):
        io.copyFile(os.path.join(fp, fl[i]), fileheader + (digitfrmt % i) + fileext);
    
    return sink


def test():    
    """Test FileList module"""  
    import ClearMap.IO.FileList as self
    reload(self)
    
    from iDISCO.Parameter import iDISCOPath
    import os
    import numpy

    basedir = iDISCOPath();
    fn = os.path.join(basedir,'Test/Data/FileList/test\d{4}.tif')  

    data = numpy.random.rand(20,50,10);
    data[5:15, 20:45, 2:9] = 0;
    data = 20 * data;
    data = data.astype('int32');
    
    print "writing raw image to: " + fn;    
    self.writeData(fn, data);

    print "Loading raw image from: " + fn;
    img = self.readData(fn);  
    print "Image size: " + str(img.shape)
    
    diff = img - data;
    print (diff.max(), diff.min())

    
    fn = os.path.join(basedir,'Test/Data/OME/16-17-27_0_8X-s3-20HF_UltraII_C00_xyz-Table Z\d{4}.ome.tif')        
    
    fp, fl = self.readFileList(fn);
    print "Found " + str(len(fl)) + " images!"    
    
    #dataSize
    print "dataSize  is %s" % str(self.dataSize(fn))
    print "dataZSize is %s" % str(self.dataZSize(fn))
    
    print "dataSize  is %s" % str(self.dataSize(fn, x = (10,20)))
    print "dataZSize is %s" % str(self.dataZSize(fn))
    
    
    img = self.readData(fn, z = (17,all));  
    print "Image size: " + str(img.shape)    
    
    import iDISCO.Visualization.Plot as plt
    plt.plotTiling(img)
        

if __name__ == "__main__":
    
    test();
    
