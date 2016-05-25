# -*- coding: utf-8 -*-
"""
Functions to gather iamge statistics in large volumetric images

The main routines extract information from a large volumetric image, such as 
the maximum or mean.
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy

from ClearMap.ImageProcessing.StackProcessing import parallelProcessStack, sequentiallyProcessStack, writeSubStack

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter, joinParameter

#from ClearMap.Visualization.Plot import plotTiling



def calculateStatistics(source, sink = None, calculateStatisticsParameter = None, method = "Max", remove = True, processMethod = all, verbose = False, **parameter):
    """Calculate statisticsfrom image data
    
    This is a main script to start extracting statistics of volumetric image data.    
    
    Arguments:
        source (str or array): Image source
        sink (str or None): destination for the results
        calculateStatisticsParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *method*  (str or function)    function to extract statistic, must be trivially distributable
                                           if None, do not extract information
            *remove*  (bool)               remove redundant overlap 
            *verbose* (bool or int)        print / plot information about this step                                 
            ========= ==================== ===========================================================
        method (str or function): 
        processMethod (str or all): 'sequential' or 'parallel'. if all its choosen automatically
        verbose (bool): print info
        **parameter (dict): parameter for the image processing sub-routines
    
    Returns:
        list of statistics
    """
    timer = Timer();
        
    method = getParameter(calculateStatisticsParameter, "method", method);
    remove = getParameter(calculateStatisticsParameter, "remove", remove);
    verbose = getParameter(calculateStatisticsParameter, "verbose", verbose); 
        
    # run segmentation
    if remove:
        parameter = joinParameter({"chunkOverlap" : 0}, parameter);
      
    if processMethod == 'sequential':
        result = sequentiallyProcessStack(source, sink = sink, function = calculateStatisticsOnStack, join = joinStatistics, method = method, remove= remove, verbose = verbose, **parameter);  
    elif processMethod is all or processMethod == 'parallel':
        result = parallelProcessStack(source, sink = sink, function = calculateStatisticsOnStack, join = joinStatistics, method = method, remove= remove, verbose = verbose, **parameter);  
    else:
        raise RuntimeError("calculateStatistics: invalid processMethod %s" % str(processMethod));
    
    if verbose:
        timer.printElapsedTime("Total Time Image Statistics");
    
    return result;




def _methodToFunction(method):
    if isinstance(method, str):
        if method.lower() == 'max':
            return numpy.max;                
        elif method.lower() == 'mean':
            return numpy.mean;
    else:
        return method;


def calculateStatisticsOnStack(img, calculateStatisticsParameter = None, method = 'Max', remove = True, verbose = False,
                        subStack = None, out = sys.stdout, **parameter):
    """Calculate a statistics from a large volumetric image
    
    The statistics is assumed to be trivially distributable, i.e. max or mean.
    
    Arguments:
        img (array): image data
        calculateStatisticsParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *method*  (str or function)    function to extract statistic, must be trivially distributable
                                           if None, do not extract information
            *remove*  (bool)               remove redundant overlap 
            *verbose* (bool or int)        print / plot information about this step                                 
            ========= ==================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array or number: extracted statistics
        
    Note:
        One might need to choose zero overlap in the stacks to function properly!
    """
    
    method = getParameter(calculateStatisticsParameter, "method", method);
    remove = getParameter(calculateStatisticsParameter, "remove", remove);
    verbose = getParameter(calculateStatisticsParameter, "verbose", verbose);   
    
    if verbose:
        writeParameter(out = out, head = 'Image Statistics:', method = method);
    
    if method is None:    
        return None;
    
    timer = Timer();
    
    if not isinstance(method,list):
        method = [method];
        
    s =[];
    for m in range(len(method)):
          f = _methodToFunction(method[m]);
          
          if remove and not subStack is None:
              img = writeSubStack(None, img, subStack = subStack);
        
          #print img.shape
          s.append(f(img));

    if verbose:
        out.write(timer.elapsedTime(head = 'Image Statistics:') + '\n');
    
    return s;



def joinStatistics(results, calculateStatisticsParameter = None, method = 'Max', subStacks = None, **parameter):
    """Joins a list of calculated statistics
    
    Arguments:
        results (list): list of statics results from the individual sub-processes
        calculateStatisticsParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *method*  (str or function)    function to extract statistic, must be trivially distributable
                                           if None, do not extract information                              
            ========= ==================== ===========================================================
        subStacks (list or None): list of all sub-stack information, see :ref:`SubStack`

    
    Returns:
       list or object: joined statistics
    """
    
    method  = getParameter(calculateStatisticsParameter, "method",  method); 
    
    nchunks = len(results);

    singleMethod = False;    
    if not isinstance(method,list):
        singleMethod = True;    
        method =[method];
    
    s = [];    
    for m in range(len(method)):
        r = [results[i][m] for i in range(nchunks)];
        
        f = _methodToFunction(method[m]);
        if f == _methodToFunction('mean'):
            #weight by chunk size:
            if not subStacks is None:
                r = [r[i] * (subStacks[i]['z'][1] - subStacks[i]['z'][0]) for i in range(nchunks)];
                tot = numpy.sum([(subStacks[i]['z'][1] - subStacks[i]['z'][0]) for i in range(nchunks)]);
                r = f(r);
                r = r / float(tot);
            else:
                r = f(r);
            
            s.append(r);
            
        else:
            
            s.append(f(r));
    
    if singleMethod:
        return s[0];
    else:
        return s;