%labelFileName = '/home/kannanuv/workspace/code/HeadLight//data/ORL_ARA_v2.3_bi_rotated.tif';
%matchingSting = 'layer 1';
function imLabel = extractCorticalLayers(labelImageFile, matchingString)

addpath ('/usr/local/netgpu/fluoMouseBrain/scripts/utils/');
imLabel = imreadstack(labelImageFile);

%% Get sub-region list
addpath('/home/kannanuv/workspace/code/netgpu/fluoMouseBrain/scripts/warping/');
[regionIDList region] = readAllenRegionAnnotationFile();
regionNameMatchingIDList = getMatchingRegionNamesByID (regionIDList, region, matchingString);

imLabel = ismember (imLabel, regionNameMatchingIDList);
imwritestack (uint8(imLabel*255), [labelImageFile(1:end-4) '_' matchingString '.tif']);


function regionNameMatchingIDList = getMatchingRegionNamesByID (regionIDList, region, matchingString)

regionNameMatchingIDList= [];
for iRegion = 1:length(regionIDList)
    regionName = region(regionIDList(iRegion)).name;
    matchStr = regexp(regionName, matchingString,'ignorecase');
    if (~isempty(matchStr))
        regionNameMatchingIDList = [regionNameMatchingIDList; regionIDList(iRegion)];
        fprintf ('Adding region === %s\n',  regionName);
    else
        %fprintf ('Not adding region === %s\n',  regionName);
    end
end