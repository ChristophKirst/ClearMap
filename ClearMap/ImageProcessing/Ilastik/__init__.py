"""
This sub-package provides interfaces to external image processing software

Supported functionality:

   * Ilastik interface

Main routines for ilastik classification are:
:func:`~ClearMap.Imageprocessing.Ilastik.classifyPixel`,
:func:`~ClearMap.Imageprocessing.Ilastik.classifyCells`.

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

#__all__ = ['Ilastik'];

from ClearMap.ImageProcessing.Ilastik.Ilastik import * 

