function label = syntheticLabeledImage(isize, nlabel, objsize)
%
% label = syntheticLabeledImage(size, nlabel. objsize)
%
% description:
%     generates a test labeled image
%

label = zeros(isize);
dim = length(isize);

if nargin < 3
   objsize = 10 * ones(1, dim);
else
   objsize = padright(objsize, dim, 'circular');
end

if dim == 2
   for i = 1:nlabel
      wh = round(objsize .* rand(1,2) + 2);
      xy = round((isize-1 + 2 * wh) .* rand(1,2) + 1 - wh);
      
      obj = fspecial2('disk', wh, 0);
      idx = imind2sub(size(obj), find(obj));
      idx = idx + repmat(xy, size(idx,1), 1);
      maxsi = repmat(isize, size(idx,1), 1);
      minsi = ones(size(idx, 1), 3);
      ii = or(idx > maxsi, idx < minsi);
      ii = ~any(ii, 2);
      idx = idx(ii, :);
      idx = imsub2ind(isize, idx);
      label(idx) = i;
      
      %label = label + imreplace(zeros(isize), fspecial2('disk', wh, 0) > 0, xy, 'chop', true);
   end
elseif dim == 3
   for i = 1:nlabel
      wh = round(objsize .* rand(1,3) + 2);
      xy = round((isize-1 + 2 * wh) .* rand(1,3) + 1 - wh);
   
      obj = fspecial3('disk', wh, 0);
      idx = imind2sub(size(obj), find(obj));
      idx = idx + repmat(xy, size(idx,1), 1);
      maxsi = repmat(isize, size(idx,1), 1);
      minsi = ones(size(idx, 1), 3);
      ii = or(idx > maxsi, idx < minsi);
      ii = ~any(ii, 2);
      idx = idx(ii, :);
      idx = imsub2ind(isize, idx);
      label(idx) = i;
      
      %label = label + imreplace(zeros(isize), fspecial3('disk', wh, 0) > 0, xy, 'chop', true);
   end
else
   error('syntheticLabeledImage: image expected to be 2 or 3d, found: %g!', length(isize));
end

%label = bwlabeln(label > 0);

end

      