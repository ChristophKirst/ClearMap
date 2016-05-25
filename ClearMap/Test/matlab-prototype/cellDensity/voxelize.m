%--------------------------------------------------------------------------
% voxelize.m script is used generate voxelized tif file from sparse points
%
%% Developed and maintained by Kannan Umadevi Venkataraju <kannanuv@cshl.edu>
%% do not distribute without permission.
%
% Usage 
% nx=450; minx=0;maxx=450;ny=650;miny=0;maxy=650;nz=300;minz=0;maxz=300;distance=100;fileName = '~/workspace/code/prototype_matlab/data/outputpoints_pointList.mat';
% vox = voxelize (nx, minx, maxx, ny, miny, maxy, nz, minz, maxz, distance, voxelNature, pointListFile)
% voxelNature = 0 for sphere; 1 for cuboid
%---------------------------------------------------------------------------
% History
%---------------------------------------------------------------------------
% Author   | Date         |Change
%==========|==============|=================================================
% kannanuv | 2011 May 01  |Initial Creation
% kannanuv | 2015 Jun 15  |Exposed x, y, z scales
%          |              |Write as 16-bit voxel images for higher range
%---------------------------------------------------------------------------

function vox = voxelize (nx, minx, maxx, xScale, ny, miny, maxy, yScale, nz, minz, maxz, zScale, distance, voxelNature, pointListFile)

if (isdeployed)
    nx = str2double(nx);
    minx = str2double(minx);
    maxx = str2double(maxx);
    xScale = str2double(xScale);
    ny = str2double(ny);
    miny = str2double(miny);
    maxy = str2double(maxy);
    yScale =str2double(yScale);
    nz = str2double(nz);
    minz = str2double(minz);
    maxz = str2double(maxz);
    zScale = str2double(zScale);
    distance = str2double(distance);
    voxelNature = str2double(voxelNature);
else
    addpath ('../utils/');
    addpath ('../cellCounting/');
end

load (pointListFile);
pointList = single (pointList);
tifFileName = [pointListFile(1:end-4) '_voxelImage.tif'];

vox = voxelizeC (nx, minx, maxx, xScale, ny, miny, maxy, yScale, nz, minz, maxz, zScale, distance, pointListFile, tifFileName , voxelNature, pointList(:,1), pointList(:,2), pointList(:,3));
imwritestack (uint16(vox), tifFileName);

elastixFileName = [pointListFile(1:end-4) '_pointList.txt'];
writeElastixPointFile (elastixFileName, pointList');
