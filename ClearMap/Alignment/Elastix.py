# -*- coding: utf-8 -*-
"""
Interface to Elastix for alignment of volumetric data

The elastix documentation can be found `here <http://elastix.isi.uu.nl/>`_.

In essence, a transformation :math:`T(x)` is sought so that for a fixed image 
:math:`F(x)` and a moving image :math:`M(x)`:

.. math::
    F(x) = M(T(x))

Once the map :math:`T` is estimated via elastix, transformix maps an image
:math:`I(x)` from the moving image frame to the fixed image frame, i.e.:

.. math::
    I(x) \\rightarrow I(T(x)) 

To register an image onto a reference image, the fixed image is typically 
choosed to be the image to be registered, while the moving image is the 
reference image. In this way an object identified in the data at position x
is mapped via transformix as:

.. math::
    x \\rightarrow T(x)
    



Summary
-------
    * elastix finds a transformation :math:`T: \\mathrm{fixed image} \\rightarrow \\mathrm{moving image}`
    * the fixed image is image to be registered
    * the moving image is typically the reference image
    * the result folder may contain an image (mhd file) that is :math:`T^{-1}(\\mathrm{moving})`,
      i.e. has the size of the fixed image
    * transformix applied to data gives :math:`T^{-1}(\\mathrm{data})` !
    * transformix applied to points gives :math:`T(\\mathrm{points})` !
    * point arrays are assumed to be in (x,y,z) coordinates consistent with (x,y,z) array represenation of images in ClearMap
    
Main routines are: :func:`alignData`, :func:`transformData` and :func:`transformPoints`.
    
See Also:
    `Elastix documentation <http://elastix.isi.uu.nl/>`_
    :mod:`~ClearMap.Alignment.Resampling`
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


import os
import tempfile
import shutil
import numpy
import re

import ClearMap.Settings as settings
import ClearMap.IO as io

##############################################################################
### Initialization and Enviroment Settings
##############################################################################

ElastixBinary = None;
"""str: the elastix executable

Notes:
    - setup in :func:`initializeElastix`
"""

ElastixLib = None;
"""str: path to the elastix library

Notes:
    - setup in :func:`initializeElastix`
"""

TransformixBinary = None;
"""str: the transformix executable

Notes:
    - setup in :func:`initializeElastix`
"""
    
Initialized = False;
"""bool: True if the elastixs binarys and paths are setup

Notes:
    - setup in :func:`initializeElastix`
"""

    
def printSettings():
    """Prints the current elastix configuration
    
    See also:
        :const:`ElastixBinary`, :const:`ElastixLib`, :const:`TransformixBinary`, :const:`Initialized`
    """
    
    global ElastixBinary, ElastixLib, TransformixBinary, Initialized
    
    if Initialized:
        print "ElastixBinary     = %s" % ElastixBinary;
        print "ElastixLib        = %s" % ElastixLib;
        print "TransformixBinary = %s" % TransformixBinary;
    else:
        print "Elastix not initialized";


def setElastixLibraryPath(path = None): 
    """Add elastix library path to the LD_LIBRARY_PATH variable in linux
    
    Arguments:
        path (str or None): path to elastix root directory if None :const:`ClearMap.Settings.ElastixPath` is used.
    """
     
    if path is None:
        path = settings.ElastixPath;
    
    if os.environ.has_key('LD_LIBRARY_PATH'):
        lp = os.environ['LD_LIBRARY_PATH'];
        if not path in lp.split(':'):
            os.environ['LD_LIBRARY_PATH'] = lp + ':' + path;
    else:
        os.environ['LD_LIBRARY_PATH'] = path


def initializeElastix(path = None):
    """Initialize all paths and binaries of elastix

    Arguments:
        path (str or None): path to elastix root directory, if None 
        :const:`ClearMap.Settings.ElastixPath` is used.
        
    See also:
        :const:`ElastixBinary`, :const:`ElastixLib`, :const:`TransformixBinary`,
        :const:`Initialized`, :func:`setElastixLibraryPath`
    """
    
    global ElastixBinary, ElastixLib, TransformixBinary, Initialized
    
    if path is None:
        path = settings.ElastixPath;
    
    #search for elastix binary
    elastixbin = os.path.join(path, 'bin/elastix');
    if os.path.exists(elastixbin):
        ElastixBinary = elastixbin;
    else:
        raise RuntimeError("Cannot find elastix binary %s, set path in Settings.py accordingly!" % elastixbin);
    
    #search for transformix binarx
    transformixbin = os.path.join(path, 'bin/transformix');
    if os.path.exists(transformixbin):
        TransformixBinary = transformixbin;
    else:
        raise RuntimeError("Cannot find transformix binary %s set path in Settings.py accordingly!" % transformixbin);
    
    #search for elastix libs
    elastixlib = os.path.join(path, 'lib');
    if os.path.exists(elastixlib):
        ElastixLib = elastixlib;
    else:
        raise RuntimeError("Cannot find elastix libs in %s  set path in Settings.py accordingly!" % elastixlib);
    
    #set path
    setElastixLibraryPath(elastixlib);
        
    Initialized = True;
    
    print "Elastix sucessfully initialized from path: %s" % path;
    
    return path;



initializeElastix();


def checkElastixInitialized():
    """Checks if elastix is initialized
    
    Returns:
        bool: True if elastix paths are set.
    """
    
    global Initialized;
    
    if not Initialized:
        raise RuntimeError("Elastix not initialized: run initializeElastix(path) with proper path to elastix first");
    #print ElastixSettings.ElastixBinary;

    return True;



##############################################################################
### Basic interface routines
##############################################################################

def getTransformParameterFile(resultdir):
    """Finds and returns the transformation parameter file generated by elastix
    
    Notes:
        In case of multiple transformation parameter files the top level file is returned     
    
    Arguments:
        resultdir (str): path to directory of elastix results
        
    Returns:
        str: file name of the first transformation parameter file 
    """    
    
    files = os.listdir(resultdir);
    files = [x for x in files if re.match('TransformParameters.\d.txt', x)];
    files.sort();
    
    if files == []:
        raise RuntimeError('Cannot find a valid transformation file in ' + resultdir);
    
    return os.path.join(resultdir, files[-1])


def setPathTransformParameterFiles(resultdir):
    """Replaces relative with abolsute path in the parameter files in the result directory

    Notes:
        When elastix is not run in the directory of the transformation files
        the aboslute path needs to be given in each transformation file 
        to point to the subsequent transformation files. This is done via this 
        routine
       
    Arguments:
        resultdir (str): path to directory of elastix results
    """        

    #print resultdir 
    files = os.listdir(resultdir);
    files = [x for x in files if re.match('TransformParameters.\d.txt', x)];
    files.sort();
    
    if files == []:
        raise RuntimeError('Cannot find a valid transformation file in ' + resultdir);
    
    rec = re.compile("\(InitialTransformParametersFileName \"(?P<parname>.*)\"\)");
    
    for f in files:
        fh, tmpfn = tempfile.mkstemp();
        ff = os.path.join(resultdir, f);
        #print ff        
        
        with open(tmpfn, 'w') as newfile:
            with open(ff) as parfile:
                for line in parfile:
                    #print line
                    m = rec.match(line);
                    if m != None:
                        pn = m.group('parname');
                        if pn != 'NoInitialTransform':
                            pathn, filen = os.path.split(pn);
                            filen = os.path.join(resultdir, filen);
                            newfile.write(line.replace(pn, filen));
                        else:
                            newfile.write(line);
                    else:
                        newfile.write(line);
                            
        os.close(fh);
        os.remove(ff);
        shutil.move(tmpfn, ff);


def parseElastixOutputPoints(filename, indices = True):
    """Parses the output points from the output file of transformix
    
    Arguments:
        filename (str): file name of the transformix output file
        indices (bool): if True return pixel indices otherwise float coordinates
        
    Returns:
        points (array): the transformed coordinates     
    """
    
    with open(filename) as f:
        lines = f.readlines()
        f.close();
    
    np = len(lines);
    
    if np == 0:
        return numpy.zeros((0,3));
    
    points = numpy.zeros((np, 3));
    k = 0;
    for line in lines:
        ls = line.split();
        if indices:
            for i in range(0,3):
                points[k,i] = float(ls[i+22]);
        else:
            for i in range(0,3):
                points[k,i] = float(ls[i+30]);
        
        k += 1;
    
    return points;
          
         
def getTransformFileSizeAndSpacing(transformfile):
    """Parse the image size and spacing from a transformation parameter file

    Arguments:
        transformfile (str): File name of the transformix parameter file.
        
    Returns:
        (float, float): the image size and spacing
    """
    
    resi = re.compile("\(Size (?P<size>.*)\)");
    resp = re.compile("\(Spacing (?P<spacing>.*)\)");
    
    si = None;
    sp = None;
    with open(transformfile) as parfile:
        for line in parfile:
            #print line;
            m = resi.match(line)
            if m != None:
                pn = m.group('size');
                si = pn.split();
                #print si
                
            m = resp.match(line);
            if m != None:
                pn = m.group('spacing');
                sp = pn.split();
                #print sp 
    
        parfile.close();
    
    si = [float(x) for x in si];
    sp = [float(x) for x in sp];
    
    return si, sp


def getResultDataFile(resultdir):
    """Returns the mhd result file in a result directory
    
    Arguments:
        resultdir (str): Path to elastix result directory.
        
    Returns:
        str: The mhd file in the result directory.
    
    """
    
    files = os.listdir(resultdir);
    files = [x for x in files if re.match('.*.mhd', x)];
    files.sort();
    
    if files == []:
        raise RuntimeError('Cannot find a valid result data file in ' + resultdir);
    
    return os.path.join(resultdir, files[0])


    
def setTransformFileSizeAndSpacing(transformfile, size, spacing):
    """Replaces size and scale in the transformation parameter file
    
    Arguments:
        transformfile (str): transformation parameter file
        size (tuple): the new image size
        spacing (tuplr): the new image spacing 
    """
    
    resi = re.compile("\(Size (?P<size>.*)\)");
    resp = re.compile("\(Spacing (?P<spacing>.*)\)");
    
    fh, tmpfn = tempfile.mkstemp();
    
    si = [int(x) for x in size];
    
    with open(transformfile) as parfile:        
        with open(tmpfn, 'w') as newfile:
            for line in parfile:
                #print line
                
                m = resi.match(line)
                if m != None:
                    newfile.write("(Size %d %d %d)" % si);
                else:
                    m = resp.match(line)
                    if m != None:
                        newfile.write("(Spacing %d %d %d)" % spacing);
                    else:
                        newfile.write(line);
            
            newfile.close();               
            parfile.close();
            
            os.remove(transformfile);
            shutil.move(tmpfn, transformfile);
        


def rescaleSizeAndSpacing(size, spacing, scale):
    """Rescales the size and spacing
    
    Arguments:
        size (tuple): image size
        spacing (tuple): image spacing
        scale (tuple): the scale factor 
    
    Returns:
        (tuple, tuple): new size and spacing
    """   

    si = [int(x * scale) for x in size];
    sp = spacing / scale;
    
    return si, sp



##############################################################################
### Elastix Runs
##############################################################################

def alignData(fixedImage, movingImage, affineParameterFile, bSplineParameterFile = None, resultDirectory = None):
    """Align images using elastix, estimates a transformation :math:`T:` fixed image :math:`\\rightarrow` moving image.
    
    Arguments:
        fixedImage (str): image source of the fixed image (typically the reference image)
        movingImage (str): image source of the moving image (typically the image to be registered)
        affineParameterFile (str or None): elastix parameter file for the primary affine transformation
        bSplineParameterFile (str or None): elastix parameter file for the secondary non-linear transformation
        resultDirectory (str or None): elastic result directory
        
    Returns:
        str: path to elastix result directory
    """
    
    checkElastixInitialized();
    global ElastixBinary;
    
    if resultDirectory == None:
        resultDirectory = tempfile.gettempdir();
    
    if not os.path.exists(resultDirectory):
        os.mkdir(resultDirectory);
    
    
    if bSplineParameterFile is None:
        cmd = ElastixBinary + ' -threads 16 -m ' + movingImage + ' -f ' + fixedImage + ' -p ' + affineParameterFile + ' -out ' + resultDirectory;
    elif affineParameterFile is None:
        cmd = ElastixBinary + ' -threads 16 -m ' + movingImage + ' -f ' + fixedImage + ' -p ' + bSplineParameterFile + ' -out ' + resultDirectory;
    else:
        cmd = ElastixBinary + ' -threads 16 -m ' + movingImage + ' -f ' + fixedImage + ' -p ' + affineParameterFile + ' -p ' + bSplineParameterFile + ' -out ' + resultDirectory;
        #$ELASTIX -threads 16 -m $MOVINGIMAGE -f $FIXEDIMAGE -fMask $FIXEDIMAGE_MASK -p  $AFFINEPARFILE -p $BSPLINEPARFILE -out $ELASTIX_OUTPUT_DIR
    
    res = os.system(cmd);
    
    if res != 0:
        raise RuntimeError('alignData: failed executing: ' + cmd);
    
    return resultDirectory


def transformData(source, sink = [], transformParameterFile = None, transformDirectory = None, resultDirectory = None):
    """Transform a raw data set to reference using the elastix alignment results
    
    If the map determined by elastix is 
    :math:`T \\mathrm{fixed} \\rightarrow \\mathrm{moving}`, 
    transformix on data works as :math:`T^{-1}(\\mathrm{data})`.
        
    Arguments:
        source (str or array): image source to be transformed
        sink (str, [] or None): image sink to save transformed image to. if [] return the default name of the data file generated by transformix.
        transformParameterFile (str or None): parameter file for the primary transformation, if None, the file is determined from the transformDirectory.
        transformDirectory (str or None): result directory of elastix alignment, if None the transformParameterFile has to be given.
        resultDirectory (str or None): the directorty for the transformix results
        
    Returns:
        array or str: array or file name of the transformed data
    """
    
    global TransformixBinary;    
    
    if isinstance(source, numpy.ndarray):
        imgname = os.path.join(tempfile.gettempdir(), 'elastix_input.tif');
        io.writeData(source, imgname);
    elif isinstance(source, basestring):
        if io.dataFileNameToType(source) == "TIF":
            imgname = source;
        else:
            imgname = os.path.join(tempfile.gettempdir(), 'elastix_input.tif');
            io.transformData(source, imgname);
    else:
        raise RuntimeError('transformData: source not a string or array');

    if resultDirectory == None:
        resultdirname = os.path.join(tempfile.tempdir, 'elastix_output');
    else:
        resultdirname = resultDirectory;
        
    if not os.path.exists(resultdirname):
        os.makedirs(resultdirname);
        
    
    if transformParameterFile == None:
        if transformDirectory == None:
            raise RuntimeError('neither alignment directory and transformation parameter file specified!'); 
        transformparameterdir = transformDirectory
        transformParameterFile = getTransformParameterFile(transformparameterdir);
    else:
        transformparameterdir = os.path.split(transformParameterFile);
        transformparameterdir = transformparameterdir[0];
    
    #transform
    #make path in parameterfiles absolute
    setPathTransformParameterFiles(transformparameterdir);
   
    #transformix -in inputImage.ext -out outputDirectory -tp TransformParameters.txt
    cmd = TransformixBinary + ' -in ' + imgname + ' -out ' + resultdirname + ' -tp ' + transformParameterFile;
    
    res = os.system(cmd);
    
    if res != 0:
        raise RuntimeError('transformData: failed executing: ' + cmd);
    
    
    if not isinstance(source, basestring):
        os.remove(imgname);

    if sink == []:
        return getResultDataFile(resultdirname);
    elif sink is None:
        resultfile = getResultDataFile(resultdirname);
        return io.readData(resultfile);
    elif isinstance(sink, basestring):
        resultfile = getResultDataFile(resultdirname);
        return io.convertData(resultfile, sink);
    else:
        raise RuntimeError('transformData: sink not valid!');


def deformationField(sink = [], transformParameterFile = None, transformDirectory = None, resultDirectory = None):
    """Create the deformation field T(x) - x
    
    The map determined by elastix is 
    :math:`T \\mathrm{fixed} \\rightarrow \\mathrm{moving}`
        
    Arguments:
        sink (str, [] or None): image sink to save the transformation field; if [] return the default name of the data file generated by transformix.
        transformParameterFile (str or None): parameter file for the primary transformation, if None, the file is determined from the transformDirectory.
        transformDirectory (str or None): result directory of elastix alignment, if None the transformParameterFile has to be given.
        resultDirectory (str or None): the directorty for the transformix results
        
    Returns:
        array or str: array or file name of the transformed data
    """
    
    global TransformixBinary;    
    
    if resultDirectory == None:
        resultdirname = os.path.join(tempfile.tempdir, 'elastix_output');
    else:
        resultdirname = resultDirectory;
        
    if not os.path.exists(resultdirname):
        os.makedirs(resultdirname);
        
    if transformParameterFile == None:
        if transformDirectory == None:
            raise RuntimeError('neither alignment directory and transformation parameter file specified!'); 
        transformparameterdir = transformDirectory
        transformParameterFile = getTransformParameterFile(transformparameterdir);
    else:
        transformparameterdir = os.path.split(transformParameterFile);
        transformparameterdir = transformparameterdir[0];
    
    #transform
    #make path in parameterfiles absolute
    setPathTransformParameterFiles(transformparameterdir);
   
    #transformix -in inputImage.ext -out outputDirectory -tp TransformParameters.txt
    cmd = TransformixBinary + ' -def all -out ' + resultdirname + ' -tp ' + transformParameterFile;
    
    res = os.system(cmd);
    
    if res != 0:
        raise RuntimeError('deformationField: failed executing: ' + cmd);
    
    
    if sink == []:
        return getResultDataFile(resultdirname);
    elif sink is None:
        resultfile = getResultDataFile(resultdirname);
        data = io.readData(resultfile);
        if resultDirectory is None:
            shutil.rmtree(resultdirname);
        return data;
    elif isinstance(sink, basestring):
        resultfile = getResultDataFile(resultdirname);
        data = io.convertData(resultfile, sink);
        if resultDirectory is None:
            shutil.rmtree(resultdirname);
        return data;
    else:
        raise RuntimeError('deformationField: sink not valid!');


def deformationDistance(deformationField, sink = None, scale = None):
    """Compute the distance field from a deformation vector field
    
    Arguments:
        deformationField (str or array): source of the deformation field determined by :func:`deformationField`
        sink (str or None): image sink to save the deformation field to
        scale (tuple or None): scale factor for each dimension, if None = (1,1,1)
        
    Returns:
        array or str: array or file name of the transformed data
    """
    
    deformationField = io.readData(deformationField);
    
    df = numpy.square(deformationField);
    if not scale is None:
        for i in range(3):
            df[:,:,:,i] = df[:,:,:,i] * (scale[i] * scale[i]);
            
    return io.writeData(sink, numpy.sqrt(numpy.sum(df, axis = 3)));
    

def writePoints(filename, points, indices = True):
    """Write points as elastix/transformix point file
    
    Arguments:
        filename (str): file name of the elastix point file.
        points (array or str): source of the points.
        indices (bool): write as pixel indices or physical coordiantes
    
    Returns:
        str : file name of the elastix point file
    """

    points = io.readPoints(points);
    #points = points[:,[1,0,2]]; # points in ClearMap (y,x,z) -> permute to (x,y,z)

  
    with open(filename, 'w') as pointfile:
        if indices:
            pointfile.write('index\n')
        else:
            pointfile.write('point\n')
    
        pointfile.write(str(points.shape[0]) + '\n');
        numpy.savetxt(pointfile, points, delimiter = ' ', newline = '\n', fmt = '%.5e')
        pointfile.close();
    
    return filename;



def transformPoints(source, sink = None, transformParameterFile = None, transformDirectory = None, indices = True, resultDirectory = None, tmpFile = None):
    """Transform coordinates math:`x` via elastix estimated transformation to :math:`T(x)`

    Note the transformation is from the fixed image coorindates to the moving image coordiantes.
    
    Arguments:
        source (str): source of the points
        sink (str or None): sink for transformed points
        transformParameterFile (str or None): parameter file for the primary transformation, if None, the file is determined from the transformDirectory.
        transformDirectory (str or None): result directory of elastix alignment, if None the transformParameterFile has to be given.
        indices (bool): if True use points as pixel coordinates otherwise spatial coordinates.
        resultDirectory (str or None): elastic result directory
        tmpFile (str or None): file name for the elastix point file.
        
    Returns:
        array or str: array or file name of transformed points
    """
        
    global TransformixBinary;    
    
    checkElastixInitialized();    
    global ElastixSettings;

    if tmpFile == None:
        tmpFile = os.path.join(tempfile.tempdir, 'elastix_input.txt');

    # write text file
    if isinstance(source, basestring):
        
        #check if we have elastix signature                 
        with open(source) as f:
            line = f.readline();
            f.close();
            
            if line[:5] == 'point' or line[:5] != 'index':
                txtfile = source;
            else:                
                points = io.readPoints(source);
                #points = points[:,[1,0,2]];
                txtfile = tmpFile;
                writePoints(txtfile, points); 
    
    elif isinstance(source, numpy.ndarray):
        txtfile = tmpFile;
        #points = source[:,[1,0,2]];
        writePoints(txtfile, source);
        
    else:
        raise RuntimeError('transformPoints: source not string or array!');
    
    
    if resultDirectory == None:
        outdirname = os.path.join(tempfile.tempdir, 'elastix_output');
    else:
        outdirname = resultDirectory;
        
    if not os.path.exists(outdirname):
        os.makedirs(outdirname);
        
    
    if transformParameterFile == None:
        if transformDirectory == None:
            RuntimeError('neither alignment directory and transformation parameter file specified!'); 
        transformparameterdir = transformDirectory
        transformparameterfile = getTransformParameterFile(transformparameterdir);
    else:
        transformparameterdir = os.path.split(transformParameterFile);
        transformparameterdir  = transformparameterdir[0];
        transformparameterfile = transformParameterFile;
    
    #transform
    #make path in parameterfiles absolute
    setPathTransformParameterFiles(transformparameterdir);
    
    #run transformix   
    cmd = TransformixBinary + ' -def ' + txtfile + ' -out ' + outdirname + ' -tp ' + transformparameterfile;
    res = os.system(cmd);
    
    if res != 0:
        raise RuntimeError('failed executing ' + cmd);
    
    
    #read data / file 
    if sink == []:
        return io.path.join(outdirname, 'outputpoints.txt')
    
    else:
        #read coordinates
        transpoints = parseElastixOutputPoints(os.path.join(outdirname, 'outputpoints.txt'), indices = indices);

        #correct x,y,z to y,x,z
        #transpoints = transpoints[:,[1,0,2]];     
        
        #cleanup
        for f in os.listdir(outdirname):
            os.remove(os.path.join(outdirname, f));
        os.rmdir(outdirname)
        
        return io.writePoints(sink, transpoints);

        
        
 

##############################################################################
### Test
##############################################################################

     
def test():
    """Test Elastix module"""
    import ClearMap.Alignment.Elastix as self
    reload(self)
    
    from ClearMap.Settings import ClearMapPath;
    import os, numpy
    
    p = ClearMapPath;
    
    resultdir = os.path.join(p, 'Test/Elastix/Output');
    
    print 'Searching for transformation parameter file in ' + resultdir;
    pf = self.getTransformParameterFile(resultdir)
      
    print 'Found: ' + pf;
    
    
    #replace path in trasform parameter files:
    self.setPathTransformParameterFiles(resultdir)
    
    #initialize
    self.initializeElastix('/home/ckirst/programs/elastix')
    self.printSettings()

    #transform points
    pts = numpy.random.rand(5,3);    
     
    print 'Transforming points: '
    tpts = self.transformPoints(pts, transformParameterFile = pf, indices = False);
    print pts
    print 'Transformed points: '
    print tpts
    
    
    #deformation and distance fields     
    df = self.deformationField(transformParameterFile = pf, resultDirectory = None);
    #df = '/tmp/elastix_output/deformationField.mhd';

    import ClearMap.IO as io
    data = io.readData('/tmp/elastix_output/deformationField.mhd');
    
    ds = self.deformationDistance(data);
    
    io.writeData(os.path.join(p, 'Test/Elastix/Output/distances.raw'), ds);
    
if __name__ == "__main__":
    test();
    





  

    
    
    
