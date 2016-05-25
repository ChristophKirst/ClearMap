"""
This sub-package provides an interface to alignment tools in order to 
register cleared samples to atlases or reference samples.

Supported functionality:

    * resampling and reorientation of large volumetric images in the 
      :mod:`~ClearMap.Alignment.Resampling` module.
    * registering volumetric data onto references via 
      `Elastix <http://elastix.isi.uu.nl/>`_ in the 
      :mod:`~ClearMap.Alignment.Elastix` module.

Main routines for resampling are: 
:func:`~ClearMap.Alignment.Resampling.resampleData` 
and :func:`~ClearMap.Alignment.Resampling.resamplePoints`.

Main routines for elastix registration are: 
:func:`~ClearMap.Alignment.Elastix.alignData`, 
:func:`~ClearMap.Alignment.Elastix.transformData` and 
:func:`~ClearMap.Alignment.Elastix.transformPoints`.

""" 
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


__all__ = ['Elastix', 'Resampling'];