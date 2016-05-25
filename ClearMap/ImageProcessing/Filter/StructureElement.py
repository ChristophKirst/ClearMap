# -*- coding: utf-8 -*-
"""
Routines to generate various structure elements


Structured elements defined by the ``setype`` key include: 

.. _StructureElementTypes:

Structure Element Types
-----------------------

=============== =====================================
Type            Descrition
=============== =====================================
``sphere``      Sphere structure
``disk``        Disk structure
=============== =====================================

Note:
    To be extended!

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.


import numpy


def structureElement(setype = 'Disk', sesize = (3,3)):
    """Creates specific 2d and 3d structuring elements
      
    Arguments:
        setype (str): structure element type, see :ref:`StructureElementTypes`
        sesize (array or tuple): size of the structure element
    
    Returns:
        array: structure element
    """
    
    ndim = len(sesize); 
    if ndim == 2:
        return structureElement2D(setype, sesize);
    else:
        return structureElement3D(setype, sesize);



def structureElementOffsets(sesize):
    """Calculates offsets for a structural element given its size
    
    Arguments:
        sesize (array or tuple): size of the structure element
    
    Returns:
        array: offsets to center taking care of even/odd ummber of elements
    """
    
    sesize = numpy.array(sesize);
    ndim = len(sesize);
    
    o = numpy.array(((0,0),(0,0), (0,0)));
    
    for i in range(0, ndim):   
        if sesize[i] % 2 == 0:
            o[i,0] = sesize[i]/2;
            o[i,1] = sesize[i]/2 - 1 + 1;
        else:
            o[i,0] = (sesize[i]-1)/2;
            o[i,1] = o[i,0] + 1;
    
    return o.astype('int');


def structureElement2D(setype = 'Disk', sesize = (3,3)):
    """Creates specific 2d structuring elements
    
    Arguments:
        setype (str): structure element type, see :ref:`StructureElementTypes`
        sesize (array or tuple): size of the structure element
    
    Returns:
        array: structure element
    """
    
    setype = setype.lower();
           
    if len(sesize) != 2:
        raise StandardError('structureElement2D: sesize is not 2d');
        
    o = structureElementOffsets(sesize);
    omax = o.min(axis=1);
    sesize = numpy.array(sesize);
    
    if setype == 'sphere':
        g = numpy.mgrid[-o[0,0]:o[0,1], -o[1,0]:o[1,1]];
        add = ((sesize + 1) % 2) / 2.;
        x = g[0,:,:,:] + add[0];
        y = g[1,:,:,:] + add[1];

        se = 1 - (x * x / (omax[0] * omax[0]) + y * y / (omax[1] * omax[1]));
        se[se < 0] = 0;
        return se / se.sum();

    elif setype == 'disk':
       
        g = numpy.mgrid[-o[0,0]:o[0,1], -o[1,0]:o[1,1]];
        add = ((sesize + 1) % 2) / 2.;  
        
        x = g[0,:,:] + add[0];
        y = g[1,:,:] + add[1];

        se = 1 - (x * x / (omax[0] * omax[0]) + y * y / (omax[1] * omax[1]));
        se[se >= 0] = 1;
        se[se < 0] = 0;
        return se.astype('int');

    else:
        return numpy.ones(sesize);


def structureElement3D(setype = 'Disk', sesize = (3,3,3)):
    """Creates specific 3d structuring elements
        
    Arguments:
        setype (str): structure element type, see :ref:`StructureElementTypes`
        sesize (array or tuple): size of the structure element
    
    Returns:
        array: structure element
    """
    
    setype = setype.lower();
           
    if len(sesize) != 3:
        raise StandardError('structureElement3D: sesize is not 3d');
            
    o = structureElementOffsets(sesize);
    omax = o.max(axis=1);
    sesize = numpy.array(sesize);
    
    if setype == 'sphere':
        g = numpy.mgrid[-o[0,0]:o[0,1], -o[1,0]:o[1,1], -o[2,0]:o[2,1]];
        add = ((sesize + 1) % 2) / 2.;
        x = g[0,:,:,:] + add[0];
        y = g[1,:,:,:] + add[1];
        z = g[2,:,:,:] + add[2];

        se = 1 - (x * x / (omax[0] * omax[0]) + y * y / (omax[1] * omax[1]) + z * z / (omax[2] * omax[2]));
        se[se < 0] = 0;
        return se / se.sum();
        
    elif setype == 'disk':
        
        g = numpy.mgrid[-o[0,0]:o[0,1], -o[1,0]:o[1,1], -o[2,0]:o[2,1]];
        add = ((sesize + 1) % 2) / 2.;
        x = g[0,:,:,:] + add[0];
        y = g[1,:,:,:] + add[1];
        z = g[2,:,:,:] + add[2];
        
        se = 1 - (x * x / (omax[0] * omax[0]) + y * y / (omax[1] * omax[1]) + z * z / (omax[2] * omax[2]));
        se[se < 0] = 0;
        se[se > 0] = 1;
        return se.astype('int');
    
    else:
        return numpy.ones(sesize);
        

    
     