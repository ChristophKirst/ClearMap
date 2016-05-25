

fname = '/home/ckirst/test_iDISCO_<Z,3>.tif';

dat = syntheticConfocalData();
dat = 5 * dat;

max(dat(:))

bd = 3;
dat(1:bd, :, :) = 0;
dat(end-bd:end, :, : ) = 0;

dat(:, 1:bd, :) = 0;
dat(:, end-bd:end, :) = 0;

dat(:, :, 1:bd) = 0;
dat(:, :, end-bd:end) = 0;

max(dat(:))

isize = size(dat);

g = 5 * [0.05, 0.01, 0.02]
for z = 1:isize(3)
   for x = 1:isize(1)
      for y = 1:isize(2)
         dat(x,y,z) = dat(x,y,z) + g * [x,y,z]';
      end
   end
end

dat = uint16(dat);

for z = 1:isize(3)
   imwrite(dat(:,:,z), tagExpressionToString(fname, 'Z', z), 'WriteMode', 'overwrite');
end

