# -*- coding: utf-8 -*-
"""
Cython code to convert point data into voxel image data for visulaization and analysis

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.

#cimport cython 

import numpy as np
cimport numpy as np

#IM_TYPE = np.int_
#ctypedef np.int_t IM_TYPE_t
#ctypedef np.float_t PT_TYPE_t

#@cython.boundscheck(False)  # turn of bounds-checking for entire function
def voxelizeSphere(np.ndarray[np.float_t, ndim=2] points, int xsize, int ysize, int zsize, float xdiam, float ydiam, float zdiam):
    """Converts a list of points into an volumetric image array using uniformly filled spheres at the center of each point"""
    
    cdef np.ndarray[np.int32_t, ndim =3] voximg = np.zeros([xsize, ysize, zsize], dtype=np.int32)

    cdef int iCentroid = 0
    cdef int nCentroid = points.shape[0]
    cdef int nSphereIndices = int(xdiam * ydiam * zdiam)

    # precompute indices centered at 0,0,0
    cdef np.ndarray[np.int_t, ndim = 1] xs = np.zeros([nSphereIndices], dtype=np.int)
    cdef np.ndarray[np.int_t, ndim = 1] ys = np.zeros([nSphereIndices], dtype=np.int)
    cdef np.ndarray[np.int_t, ndim = 1] zs = np.zeros([nSphereIndices], dtype=np.int)
    cdef int ns = 0

    cdef float xdiam2 = (xdiam - 1) * (xdiam - 1) / 4
    cdef float ydiam2 = (ydiam - 1) * (ydiam - 1) / 4
    cdef float zdiam2 = (zdiam - 1) * (zdiam - 1) / 4
    
    for x in range(int(-xdiam/2 + 1), int(xdiam/2 + 1)):
        for y in range(int(-ydiam/2 + 1), int(ydiam/2 + 1)):
            for z in range(int(-zdiam/2 + 1), int(zdiam/2 + 1)):
                if x*x / xdiam2 + y*y / ydiam2 + z*z / zdiam2 < 1:
                    xs[ns] = x; ys[ns] = y; zs[ns] = z;
                    ns += 1;
                    
    cdef int iss = 0
    cdef float cx0
    cdef float cy0
    cdef float cz0
    
    cdef float cxf
    cdef float cyf
    cdef float czf
    
    cdef int cx
    cdef int cy
    cdef int cz
                    
    for iCentroid in range(nCentroid):
        if ((iCentroid % 25000) == 0):
            print "\nProcessed %d/%d\n" % (iCentroid, nCentroid);
    
        cx0 = points[iCentroid, 0];
        cy0 = points[iCentroid, 1];
        cz0 = points[iCentroid, 2];
        
        for iss in range(ns):
            cxf = cx0 + xs[iss];
            cyf = cy0 + ys[iss];
            czf = cz0 + zs[iss];
            
            if cxf >= 0 and cxf < xsize:
                if cyf >= 0 and cyf < ysize:
                    if czf >= 0 and czf < zsize:
                        cx = int(cxf);
                        cy = int(cyf);
                        cz = int(czf);
                        
                        voximg[cx,cy,cz] = voximg[cx,cy,cz] + 1;
                        
    return voximg;
    


#@cython.boundscheck(False)  # turn of bounds-checking for entire function
def voxelizeSphereWithWeights(np.ndarray[np.float_t, ndim=2] points, int xsize, int ysize, int zsize, float xdiam, float ydiam, float zdiam, np.ndarray[np.float_t, ndim=1] weights):
    """Converts a list of points into an volumetric image array using uniformly filled spheres at the center of each point with a weight for each point""" 
    
    cdef np.ndarray[np.float_t, ndim =3] voximg = np.zeros([xsize, ysize, zsize], dtype=np.float)

    cdef int iCentroid = 0
    cdef int nCentroid = points.shape[0]
    cdef int nSphereIndices = int(xdiam * ydiam * zdiam)

    # precompute indices centered at 0,0,0
    cdef np.ndarray[np.int_t, ndim = 1] xs = np.zeros([nSphereIndices], dtype=np.int)
    cdef np.ndarray[np.int_t, ndim = 1] ys = np.zeros([nSphereIndices], dtype=np.int)
    cdef np.ndarray[np.int_t, ndim = 1] zs = np.zeros([nSphereIndices], dtype=np.int)
    cdef int ns = 0

    cdef float xdiam2 = (xdiam - 1) * (xdiam - 1) / 4
    cdef float ydiam2 = (ydiam - 1) * (ydiam - 1) / 4
    cdef float zdiam2 = (zdiam - 1) * (zdiam - 1) / 4
    
    for x in range(int(-xdiam/2 + 1), int(xdiam/2 + 1)):
        for y in range(int(-ydiam/2 + 1), int(ydiam/2 + 1)):
            for z in range(int(-zdiam/2 + 1), int(zdiam/2 + 1)):
                if x*x / xdiam2 + y*y / ydiam2 + z*z / zdiam2 < 1:
                    xs[ns] = x; ys[ns] = y; zs[ns] = z;
                    ns += 1;
                    
    cdef int iss = 0
    cdef float cx0
    cdef float cy0
    cdef float cz0
    
    cdef float cxf
    cdef float cyf
    cdef float czf
    
    cdef int cx
    cdef int cy
    cdef int cz
                    
    for iCentroid in range(nCentroid):
        if ((iCentroid % 25000) == 0):
            print "\nProcessed %d/%d\n" % (iCentroid, nCentroid);
    
        cx0 = points[iCentroid, 0];
        cy0 = points[iCentroid, 1];
        cz0 = points[iCentroid, 2];
        
        for iss in range(ns):
            cxf = cx0 + xs[iss];
            cyf = cy0 + ys[iss];
            czf = cz0 + zs[iss];
            
            if cxf >= 0 and cxf < xsize:
                if cyf >= 0 and cyf < ysize:
                    if czf >= 0 and czf < zsize:
                        cx = int(cxf);
                        cy = int(cyf);
                        cz = int(czf);
                        
                        voximg[cx,cy,cz] = voximg[cx,cy,cz] + weights[iCentroid];
                        
    return voximg;
    
    
#@cython.boundscheck(False)  # turn of bounds-checking for entire function
def voxelizeRectangle(np.ndarray[np.float_t, ndim=2] points, int xsize, int ysize, int zsize, float xdiam, float ydiam, float zdiam):
    """Converts a list of points into an volumetric image array using uniformly filled rectangle at the center of each point""" 
        
    cdef np.ndarray[np.int32_t, ndim =3] voximg = np.zeros([xsize, ysize, zsize], dtype=np.int32)

    cdef int iCentroid = 0
    cdef int nCentroid = points.shape[0]
                    
    cdef int iss = 0
    
    cdef float cxf
    cdef float cyf
    cdef float czf
    
    cdef int cx
    cdef int cy
    cdef int cz
    
    cdef int xmin = int(-xdiam/2 + 1)
    cdef int xmax = int(xdiam/2 + 1)
    
    cdef int ymin = int(-ydiam/2 + 1)
    cdef int ymax = int(ydiam/2 + 1)
    
    cdef int zmin = int(-zdiam/2 + 1)
    cdef int zmax = int(zdiam/2 + 1)
    
    cdef int xl, xh, yl, yh, zl, zh
                    
    for iCentroid in range(nCentroid):
        if ((iCentroid % 25000) == 0):
            print "\nProcessed %d/%d\n" % (iCentroid, nCentroid);
    
        cx0 = points[iCentroid, 0];
        cy0 = points[iCentroid, 1];
        cz0 = points[iCentroid, 2];
        
        xl = max(0, int(cx0 + xmin));
        xh = min(xsize, int(cx0 + xmax));
    
        yl = max(0, int(cy0 + ymin));
        yh = min(xsize, int(cy0 + ymax));   
        
        zl = max(0, int(cz0 + zmin));
        zh = min(zsize, int(cz0 + zmax));   
        
        for xs in range(xl,xh):
            for ys in range(yl,yh):
                for zs in range(zl,zh):
                    voximg[xs,ys,zs] = voximg[xs,ys,zs] + 1;
                        
    return voximg;
    
    
       
#@cython.boundscheck(False)  # turn of bounds-checking for entire function
def voxelizeRectangleWithWeights(np.ndarray[np.float_t, ndim=2] points, int xsize, int ysize, int zsize, float xdiam, float ydiam, float zdiam, np.ndarray[np.float_t, ndim=1] weights):
    """Converts a list of points into an volumetric image array using uniformly filled rectangle at the center of each point with a weight factor for each array"""     
    
    cdef np.ndarray[np.float_t, ndim =3] voximg = np.zeros([xsize, ysize, zsize], dtype=np.float)

    cdef int iCentroid = 0
    cdef int nCentroid = points.shape[0]
                    
    cdef int iss = 0
    
    cdef float cxf
    cdef float cyf
    cdef float czf
    
    cdef int cx
    cdef int cy
    cdef int cz
    
    cdef int xmin = int(-xdiam/2 + 1)
    cdef int xmax = int(xdiam/2 + 1)
    
    cdef int ymin = int(-ydiam/2 + 1)
    cdef int ymax = int(ydiam/2 + 1)
    
    cdef int zmin = int(-zdiam/2 + 1)
    cdef int zmax = int(zdiam/2 + 1)
    
    cdef int xl, xh, yl, yh, zl, zh
                    
    for iCentroid in range(nCentroid):
        if ((iCentroid % 25000) == 0):
            print "\nProcessed %d/%d\n" % (iCentroid, nCentroid);
    
        cx0 = points[iCentroid, 0];
        cy0 = points[iCentroid, 1];
        cz0 = points[iCentroid, 2];
        
        xl = max(0, int(cx0 + xmin));
        xh = min(xsize, int(cx0 + xmax));
    
        yl = max(0, int(cy0 + ymin));
        yh = min(xsize, int(cy0 + ymax));   
        
        zl = max(0, int(cz0 + zmin));
        zh = min(zsize, int(cz0 + zmax));   
        
        for xs in range(xl,xh):
            for ys in range(yl,yh):
                for zs in range(zl,zh):
                    voximg[xs,ys,zs] = voximg[xs,ys,zs] + weights[iCentroid];
                        
    return voximg;