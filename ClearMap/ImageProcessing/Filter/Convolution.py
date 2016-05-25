# -*- coding: utf-8 -*-
"""
Convolve volumetric data with a 3d kernel, optimized for memory / float32 use

Based on `scipy.signal <http://docs.scipy.org/doc/scipy/reference/signal.html>`_
routines.

Author
""""""
    Original code from `scipy.signal <http://docs.scipy.org/doc/scipy/reference/signal.html>`_.

    Modified by Chirstoph Kirst to optimize memory and sped and integration into ClearMap.
    The Rockefeller University, New York City, 2015
"""

import numpy
import scipy.fftpack as fft


def _next_regular(target):
    """
    Find the next regular number greater than or equal to target.
    Regular numbers are composites of the prime factors 2, 3, and 5.
    Also known as 5-smooth numbers or Hamming numbers, these are the optimal
    size for inputs to FFTPACK.
    Target must be a positive integer.
    """
    if target <= 6:
        return target

    # Quickly check if it's already a power of 2
    if not (target & (target-1)):
        return target

    match = float('inf')  # Anything found will be smaller
    p5 = 1
    while p5 < target:
        p35 = p5
        while p35 < target:
            # Ceiling integer division, avoiding conversion to float
            # (quotient = ceil(target / p35))
            quotient = -(-target // p35)

            # Quickly find next power of 2 >= quotient
            try:
                p2 = 2**((quotient - 1).bit_length())
            except AttributeError:
                # Fallback for Python <2.7
                p2 = 2**(len(bin(quotient - 1)) - 2)

            N = p2 * p35
            if N == target:
                return N
            elif N < match:
                match = N
            p35 *= 3
            if p35 == target:
                return p35
        if p35 < match:
            match = p35
        p5 *= 5
        if p5 == target:
            return p5
    if p5 < match:
        match = p5
    return match



def _cook_nd_args(a, s=None, axes=None, invreal=0):
    if s is None:
        shapeless = 1
        if axes is None:
            s = list(a.shape)
        else:
            s = numpy.take(a.shape, axes)
    else:
        shapeless = 0
    s = list(s)
    if axes is None:
        axes = list(range(-len(s), 0))
    if len(s) != len(axes):
        raise ValueError("Shape and axes have different lengths.")
    if invreal and shapeless:
        s[-1] = (a.shape[axes[-1]] - 1) * 2
    return s, axes    
    

def _centered(arr, newsize):
    # Return the center newsize portion of the array.
    newsize = numpy.asarray(newsize)
    currsize = numpy.array(arr.shape)
    startind = (currsize - newsize) // 2
    endind = startind + newsize
    myslice = [slice(startind[k], endind[k]) for k in range(len(endind))]
    return arr[tuple(myslice)]


#def _rfftn(a, s=None, axes=None):
#    s, axes = _cook_nd_args(a, s, axes);
#    a = fft.rfft(a, s[-1], axes[-1], overwrite_x = True)
#    for ii in range(len(axes)-1):
#        a = fft.fft(a, s[ii], axes[ii], overwrite_x = True)
#    return a

#def _irfftn(a, s=None, axes=None):   
#    #a = asarray(a).astype('complex64')
#    s, axes = _cook_nd_args(a, s, axes, invreal=1)
#    for ii in range(len(axes)-1):
#        a = fft.ifft(a, s[ii], axes[ii], overwrite_x = True);
#    a = fft.ifft(a, s[-1], axes[-1], overwrite_x = True);
#    a = a.real;
#    return a

def _rfftn(a, s=None, axes=None):
    return fft.fftn(a, shape = s, axes = axes);

def _irfftn(a, s=None, axes=None):
    return fft.ifftn(a, shape = s, axes = axes).real;



def convolve(x, k, mode = 'same'):
    """Convolve array with kernel using float32 / complex64, optimized for memory consumption and speed
    
    Arguments:
        x (array): data to be convolved
        k (array): filter kernel
        
    Returns:
        array: convolution
    """
    
    s1 = numpy.array(x.shape)
    s2 = numpy.array(k.shape)      
    shape =  s1 + s2 - 1;
    
    fshape = [_next_regular(int(d)) for d in shape];
    fslice = tuple([slice(0, int(sz)) for sz in shape]);
    
    #scipys fftpack keeps float32    
    #ret = irfftn(rfftn(in1, fshape) * rfftn(in2, fshape), fshape)[fslice].copy()
    ret = _irfftn(_rfftn(x, fshape) * _rfftn(k, fshape), fshape)[fslice];
    
    if mode == "full":
        return ret
    elif mode == "same":
        return _centered(ret, s1)
    else:
        raise ValueError("Acceptable mode flags are 'same' or 'full'.")
   
        
def _test():
    """Test for Convolution module"""
    import numpy as np
    
    x = np.random.rand(50,50,50);
    k = np.random.rand(5,5,5);
    
    x = x.astype('float32');
    k = k.astype('float32');
    
    from scipy.signal import fftconvolve;
    
    cs = fftconvolve(x,k, mode='same');
    co = convolve(x,k);
    
    print 'shapes:'
    print cs.shape
    print co.shape
    
    print 'dtypes:'
    print cs.dtype;
    print co.dtype;
    
    print 'difference:'
    diff = numpy.abs(cs-co);
    print diff.max()
    
if __name__ == "__main__":
    _test()
    
    
    
    
    
    