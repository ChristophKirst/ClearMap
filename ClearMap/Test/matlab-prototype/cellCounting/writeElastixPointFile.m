h%--------------------------------------------------------------------------
% writeElastixPointFile.m script is used generate elastix file of sparse point lists as input for transformix
%
%% Developed and maintained by Kannan Umadevi Venkataraju <kannanuv@cshl.edu>
%% do not distribute without permission.
%
% Usage 
% writeElastixPointFile (elastixFileName, pointList)
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
%---------------------------------------------------------------------------
function writeElastixPointFile (elastixFileName, pointList)

%% Write elastix point list file
nPoints = size (pointList, 2);
fp = fopen (elastixFileName, 'w+');
fprintf (fp, 'point\n');
fprintf (fp, '%d\n', nPoints);
fprintf (fp, '%05.4f %5.4f %5.4f\n', pointList);
fclose (fp);
