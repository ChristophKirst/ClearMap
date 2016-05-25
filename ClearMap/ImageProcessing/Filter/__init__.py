# -*- coding: utf-8 -*-
"""This sub-package provides various volumetric filter kernels and structure elments

A set of linear filters can be applied to the data using 
:mod:`~ClearMap.ImageProcessing.Filter.LinearFilter`. 

Because its utility for cell detection the difference of Gaussians filter
is implemented directly in :mod:`~ClearMap.ImageProcessing.Filter.DoGFilter`.

The fitler kernels defined in :mod:`~ClearMap.ImageProcessing.Filter.FilterKernel` 
can be used in combination with the :mod:`~ClearMap.ImageProcessing.Convolution` 
module.

Structured elements defined in 
:mod:`~ClearMap.ImageProcessing.Filter.StructureElements` can be used in 
combination with various morphological operations, e.g. used in the
:mod:~ClearMap.ImageProcessing.BackgroundRemoval` module.

"""  
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.