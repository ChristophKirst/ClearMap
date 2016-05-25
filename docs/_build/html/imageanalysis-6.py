import os
import ClearMap.Settings as settings
filename = os.path.join(settings.ClearMapPath, 'Test/Data/ImageAnalysis/cfos-substack.tif');
import ClearMap.Visualization.Plot as plt
import ClearMap.IO as io
data = io.readData(filename, z = (0,26));
import ClearMap.ImageProcessing.BackgroundRemoval as bgr
dataBGR = bgr.removeBackground(data.astype('float'), size=(10,10), verbose = True);
from ClearMap.ImageProcessing.Filter.DoGFilter import filterDoG
dataDoG = filterDoG(dataBGR, size=(8,8,4), verbose = True);
plt.plotTiling(dataDoG, inverse = True, z = (10,16));