# -*- coding: utf-8 -*-
"""
Some statistics tests not in standard python packages

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

import sys
import numpy as np

from scipy.stats import rankdata
from scipy.stats import distributions


def testCramerVonMises2Sample(x, y):
    """
    Computes the Cramer von Mises two sample test.
    
    This is a two-sided test for the null hypothesis that 2 independent samples
    are drawn from the same continuous distribution.    
    
    Parameters:
        x, y (sequence of 1-D ndarrays): two arrays of sample observations 
        assumed to be drawn from a continuous distribution, sample sizes 
        can be different

    Returns:
        (float, float): T statistic, two-tailed p-value
        
    References:
        - modified from https://github.com/scipy/scipy/pull/3659
    """
    
    #following notation of Anderson et al. doi:10.1214/aoms/1177704477
    N = len(x)
    M = len(y)
    assert N * M * (N + M) < sys.float_info.max
    
    alldata = np.concatenate((x,y))
    allranks = rankdata(alldata)
    ri = allranks[:N]
    sj = allranks[-M:]
    
    i = rankdata(x)
    j = rankdata(y)
    #Anderson et al. Eqn 10
    U = N*np.sum((ri - i)**2) + M*np.sum((sj - j)**2)
    #print U
    
    #Anderson et al. Eqn 9
    T = U/(N * M * (N + M)) - (4 * M * N - 1)/(6 * (M + N))
    #print T
    
    Texpected = 1./6 + 1./(6 * (M + N))
    Tvariance = 1./45 * (M + N + 1)/(M + N)**2 * (4 * M * N * (M+N) - 3*(M**2 + N**2) - 2*M*N)/(4 * M * N)
    
    zscore = np.abs(T - Texpected) / np.sqrt(Tvariance)
    #print zscore
    
    return T, 2*distributions.norm.sf(zscore)

