"""
Grey reconstruction module

This morphological reconstruction routine was adapted from 
`CellProfiler <http://www.cellprofiler.org>`_.

Author
""""""
    Original author: Lee Kamentsky 
    Copyright (c) 2003-2009 Massachusetts Institute of Technology
    Copyright (c) 2009-2011 Broad Institute

    Modified by Chirstoph Kirst to optimize integration
    into ClearMap, The Rockefeller University, New York City, 2015
"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import numpy as np

import sys

from ClearMap.ImageProcessing.Filter.StructureElement import structureElement
from ClearMap.ImageProcessing.StackProcessing import writeSubStack

from ClearMap.Utils.Timer import Timer
from ClearMap.Utils.ParameterTools import getParameter, writeParameter

from ClearMap.Visualization.Plot import plotTiling



from skimage.filters._rank_order import rank_order

def reconstruct(seed, mask, method = 'dilation', selem = None, offset = None):
    """Performs a morphological reconstruction of an image.

    Reconstruction uses a seed image, which specifies the values
    to dilate and a mask image that gives the maximum allowed dilated value at
    each pixel.
    
    The algorithm is taken from [1]_. Applications for greyscale 
    reconstruction are discussed in [2]_ and [3]_.

    Arguments:
        seed (array): seed image to be dilated or eroded.
        mask (array): maximum (dilation) / minimum (erosion) allowed
        method (str): {'dilation'|'erosion'}
        selem (array): structuring element
        offset (array or None): offset of the structuring element, None is centered

    Returns:
        array: result of morphological reconstruction.
        
    Note: 
        Operates on 2d images.
    
    Reference:
    
    .. [1] Robinson, "Efficient morphological reconstruction: a downhill
           filter", Pattern Recognition Letters 25 (2004) 1759-1767.
    .. [2] Vincent, L., "Morphological Grayscale Reconstruction in Image
           Analysis: Applications and Efficient Algorithms", IEEE Transactions
           on Image Processing (1993)
    .. [3] Soille, P., "Morphological Image Analysis: Principles and
           Applications", Chapter 6, 2nd edition (2003), ISBN 3540429883.
    """
    
    assert tuple(seed.shape) == tuple(mask.shape)
    if method == 'dilation' and np.any(seed > mask):
        raise ValueError("Intensity of seed image must be less than that "
                         "of the mask image for reconstruction by dilation.")
    elif method == 'erosion' and np.any(seed < mask):
        raise ValueError("Intensity of seed image must be greater than that "
                         "of the mask image for reconstruction by erosion.")
    try:
        from skimage.morphology._greyreconstruct import reconstruction_loop
    except ImportError:
        raise ImportError("_greyreconstruct extension not available.")

    if selem is None:
        selem = np.ones([3] * seed.ndim, dtype=bool)
    else:
        selem = selem.copy()

    if offset is None:
        if not all([d % 2 == 1 for d in selem.shape]):
            ValueError("Footprint dimensions must all be odd")
        offset = np.array([d // 2 for d in selem.shape])
    
    # Cross out the center of the selem
    selem[[slice(d, d + 1) for d in offset]] = False

    # Make padding for edges of reconstructed image so we can ignore boundaries
    padding = (np.array(selem.shape) / 2).astype(int)
    dims = np.zeros(seed.ndim + 1, dtype=int)
    dims[1:] = np.array(seed.shape) + 2 * padding
    dims[0] = 2
    inside_slices = [slice(p, -p) for p in padding]
    # Set padded region to minimum image intensity and mask along first axis so
    # we can interleave image and mask pixels when sorting.
    if method == 'dilation':
        pad_value = np.min(seed)
    elif method == 'erosion':
        pad_value = np.max(seed)
    images = np.ones(dims, dtype = seed.dtype) * pad_value
    images[[0] + inside_slices] = seed
    images[[1] + inside_slices] = mask

    # Create a list of strides across the array to get the neighbors within
    # a flattened array
    value_stride = np.array(images.strides[1:]) / images.dtype.itemsize
    image_stride = images.strides[0] // images.dtype.itemsize
    selem_mgrid = np.mgrid[[slice(-o, d - o)
                            for d, o in zip(selem.shape, offset)]]
    selem_offsets = selem_mgrid[:, selem].transpose()
    nb_strides = np.array([np.sum(value_stride * selem_offset)
                           for selem_offset in selem_offsets], np.int32)

    images = images.flatten()

    # Erosion goes smallest to largest; dilation goes largest to smallest.
    index_sorted = np.argsort(images).astype(np.int32)
    if method == 'dilation':
        index_sorted = index_sorted[::-1]

    # Make a linked list of pixels sorted by value. -1 is the list terminator.
    prev = -np.ones(len(images), np.int32)
    next = -np.ones(len(images), np.int32)
    prev[index_sorted[1:]] = index_sorted[:-1]
    next[index_sorted[:-1]] = index_sorted[1:]

    # Cython inner-loop compares the rank of pixel values.
    if method == 'dilation':
        value_rank, value_map = rank_order(images)
    elif method == 'erosion':
        value_rank, value_map = rank_order(-images)
        value_map = -value_map

    start = index_sorted[0]
    reconstruction_loop(value_rank, prev, next, nb_strides, start, image_stride)

    # Reshape reconstructed image to original image shape and remove padding.
    rec_img = value_map[value_rank[:image_stride]]
    rec_img.shape = np.array(seed.shape) + 2 * padding
    
    return rec_img[inside_slices]



def greyReconstruction(img, mask, greyReconstructionParameter = None, method = None, size = 3, save = None, verbose = False,
                       subStack = None, out = sys.stdout, **parameter):
    """Calculates the grey reconstruction of the image 
    
    Reconstruction is done z-slice by z-slice.
    
    Arguments:
        img (array): image data
        removeBackGroundParameter (dict):
            ========= ==================== ===========================================================
            Name      Type                 Descritption
            ========= ==================== ===========================================================
            *method*  (tuple or None)      'dilation' or 'erosion', if None return original image
            *size*    (int or tuple)       size of structuring element
            *save*    (str or None)        file name to save result of this operation
                                           if None dont save to file 
            *verbose* (bool or int)        print / plot information about this step 
            ========= ==================== ===========================================================
        subStack (dict or None): sub-stack information 
        verbose (bool): print progress info 
        out (object): object to write progress info to
        
    Returns:
        array: grey reconstructed image
    """
    
    method = getParameter(greyReconstructionParameter, "method", method);
    size   = getParameter(greyReconstructionParameter, "size", size);
    save   = getParameter(greyReconstructionParameter, "save", save);    
    verbose= getParameter(greyReconstructionParameter, "verbose", verbose);   
    
    if verbose:
        writeParameter(out = out, head = 'Grey reconstruction:', method = method, size = size, save = save);
    
    if method is None:
        return img;
    
    timer = Timer();
    
    # background subtraction in each slice
    se = structureElement('Disk', size).astype('uint8');
    for z in range(img.shape[2]):
         #img[:,:,z] = img[:,:,z] - grey_opening(img[:,:,z], structure = structureElement('Disk', (30,30)));
         #img[:,:,z] = img[:,:,z] - morph.grey_opening(img[:,:,z], structure = self.structureELement('Disk', (150,150)));
         img[:,:,z] = img[:,:,z] - reconstruct(img[:,:,z], method = method, selem = se)
    
    if not save is None:
        writeSubStack(save, img, subStack = subStack)

    if verbose > 1:
        plotTiling(img);

    if verbose:
        out.write(timer.elapsedTime(head = 'Grey reconstruction:') + '\n');
    
    return img 

