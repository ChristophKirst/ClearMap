function zyp05Image = createWarpable(imageDirectory, xInResolution, yInResolution, zInResolution, xOutResolution, yOutResolution, zOutResolution, processingDirectory, datasetPrefix, nThread)

%% Check parameter validity
if (imageDirectory(end) ~= '/')
    imageDirectory = [imageDirectory '/'];
end
if (processingDirectory(end) ~= '/')
    processingDirectory = [processingDirectory '/'];
end

if (isdeployed)
    xInResolution = str2double(xInResolution);
    yInResolution = str2double(yInResolution);
    zInResolution = str2double(zInResolution);
    xOutResolution = str2double(xOutResolution);
    yOutResolution = str2double(yOutResolution);
    zOutResolution = str2double(zOutResolution);
    nThread = str2double (nThread);
else
    addpath ('/home/kannanuv/workspace/code/assemblaSVN/prototype-matlab/src/utils/');
end

listOfImages = dir([imageDirectory '*tif']);
nImage = length(listOfImages);
sagittalImage_p05 = zeros(40);
outputFileName_p05 = [processingDirectory datasetPrefix '_p05.tif'];

matlabpool (nThread)

%% Scaling XY plane
parfor iImage = 1:nImage
    imageFileName = [imageDirectory listOfImages(iImage).name];
    p05imageFileName = [processingDirectory listOfImages(iImage).name(1:end-4) '_p05.tif'];
    fprintf('%s\n', p05imageFileName)
    sagittalImage = imread(imageFileName);
    outputImageSize = ceil([size(sagittalImage,1) size(sagittalImage,2)].*[yInResolution/yOutResolution xInResolution/xOutResolution]);
    sagittalImage_p05 = imresize (sagittalImage, outputImageSize, 'bilinear');
    imwrite (sagittalImage_p05, p05imageFileName);
end

%% Scaling in the Z plane
p05imageFileName = [processingDirectory listOfImages(1).name(1:end-4) '_p05.tif'];
sagittalImage_p05 = imread (p05imageFileName);
xyp05image = zeros(size(sagittalImage_p05,1), size(sagittalImage_p05,2), nImage);
for iImage = 1:nImage
    if (mod(iImage, ceil(nImage/10)) == 0)
        fprintf ('Reading %d/%d\n', iImage, nImage)
    end
    p05imageFileName = [processingDirectory listOfImages(iImage).name(1:end-4) '_p05.tif'];
    xyp05image(:,:,iImage) = imread (p05imageFileName);
end

zyp05Image = permute(xyp05image,[1 3 2]);
resizedZAxisSize = ceil (nImage * zInResolution/zOutResolution);
zyp05ImageResized = zeros (size(zyp05Image,1), resizedZAxisSize, size(zyp05Image,3));

for iImage = 1:size(zyp05Image, 3)
        if (mod(iImage, ceil(size(zyp05Image, 3))) == 0)
        fprintf ('Processing %d/%d\n', iImage, ceil(size(zyp05Image, 3)/10))
    end
    zyp05ImageResized(:,:,iImage) = imresize (zyp05Image(:,:,iImage), [size(zyp05Image,1) resizedZAxisSize]);
end

zyp05Image = permute(zyp05ImageResized, [1 3 2]);

imwritestack (uint16(zyp05Image), outputFileName_p05);
matlabpool close