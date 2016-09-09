# -*- coding: utf-8 -*-
"""
Inteface to Illastik for pixel classification / object detection

This module allows to integrate ilastik into the *ClearMap* pipeline.

To use ilastik within *ClearMap* use the followng steps:

  * start ilastik interface (e.g. manually or using 
    :func:`~ClearMap.Imageprocessing.Ilastik.runIlastik)
    
  * train e.g. a pixel classifier in ilastik
  
  * save the ilastik project under some file name <name>.ilp
  
  * pass this ilastik project file name to e.g. 
    :func:`~ClearMap.Imageprocessing.Ilastik.classifyPixel
  

Note:
    Note that ilastik classification works in parallel, thus it is advised to 
    process the data sequentially, see 
    :func:`~ClearMap.Imageprocessing.StackProcessing.sequentiallyProcessStack`  

References:
    * `Ilastik <http://ilastik.org/>`_
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import os
import tempfile
import shutil
import h5py
import numpy

import ClearMap.Settings as settings
import ClearMap.IO as io
import ClearMap.IO.FileList as filelist


##############################################################################
# Initialization and Enviroment Settings
##############################################################################

IlastikBinary = None;
"""str: the ilastik run script

Notes:
    - setup in :func:`initializeIlastik`
"""
    
Initialized = False;
"""bool: True if the ilastik binarys and paths are setup

Notes:
    - setup in :func:`initializeIlastik`
"""

    
def printSettings():
    """Prints the current ilastik configuration
    
    See also:
        :const:`IlastikBinary`, :const:`Initialized`
    """
    
    global IlastikBinary, Initialized
    
    if Initialized:
        print "IlastikBinary     = %s" % IlastikBinary;
    else:
        print "Ilastik not initialized";


def initialize(path = None):
    """Initialize all paths and binaries of ilastik

    Arguments:
        path (str or None): path to ilastik root directory, if None 
        :const:`ClearMap.Settings.IlastikPath` is used.
        
    See also:
        :const:`IlastikBinary`, :const:`Initialized`
    """
    
    global IlastikBinary, Initialized
    
    if path is None:
        path = settings.IlastikPath;
        
    if path is None:
        path = '.';
    
    #search for elastix binary
    ilastikbin = os.path.join(path, 'run_ilastik.sh');
    if os.path.exists(ilastikbin):
        print "Ilastik sucessfully initialized from path: %s" % path;
        IlastikBinary = ilastikbin;
        Initialized = True;
        return path;
    else:
        print "Cannot find ilastik binary %s, set path in Settings.py accordingly!" % ilastikbin;
        IlastikBinary = None;
        Initialized = False;
        return None;

initialize();


def isInitialized():
    """Checks if ilastik is initialized
    
    Returns:
        bool: True if ilastik paths are set.
    """
    
    global Initialized;
    
    if not Initialized:
        raise RuntimeError("Ilastik not initialized: run initializeIlastik(path) with proper path to ilastik first");
    #print ElastixSettings.ElastixBinary;

    return True;


def start():
  """Start Ilastik software to train a classifier"""
  
  global IlastikBinary;
  isInitialized();  
  return os.system(IlastikBinary);


def run(args = ""):
    """Run Ilastik in headless mode
    
    Arguments:
      args (str): string of arguments to pass to the headless running command
      
    Note:
      run runIlastik() to test headles mode is operative!
    """

    global IlastikBinary;    
    isInitialized();
        
    #if resultDirectory == None:
    #    resultDirectory = tempfile.gettempdir();
    #
    #if not os.path.exists(resultDirectory):
    #    os.mkdir(resultDirectory);
    
    cmd = IlastikBinary + ' --headless ' + args;
    print 'Ilastik: running: %s' % cmd;
    
    res = os.system(cmd);
    
    if res != 0:
        raise RuntimeError('runIlastik: failed executing: ' + cmd);
    
    return cmd


def isValidInputFileName(filename):
  """Checks if the file is a valid format for use with Ilastik input
  
  Arguments:
    filename (str): image file name or expression
  
  Returns:
    bool: True if the image file can be read by Ilastik
  """
  
  validExtensions  = ['bmp', 'exr', 'gif', 'jpg', 'jpeg', 'tif', 'tiff', 'ras',
                      'png', 'pbm', 'pgm', 'ppm', 'pnm', 'hdr', 'xv', 'npy'];
  
  return io.fileExtension(filename) in validExtensions;

 
def isValidOutputFileName(filename):
  """Checks if the file is a valid format for use with Ilastik ouput
  
  Arguments:
    filename (str): image file name or expression
  
  Returns:
    bool: True if the image file can be written by Ilastik
  """
    
  if io.isFileExpression(filename):
    validExtensions  = ['bmp', 'gif', 'hdr', 'jpg', 'jpeg', 'pbm', 'pgm', 'png', 'pnm', 'ppm', 'ras', 'tif', 'tiff', 'xv'];
    return io.fileExtension(filename) in validExtensions;
  else:
    validExtensions  = ['bmp', 'gif', 'hdr', 'jpg', 'jpeg', 'pbm', 'pgm', 'png', 'pnm', 'ppm', 'ras', 'tif', 'tiff', 'xv', 'h5', 'npy'];
    return io.fileExtension(filename) in validExtensions;


def fileNameToIlastikInput(filename):
  """Converts *ClearMap* file name to a string for use with Ilastik input
  
  Arguments:
    filename (str): image file name or expression
  
  Returns:
    str: Ilastik conform file name
    
  Note:
    file expressions in *ClearMap* are regular expressions but shell expressions in Ilastik.
  """

  if not isValidInputFileName(filename):
    raise RuntimeError('Ilastik: file format not compatibel with Ilastik');
  
  if io.isFileExpression(filename):
    return '"' + filelist.fileExpressionToFileName(filename, '*') + '"';
  else:
    return '"' + filename + '"';
  
  
def fileNameToIlastikOuput(filename):
  """Converts *ClearMap* file name to an argument string for use with Ilastik headless mode
  
  Arguments:
    filename (str): image file name or expression
  
  Returns:
    str: Ilastik headless ouput specifications
    
  Note:
    The output is formated accroding to the Ilastik pixel calssification output specifications
  """

  if not isValidOutputFileName(filename):
    raise RuntimeError('Ilastik: file format not compatibel with Ilastik output');
  
  if io.isFileExpression(filename):
    o = '--output_format="' + io.fileExtension(filename) + ' sequence" '+ \
        '--output_filename_format="' + filelist.fileExpressionToFileName(filename, '{slice_index}') + '"';
    return o;
    
  else: # single file
    extensionToOuput  = {'bmp' : 'bmp', 'gif' : 'gif', 'hdr' : 'hrd', 
                         'jpg' : 'jpg', 'jpeg': 'jpeg','pbm' : 'pbm', 
                         'pgm' : 'pgm', 'png' : 'png', 'pnm' : 'pnm', 'ppm' : 'ppm', 
                         'ras' : 'ras', 'tif' : 'tif', 'tiff': 'tiff','xv'  : 'xv',
                         'h5'  : 'hdf5' , 'npy' : 'numpy'};
    ext = extensionToOuput[io.fileExtension(filename)];
    o = '--output_format="' + ext +'" ' + \
        '--output_filename_format="' + filename + '"';
    return o;


def readResultH5(filename):
  """Reads the ilastik result from an hdf5 file
  
  Arguments:
    filename (str): h5 file name 
  
  Returns:
    array: the classification result
  
  Note:
    For large files might be good to consider a memmap return object"""
    
  f = h5py.File(filename, "r");
  
  dsname = "/exported_data";
  dset = f.get(dsname);
  #dsize = dset.shape;
  
  data = numpy.array(dset);
  data = data.transpose((2,1,0,3)); # ilastik stores h5py as x,y,z,c 
      
  f.close();
    
  return data;


def classifyPixel(project, source, sink = None, processingDirectory = None, cleanup = True):
  """Run pixel classification in headless moded using a trained project file
  
  Arguments:
    project (str): ilastik project .ilp file
    source (str or array): image source
    sink (str or array or None): image sink
  
  Returns:
    str or array: classified image sink
  """
  
  #generate source image file if source is array
  if isinstance(source, str):
    inpfile = source;
  else:
    #generate temporary file
    if processingDirectory is None:
        processingDirectory = tempfile.mkdtemp();
    
    inpfile = os.path.join(processingDirectory, 'ilastik.npy')
    io.writePoints(inpfile, source.transpose((2,1,0)));
  
  if isinstance(sink, str):
    outfile = sink;
  else:
    #outdir  = tempfile.mkdtemp();
    #outfile = os.path.join(outdir, 'result\d*.tif');
    outfile = tempfile.mktemp('.h5');
  
  ilinp = fileNameToIlastikInput(inpfile);
  ilout = fileNameToIlastikOuput(outfile);

  args = '--project="' + project + '" ' + ilout + ' ' + ilinp;
  run(args);
  
  #clean up 
  if cleanup and processingDirectory is not None:
    shutil.rmtree(processingDirectory);
  
  if not isinstance(sink, str):
    sink = readResultH5(outfile);
    if cleanup:
      os.remove(outfile);
  
  return sink;


def test():
  import os;
  import ClearMap.IO as io
  import ClearMap.Settings as settings
  import ClearMap.ImageProcessing.Ilastik as il;
  reload(il);
  
  ilp = os.path.join(settings.ClearMapPath, 'Test/Ilastik/Test.ilp')
  src = os.path.join(settings.ClearMapPath, 'Test/Data/ImageAnalysis/cfos-substack.tif');
  #out = os.path.join(settings.ClearMapPath, 'Test/Data/Ilastik/image.npy');
  out = None;
  #out = os.path.join(settings.ClearMapPath, 'Test/Data/Ilastik/result\d*.tif');
  
  cls = il.classifyPixel(ilp, src, out);
  print io.dataSize(src)
  print cls.shape
  io.writeData('/home/ckirst/result.raw', cls);