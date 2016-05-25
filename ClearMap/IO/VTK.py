# -*- coding: utf-8 -*-
"""
Interface to write points to VTK files

Notes:
    - points are assumed to be in [x,y,z] coordinates as standard in ClearMap
    - reading of points not supported at the moment!

"""
#:copyright: Copyright 2015 by Christoph Kirst, The Rockefeller University, New York City
#:license: GNU, see LICENSE.txt for details.
# Modified from a matlab code by Kannan Umadevi Venkataraju

#from evtk.hl import pointsToVTK 

import numpy;

import ClearMap.IO as io;

def writePoints(filename, points, labelImage = None):
    """Write point data to vtk file
    
    Arguments:
        filename (str): file name
        points (array): point data
        labelImage (str, array or None): optional label image to determine point label
    
    Returns:
        str: file name
    """

    #y = points[:,0];
    #x = points[:,1];
    #z = points[:,2];    
    
    x = points[:,0];
    y = points[:,1];
    z = points[:,2];    
    nPoint = x.size;
    
    #print nPoint;
    
    pointLabels = numpy.ones(nPoint);
    if not labelImage is None:
        if isinstance(labelImage, basestring):
            labelImage = io.readData(labelImage);
            
        dsize = labelImage.shape;
        for i in range(nPoint):
            #if y[i] >= 0 and y[i] < dsize[0] and x[i] >= 0 and x[i] < dsize[1] and z[i] >= 0 and z[i] < dsize[2]:
            if x[i] >= 0 and x[i] < dsize[0] and y[i] >= 0 and y[i] < dsize[1] and z[i] >= 0 and z[i] < dsize[2]:
                 #pointLabels[i] = labelImage[y[i], x[i], z[i]];
                 pointLabels[i] = labelImage[x[i], y[i], z[i]];
        
    #write VTK file
    vtkFile = file(filename, 'w')
    vtkFile.write('# vtk DataFile Version 2.0\n');
    vtkFile.write('Unstructured Grid Example\n');
    vtkFile.write('ASCII\n');
    vtkFile.write('DATASET UNSTRUCTURED_GRID\n');
    vtkFile.write("POINTS " + str(nPoint) + " float\n")
    for iPoint in range(nPoint):
        vtkFile.write(str(x[iPoint]).format('%05.20f') + " " +  str(y[iPoint]).format('%05.20f') + " " + str(z[iPoint]).format('%05.20f') + "\n");    
    
    vtkFile.write("CELLS " + str(nPoint) + " " + str(nPoint * 2) + "\n");


    for iPoint in range(nPoint):
        vtkFile.write("1 " + str(iPoint) + "\n");
    vtkFile.write("CELL_TYPES " + str(nPoint) + "\n");
    for iPoint in range(0, nPoint):
        vtkFile.write("1 \n");
    #vtkFile.write("\n");
    vtkFile.write("POINT_DATA " + str(nPoint) + "\n");
    vtkFile.write('SCALARS scalars float 1\n');
    vtkFile.write("LOOKUP_TABLE default\n");
    for iLabel in pointLabels:
        vtkFile.write(str(int(iLabel)) + " ");
        #vtkFile.write("1 ")
    vtkFile.write("\n");
    vtkFile.close();   
    
    return filename;


def readPoints(filename, **args):
    """Read points form vtk file
    
    Notes:
        - Not implmented yet !
    """
    raise RuntimeError('readPoints for VTK files not implmented!');






#%%
############# Stuff -> test above then delete this here//./
#
#if (numel(varargin) >= 2)
#    labelList = varargin{2};
#    labelIndices = ismember (pointLabels, labelList);
#    pointList = pointList (:, labelIndices);
#    pointLabels = pointLabels(labelIndices);
#end
#
#nPoint = size (pointList, 2);
#
#%%Swap x and y axis
#pointListx = pointList(2,:);
#pointListy = pointList(1,:);
#pointList(1,:) = pointListx;
#pointList(2,:) = pointListy;
#
#%% Write VTK File
#fp = fopen (vtkFileName, 'w+');
#fprintf (fp, '# vtk DataFile Version 2.0\n');
#fprintf (fp, 'Unstructured Grid Example\n');
#fprintf (fp, 'ASCII\n');
#fprintf (fp, 'DATASET UNSTRUCTURED_GRID\n');
#fprintf (fp, 'POINTS %d float\n', nPoint);
#fprintf (fp, '%05.20f %5.20f %5.20f\n', pointList);
#fprintf (fp, 'CELLS %d %d\n',nPoint, nPoint * 2);
#fprintf (fp, '%d %d\n', [ones(nPoint, 1) [0:nPoint-1]']');
#fprintf (fp, 'CELL_TYPES %d\n', nPoint);
#fprintf (fp, '%d\n', ones (nPoint, 1));
#fprintf (fp, 'POINT_DATA %d\n',nPoint);
#fprintf (fp, 'SCALARS scalars float 1\n');
#fprintf (fp, 'LOOKUP_TABLE default\n');
#fprintf (fp, '%f ', pointLabels);
#fclose (fp);
#
#
#
#
##def writePoints(filename, points, data = None):
##    x = points[:,0];
##    y = points[:,1];
##    z = points[:,2];
##    
##    pointsToVTK(filename, x, y, z, data = data);
#    
#  
#def readPoints(filename):
#    raise RuntimeError("Reading points from VTK file not implemented yet""")
#
#  
#  
#
# vtkFileName is the file name to be written
# pointList is the list of x, y, z points to be written
# pointsLabel is the label for each point, it tell which region on brain the cell belongs to
#
#def writeSparsePointsWithLabelVTKFile (vtkFileName, pointList, pointLabels):
#    #swap x and y axis
#    x = pointList[:,1];
#    y = pointList[:,0];
#    z = pointList[:,2];
#    
#    nPoint = x.size;
#    
#    #write VTK file
#    vtkFile = open(vtkFileName, 'w')
#    vtkFile.write('# vtk DataFile Version 2.0\n');
#    vtkFile.write('Unstructured Grid Example\n');
#    vtkFile.write('ASCII\n');
#    vtkFile.write('DATASET UNSTRUCTURED_GRID\n');
#    vtkFile.write("POINTS " + str(nPoint) + " float\n")
#    for iPoint in range(0,nPoint):
#        vtkFile.write(str(x[iPoint]).format('%05.20f') + " " +  str(y[iPoint]).format('%05.20f') + " " + str(z[iPoint]).format('%05.20f') + "\n");    
#    
#    vtkFile.write("CELLS " + str(nPoint) + " " + str(nPoint * 2) + "\n");
#    for iPoint in range(0, nPoint):
#        vtkFile.write("1 " + str(iPoint) + "\n");
#    vtkFile.write("CELL_TYPES " + str(nPoint) + "\n");
#    for iPoint in range(0, nPoint):
#        vtkFile.write("1 \n");
#    #vtkFile.write("\n");
#    vtkFile.write("POINT_DATA " + str(nPoint) + "\n");
#    vtkFile.write('SCALARS scalars float 1\n');
#    vtkFile.write("LOOKUP_TABLE default\n");
#    for iLabel in pointLabels:
#        vtkFile.write(str(int(iLabel)) + " ");
#        #vtkFile.write("1 ")
#    vtkFile.write("\n");
#    vtkFile.close();
#    
#"""
#    
#    
#
#    
#    vtkFile.close();
#"""
## If the labels are not specified for the cells then all are assigned as one
#def writeSparsePointsVTKFile (vtkFileName, pointList):
#    x = pointList[:,1];
#    nPoint = x.size;
#    pointLabels = numpy.ones([nPoint,1], float)
#    writeSparsePointsWithLabelVTKFile (vtkFileName, pointList, pointLabels)
#
#
## sample code of how to use the functions
#vtkFileName = '/Users/kannanuv/Documents/workspace/code/assemblaSVN/idisco/iDISCO/Visualization/test.vtk'
#nPoint = 100;
#pointList = numpy.zeros([nPoint,3], float)
#for iPoint in range(0, nPoint):
#    for iCoord in range(0, 3):
#        pointList[iPoint,iCoord] = random.random() * 10;
#pointList
#pointLabels = numpy.ones([nPoint,1], dtype=numpy.int)
#writeSparsePointsVTKFile (vtkFileName, pointList)




