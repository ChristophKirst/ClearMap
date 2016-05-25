# -*- coding: utf-8 -*-
"""
Method to extend interpolation objects to constantly / linearly extrapolate.

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import scipy.interpolate

from numpy import array


def extrap1d(x, y, interpolation = 'linear', exterpolation = 'constant'):
    """Interpolate on given values and extrapolate outside the given data
    
    Arguments:
        x (numpy.array): x values of the data to interpolate
        y (numpy.array): y values of the data to interpolate
        interpolation (Optional[str]): interpolation method, see kind of scipy.interpolate.interp1d, default: "linear"
        exterpolation (Optional[str]): interpolation method, either "linear" or "constant"
    
    Returns:
        (function): inter- and extra-polation function
    """
        
    interpolator = scipy.interpolate.interp1d(x, y, kind = interpolation);
    return extrap1dFromInterp1d(interpolator, exterpolation);   


def  extrap1dFromInterp1d(interpolator, exterpolation = 'constant'):
    """Extend interpolation function to extrapolate outside the given data
    
    Arguments:
        interpolator (function): interpolating function, see e.g. scipy.interpolate.interp1d
        exterpolation (Optional[str]): interpolation method, either "linear" or "constant"
    
    Returns:
        (function): inter- and extra-polation function
    """    
    xs = interpolator.x
    ys = interpolator.y
    cs = (exterpolation == 'constant');

    def pointwise(x):
        if cs:   #constant extrapolation
            if x < xs[0]:
                return ys[0];
            elif x > xs[-1]:
                return ys[-1];
            else:
                return interpolator(x);
        else:  # linear extrapolation
            if x < xs[0]:
                return ys[0]+(x-xs[0])*(ys[1]-ys[0])/(xs[1]-xs[0])
            elif x > xs[-1]:
                return ys[-1]+(x-xs[-1])*(ys[-1]-ys[-2])/(xs[-1]-xs[-2])
            else:
                return interpolator(x)

    def extrapfunc(xs):
        return array(map(pointwise, array(xs)))

    return extrapfunc