%--------------------------------------------------------------------------
% writeSparsePointsVTKFile.m script is used generate VTK file of sparse point lists
%
%% Developed and maintained by Kannan Umadevi Venkataraju <kannanuv@cshl.edu>
%% do not distribute without permission.
%
% Usage 
% [labelMap pointLabels] = writeSparsePointsVTKFile (vtkFileName, pointList, varargin)
% vtkFileName - name of the vtk File to be written
% pointList   - an array of x y z co-ordinate values of nucleus centroids
% varargin{1} - Label image of the segmented brain image
% varargin{2} - specific label value
%---------------------------------------------------------------------------
% History
%---------------------------------------------------------------------------
% Author   | Date         |Change
%==========|==============|=================================================
% kannanuv | 2011 May 01  |Initial Creation
% kannanuv | 2013 Aug 09  |Improved precision of world co-ordinates for visualization in 
%          |              | millimeters
% kannanuv | 2013 Nov 08  |Fixed xy axis switching
%---------------------------------------------------------------------------
function [labelMap pointLabels] = writeSparsePointsVTKFile (vtkFileName, pointList, varargin)

labelMap = {};
%henkelmanMap; uncomment this if you need henkelman label values
if (~isdeployed)
    addpath ('/usr/local/netgpu/fluoMouseBrain/scripts/utils/');
end

nPoint = size (pointList, 2);

if (numel(varargin) >= 1)
    labelImageFileName = varargin{1};
    labelImage = imreadstack (labelImageFileName);
    sprintf ('Finding labels\n')
    pointLabels = interp3 (labelImage, pointList(1,:), pointList(2,:) , pointList(3,:), 'nearest');
else
    pointLabels = ones (nPoint, 1);
end

if (numel(varargin) >= 2)
    labelList = varargin{2};
    labelIndices = ismember (pointLabels, labelList);
    pointList = pointList (:, labelIndices);
    pointLabels = pointLabels(labelIndices);
end

nPoint = size (pointList, 2);

%%Swap x and y axis
pointListx = pointList(2,:);
pointListy = pointList(1,:);
pointList(1,:) = pointListx;
pointList(2,:) = pointListy;

%% Write VTK File
fp = fopen (vtkFileName, 'w+');
fprintf (fp, '# vtk DataFile Version 2.0\n');
fprintf (fp, 'Unstructured Grid Example\n');
fprintf (fp, 'ASCII\n');
fprintf (fp, 'DATASET UNSTRUCTURED_GRID\n');
fprintf (fp, 'POINTS %d float\n', nPoint);
fprintf (fp, '%05.20f %5.20f %5.20f\n', pointList);
fprintf (fp, 'CELLS %d %d\n',nPoint, nPoint * 2);
fprintf (fp, '%d %d\n', [ones(nPoint, 1) [0:nPoint-1]']');
fprintf (fp, 'CELL_TYPES %d\n', nPoint);
fprintf (fp, '%d\n', ones (nPoint, 1));
fprintf (fp, 'POINT_DATA %d\n',nPoint);
fprintf (fp, 'SCALARS scalars float 1\n');
fprintf (fp, 'LOOKUP_TABLE default\n');
fprintf (fp, '%f ', pointLabels);
fclose (fp);
