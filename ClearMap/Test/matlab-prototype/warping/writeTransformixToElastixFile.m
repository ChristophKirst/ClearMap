function writeTransformixToElastixFile (inputFileName, zSpacing, labelFileName)

if (~isdeployed)
    addpath ('../cellCounting/');
else
    zSpacing = str2double(zSpacing);
end

elastixScalingFactor = [0.05 0.05 1];
visualizationSpacingFactor = [1 1 zSpacing] * 1e-3; %millimeter units in mha

fp = fopen (inputFileName);
C = textscan (fp, 'Point	%d	; InputIndex = [ %d %d %d ]	; InputPoint = [ %f %f %f ]	; OutputIndexFixed = [ %d %d %d ]	; OutputPoint = [ %f %f %f ]	; Deformation = [ %f %f %f ]');
pointList = cell2mat(C(11:13));
warpableFileName = sprintf ('%s_elastix_warpable_pointList.txt', inputFileName(1:end-4));
vtkFileName = sprintf ('%s_pointList.vtk', inputFileName(1:end-4));
matFileName = sprintf ('%s_pointList.mat', inputFileName(1:end-4));

visualizationCentroidList = double (pointList) .* repmat (visualizationSpacingFactor./elastixScalingFactor , [size(pointList,1) 1]);

writeElastixPointFile (warpableFileName, pointList');
writeSparsePointsVTKFile (vtkFileName, visualizationCentroidList', labelFileName);
save (matFileName, 'pointList', 'visualizationCentroidList');
