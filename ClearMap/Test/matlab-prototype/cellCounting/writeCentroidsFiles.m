%--------------------------------------------------------------------------
% writeCentroidsFiles.m script is used write centroid files for elastix and
% visualization
%
%% Developed and maintained by Kannan Umadevi Venkataraju <kannanuv@cshl.edu>
%% do not distribute without permission.
%
% Usage 
% writeCentroidsFiles(cleanupDirectory, stitchedImageDirectory, fileName, doDetectCircles, doWriteCentroidImage, areaSize, nThreads)
% 
% History
% Author   | Date         |Change
%==========|==============|=================================================
% kannanuv | 2012 May 01  |Initial Creation
% kannanuv | 2013 Jly 16  |Parallelize write centroids to detect centroids
%          |              |parallely section-wise
% kannanuv | 2013 Jly 16  |Ability to specify number of threads since it is
%          |              |memory intensive
% kannanuv | 2013 Aug 08  |Added feature get mean intensity of the nuclei
% kannanuv | 2013 Aug 09  |Added scaling of centroid to real world co-ordinates for visualization
% kannanuv | 2013 Aug 23  |Added placeholder to get mean intensity of the nuclei with cell separation
% kannanuv | 2013 Sep 20  |Handle condition when no cells are detected in a section
% kannanuv | 2013 Sep 20  |write overlay files in centroids directory
% kannanuv | 2013 Oct 11  |Change image origin to (0,0) from (1,1) for vtk and elastix
% kannanuv | 2013 Dec 17  |Adding backward compatibility to old pipeline by
%                         |having additional area size filtering at write centroids
%--------------------------------------------------------------------------
function writeCentroidsFiles(cleanupDirectory, stitchedImageDirectory, fileName, doDetectCircles, doWriteCentroidImage, areaSize, xSpacing, ySpacing, zSpacing, nThreads, labelFileName)

if (isdeployed)
    doDetectCircles = str2double (doDetectCircles);
    doWriteCentroidImage = str2double (doWriteCentroidImage);
    areaSize = str2double (areaSize);
    nThreads = str2double (nThreads);
    xSpacing = str2double (xSpacing);
    ySpacing = str2double (ySpacing);
    zSpacing = str2double (zSpacing);
end

%% Read the images and get centroids
listOfFiles = dir ([cleanupDirectory '*tif']);
nCentroid = 0;
elastixScalingFactor = [0.05 0.05 1];
visualizationScalingFactor = [xSpacing ySpacing zSpacing] * 1e-3; %millimeter units in mha
imageSize = [13000 9000];
processingDir = cleanupDirectory;
mkdir (processingDir, 'centroids');
centroidsDirectory = [processingDir 'centroids/'];
vtkFileName = strcat (centroidsDirectory, fileName, '.vtk');
dataFileName = strcat (centroidsDirectory, fileName, '.mat');
elastixFileName = strcat (centroidsDirectory, fileName, '_elastix.txt');

if (nThreads > 1)
    matlabpool (nThreads)
end

%parfor iFile = 1:length(listOfFiles)
%for iFile = length(listOfFiles):-1:1
for iFile = 1:length(listOfFiles)
  isCleanedUpFile = ~isempty(findstr(listOfFiles(iFile).name, 'cleanup')) & isempty(findstr(listOfFiles(iFile).name, 'cleanup1'));
  if (isCleanedUpFile)
    fprintf ('Getting Centroids in image %s ...\n', listOfFiles(iFile).name)
    stitchedFileName = [stitchedImageDirectory listOfFiles(iFile).name(1:end-12) '.tif'];
    cleanupFileName = [cleanupDirectory listOfFiles(iFile).name];
    imCleanup = imread (cleanupFileName);
    imCleanup = removeSmallRegions ((imCleanup > 0), areaSize-1);
    imStitched = imread (stitchedFileName);
    im = imCleanup;
    predictionImageSize = size(im);
    imCleanupPadded = padarray (im, [(imageSize(1)-size(im,1)) (imageSize(2)-size(im,2))], 0, 'post');
    imStitchedPadded = padarray (imStitched, [(imageSize(1)-size(im,1)) (imageSize(2)-size(im,2))], 0, 'post');
    imBinary = (imCleanupPadded > 0.5);
    [imLabel, nLabel] = bwlabel (imBinary, 8);
    

    if (doDetectCircles == 0)    
        predictedImageStats = regionprops (imBinary, imStitchedPadded, 'centroid', 'Mean');
        predictedMeanIntensityList = [predictedImageStats.MeanIntensity];
        predictedCentroidList = [predictedImageStats.Centroid];
        predictedCentroidList = reshape(predictedCentroidList, [2 length(predictedCentroidList)/2]);
    else
        warning off;
        [predictedCentroidList r m] = imfindcircles (imBinary, [1 15]);
        warning on;
        predictedCentroidList = predictedCentroidList';
        % Mean intensity has to be calculated
        predictedMeanIntensityList = ones (size(predictedCentroidList,2), 1);
    end
    predictedCentroidList = predictedCentroidList - 1;
    
    if (doWriteCentroidImage == 1)
        imCentroids = zeros (size(imCleanup));
        predictedCentroidList = uint16 (predictedCentroidList);
        for i=1:size(predictedCentroidList,2)
            imCentroids(predictedCentroidList(2,i), predictedCentroidList(1,i)) = 1; 
        end
        imOverlay = zeros (size(imCleanup,1), size(imCleanup,2), 3);
        imOverlay(:,:,1) = ~imdilate(imCentroids, ones(4)) & imCleanup;
        imOverlay(:,:,2) = imdilate(imCentroids, ones(4));
        imOverlay(:,:,3) = 0;
        imwrite (uint8 (imOverlay) * 255, [centroidsDirectory listOfFiles(iFile).name(1:end-4) '_centroids.tif'], 'compress', 'lzw')
    end
    
    zCoords = ((iFile - 1) * [ones(size(predictedCentroidList,2),1)]);
	centroidList = [predictedCentroidList' zCoords];
    if (size (centroidList,1) == 0)
        centroidList = zeros(0,3);
    end

    elastixCentroidList = double (centroidList) .* repmat (elastixScalingFactor, [size(predictedCentroidList,2) 1]);
    visualizationCentroidList = double (centroidList) .* repmat (visualizationScalingFactor, [size(predictedCentroidList,2) 1]);
    centroids(iFile).centroidList = elastixCentroidList;
    centroids(iFile).visualizationCentroidList = visualizationCentroidList;
    centroids(iFile).MeanIntensity = predictedMeanIntensityList;
    centroidCount(iFile) = size(centroidList,1);
    fprintf ('Number of c-fos centers in %s = %d\n', listOfFiles(iFile).name, size(centroidList,1))
  else
    fprintf (' %s is not proper cleanup image file\n', listOfFiles(iFile).name)
  end
end

%% Save in cell format for downstream applications
for iSlice = 1:size (centroids, 2)
    centroidsCell{iSlice, 1} = centroids(iSlice).centroidList;
    visualizationCentroidsCell{iSlice, 1} = centroids(iSlice).visualizationCentroidList;
    centroidCountCell{iSlice} = centroidCount(iSlice);
    meanIntensity{iSlice} = centroids(iSlice).MeanIntensity;
end

elastixPointList = [];
visualizationPointList = [];
for iSection = 1:size(centroids,2)
    elastixPointList = [elastixPointList;centroids(iSection).centroidList]; 
    visualizationPointList = [visualizationPointList ;centroids(iSection).visualizationCentroidList];
end
elastixPointList = elastixPointList';
visualizationPointList = visualizationPointList';
writeSparsePointsVTKFile (vtkFileName, visualizationPointList, labelFileName);
writeElastixPointFile (elastixFileName, elastixPointList);

centroids = centroidsCell;
visualizationCentroids = visualizationCentroidsCell;
centroidCount = centroidCountCell;
save (dataFileName, 'centroidCount', 'centroids', 'meanIntensity', 'visualizationCentroids');

if (nThreads > 1)
    matlabpool close;
end
