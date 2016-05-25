function [plotStat, flattenedCortex] = flattenCortex ()

addpath ('/usr/local/netgpu/fluoMouseBrain/scripts/utils/')
%imFlattenCortexLine = imreadstack('ORL_ARA_v2.3_bi_cortexFlattenLines.tif');
% generated using extractCorticalLayers.m
imFlattenCortexLine = imreadstack('/home/kannanuv/workspace/code/cortexFlatten/ORL_ARA_v2.3_bi_rotated_layer_2_right.tif');
imSkeletonizedLine = zeros (size(imFlattenCortexLine));
imVoxelImage = imreadstack ('130806_YK_CM_tFos_OCI_10_raw_ch2_voxelImage.tif');
%imCurve = imread ('testCurve.tif');
showDebug = 0;
plotStat = {};
sectionsOfInterest = 90:195
bregma = [+0.1745 -3.63];
%sectionsOfInterest = 90:95

for iSection = sectionsOfInterest
    fprintf ('Processing %d\n', iSection);
    imCurve = imFlattenCortexLine(:,:,iSection);
    imVoxelSliceImage = imVoxelImage(:,:,iSection);
    imCurveBinary = imCurve > 0;
    if (showDebug)
        imRGB = zeros ([size(imCurve,1) size(imCurve,2) 3]);
    end

    [labelMap nLabels] = bwlabel (imCurveBinary);
    imCurveBinary = bwmorph(imCurveBinary,'dilate');
    imCurveBinary = bwmorph(imCurveBinary,'dilate');
    if (showDebug)
        imRGB(:,:,1) = imCurveBinary * 255;
    end
    imCurveBinary = bwmorph(imCurveBinary,'thin', Inf);
    if (showDebug)
        imRGB(:,:,2) = imCurveBinary * 255;
    end
    imSkeletonizedLine(:,:, iSection) = imCurveBinary;
%     imCurveEndPoints = bwmorph(imCurveBinary,'endpoints');
%     [yEnds, xEnds] = find (imCurveEndPoints);
%     [y, x] = find (imCurveBinary);
%     if (yEnds(1) > yEnds(end))
%         starty = yEnds(end); startx = xEnds(end);
%         endy = yEnds(1); endx = xEnds(1);
%     else
%         starty = yEnds(1); startx = xEnds(1);
%         endy = yEnds(end); endx = xEnds(end);
%     end
%     %imshow (imRGB); hold on;
%     %figure(1); imshow (imCurve); hold on;
%     %plot (startx, starty, 'b*');
%     %plot (endx, endy, 'k*');
%     predictedImageStats = regionprops (imCurveBinary, 'centroid', 'PixelIdxList');
%     curvePixelList = predictedImageStats(1).PixelIdxList;
%     curvePixelsOrdered = [];
% 
%     %% Start walking along the curve
%     yxStart = [starty startx];
%     yxCurve = [y x];
%     xPoint = startx; yPoint = starty;
%     nCurvePixels = size(yxCurve, 1);
%     while (nCurvePixels > 0)
%         %fprintf ('%d Points to go\n', nCurvePixels);
%         [yxNext yxCurve] = getNextCurvePoint(yxStart, yxCurve);
%         curvePixelsOrdered = [curvePixelsOrdered; yxNext];
%         yxStart = yxNext;
%         nCurvePixels = size(yxCurve, 1);
%     end
% 
%     nPixelsInCurve = size(curvePixelsOrdered, 1);
%     cellDensitiesAlongCurve = zeros(nPixelsInCurve, 1);
% 
%     if (showDebug)
%         for iPixel = 1:nPixelsInCurve
%             faceColor1 = [0 (single(iPixel)/single(nPixelsInCurve)) 0];
%             faceColor2 = [(single(nPixelsInCurve - iPixel)/single(nPixelsInCurve)) 0 0];
%             faceColor = faceColor1 + faceColor2;
%             plot (curvePixelsOrdered(iPixel,2), curvePixelsOrdered(iPixel,1), 'o', 'MarkerFaceColor', faceColor, 'MarkerEdgeColor', 'none');
%         end
%         title (sprintf ('Section number = %d', iSection))
%     end
% 
% 
%     for iPixel = 1:nPixelsInCurve
%         cellDensitiesAlongCurve(iPixel) = imVoxelSliceImage(curvePixelsOrdered(iPixel, 1), curvePixelsOrdered(iPixel, 2));
%     end
%     %cellDensitiesAlongCurve = repmat (cellDensitiesAlongCurve, [1 100]);
%     %figure(2); imagesc(cellDensitiesAlongCurve); axis equal; colorbar;
%     plotStat{iSection}.curvePixelsOrdered = curvePixelsOrdered;
%     plotStat{iSection}.cellDensitiesAlongCurve = cellDensitiesAlongCurve;
%     %pause;
end

maxLength = 0;
for iSection = sectionsOfInterest
    maxLength = max([maxLength size(cellDensitiesAlongCurve,1)]);
end
flattenedCortex = zeros (size(sectionsOfInterest,2), maxLength);

for iSection = 1:length(sectionsOfInterest)
    flattenedCortex(iSection, 1:length(plotStat{sectionsOfInterest(iSection)}.cellDensitiesAlongCurve)) = plotStat{sectionsOfInterest(iSection)}.cellDensitiesAlongCurve;
end

h = imagesc (flattenedCortex); colorbar;
saveas (h, 'flattenedCortex_130806_YK_CM_tFos.pdf');

function [yxNext yxCurve] = getNextCurvePoint(yxStart, yxCurve)
yxStart = repmat (yxStart, [size(yxCurve,1) 1]);
distance = sum ((yxStart - yxCurve).^2, 2);
[minValue minIndex] = min (distance);
yxNext = yxCurve(minIndex, :);
yxCurve(minIndex, :) = [];

    % predictedCentroidList = [predictedImageStats.Centroid];
    % predictedCentroidList = reshape(predictedCentroidList, [2 length(predictedCentroidList)/2]);
    % imshow (imCurve); hold on;
    % plot (predictedCentroidList(1), predictedCentroidList(2), 'r*'); hold on;
    % [y x] = find(imCurveBinary);
    % nPixelsInCurve = length(predictedImageStats(1).PixelIdxList);
    % % for iPixel = 1:nPixelsInCurve
    % %     slope(iPixel) = atan(y(iPixel) - predictedCentroidList(2))/(x(iPixel) - predictedCentroidList(1));
    % % end
    % % [sortedSlope index] = sort(slope);
    % % x = x(index); y = y(index);
    % 
