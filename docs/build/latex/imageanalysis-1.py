import os
import ClearMap.Settings as settings
filename = os.path.join(settings.ClearMapPath, 'Test/Data/ImageAnalysis/cfos-substack.tif');
import ClearMap.Visualization.Plot as plt
import ClearMap.IO as io
data = io.readData(filename, z = (0,26));
plt.plotTiling(data);