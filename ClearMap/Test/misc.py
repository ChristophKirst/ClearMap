# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 14:00:49 2015

@author: ckirst
"""

    











# open data

#mount windows folder 
#sudo mount -t vboxsf D_DRIVE ./Windows/

#fn = '/home/ckirst/Science/Projects/BrainActivityMap/Data/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims';
#fn = '/run/media/ckirst/ChristophsBackuk4TB/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims';
#fn = '/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 - Copy.ims';
fn = '/media/mtllab/6C9C07289C06EC80/Users/Nicolas/My Documents/Adult cfos C row 20HF 150524 - Copy.ims';

#fn = '/home/ckirst/Science/Projects/BrainActivityMap/iDISCO_2015_04/test for spots added spot.ims'


#fout =  '/media/mtllab/6C9C07289C06EC80/Users/Nicolas/Documents/Adult cfos C row 20HF 150524 Points.cent';
#fouti = '/media/mtllab/6C9C07289C06EC80/Users/Nicolas/Documents/Adult cfos C row 20HF 150524 Points.int';
#fout = '/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 Points.cent';
fouti = '/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 Points.int';
fout = '/home/ckirst/Desktop/cfosRegistrations/Adult cfos C row 20HF 150524 Points.data';
centers.tofile(fout);
centint.tofile(fouti);






#!/usr/bin/env python
#import numpy as np
#import pylab as P
# the histogram of the data with histtype='step'
#n, bins, patches = P.hist(centint, 50, normed=1, histtype='stepfilled')
#P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)

# add a line showing the expected distribution
#y = P.normpdf( bins, mu, sigma)
#l = P.plot(bins, y, 'k--', linewidth=1.5)


# write resultf.close();

centers = np.fromfile(fout)
centers = centers.reshape(centers.shape[0] / 3, 3);

centint = np.fromfile(fouti);

c = centers.copy();
c = c[:, [2,1,0]];
 
#c = numpy.array([[0,0,0], [2176,  2560, 1920]])
#(1920, 2560, 2176600)

#working version without tranposing imaris data
#c[:,0] = c[:,0] * 4.0625;
#c[:,1] = c[:,1] * 4.0625;
#c[:,2] = c[:,2] * 3; # 4.0625;

c[:,2] = c[:,2] * 4.0625;
c[:,1] = c[:,1] * 4.0625;
c[:,0] = c[:,0] * 3; # 4.0625;


#iid = np.logical_and(c[:,2] > 2000, c[:,2]  < 3000);
#iid2 = np.logical_and(c[:,1] > 2000, c[:,1]  < 3000);
#iid = np.logical_and(iid, iid2);
#c2 = c[iid, :];t


iid = centint > 30;
c2 = c[iid,:];




#fout = '/home/ckirst/Science/Projects/BrainActivityMap/Data/iDISCO_2015_06/Adult cfos C row 20HF 150524 segmentation.ims';
fout = fn; #'/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 - Copy.ims';
h5file = io.openFile(fout);

io.writePoints(h5file, c2, mode = 'o', radius = 0.5);

h5file.close();










""" Open Data """

import iDISCO.IO.Imaris as io
import numpy as np

#fn = '/home/ckirst/Science/Projects/BrainActivityMap/Data/iDISCO_2015_06/Adult cfos C row 20HF 150524.ims';
fn = '/home/nicolas/Windows/Nico/cfosRegistrations/Adult cfos C row 20HF 150524 - Copy.ims';


f = io.openFile(fn);
dataset = io.readData(f, resolution=0);
print dataset.shape

#dataraw = dataset[1200:1600,1200:1600,1000:1160];
#print dataraw.dtype
#print (dataraw.max(), dataraw.min())
#datamax = np.iinfo(dataraw.dtype).max;

#img = dataset[0:500,0:500,1000:1008];
img = dataset[600:1000,1600:1800,800:830];
img = dataset[:,:,800:809];


#plotTiling(10 * img)
#f.close();


cc = centers.astype('int');
cc = cc[cc[:,2] < 809, :];
#cc = cc[cc[:,0] < 500, :];
#cc = cc[cc[:,1] < 500, :];



for i in range(cc.shape[0]):
    imgc[cc[i,0], cc[i,1], cc[i,2]-800] = 1;
    
    
img = img.astype('float');
img /= img.max();
img[img > 0.5] = 0.5;


cintensity = numpy.array([img[cc[i,0], cc[i,1], cc[i,2]-800] for i in range(cc.shape[0])]);
print (cintensity.min(), cintensity.max())

imgc = numpy.zeros(img.shape)
for i in range(cc.shape[0]):
    if cintensity[i] > 0.05:
        imgc[cc[i,0], cc[i,1], cc[i,2]-800] = 1;
      
plotOverlayLabel(img * 5, imgc)


"""
Test between openings for speed

"""

import numpy
from mahotas import open
from scipy.ndimage.morphology import binary_opening, grey_opening
from skimage.morphology import opening, white_tophat
from skimage.filters.rank import tophat
import cv2

from iDISCO.ImageProcessing.Filter.StructureElement import structureElement
from iDISCO.Visualization.Plot import plotTiling, plotOverlayLabel

from iDISCO.Utils.Timer import Timer;


img = numpy.random.rand(2000,2000) * 65535;
img = img.astype('int')

dataraw = dataset[:,:,1160];

img = dataraw[:,:];
img.shape


t = Timer();
res = grey_opening(img,#DoG filter
t.printElapsedTime('scipy');


#t.reset();
#res2 = open(img, structureElement('Disk', (30,30)).astype('bool'));
#t.printElapsedTime('mahotas');

#t.reset();
#res2 = open(img, structureElement('Disk', (30,30)).astype('bool'));
#t.printElapsedTime('mahotas');

t.reset();
se = structureElement('Disk', (15,15)).astype('uint8');
res2 = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
t.printElapsedTime('opencv');

#from skimage.morphology import disk
#se = disk(10);

t.reset();
#res3 = opening(img.astype('uint16'), se);
res3 = white_tophat(img.astype('uint16'), se);

t.printElapsedTime('skimage');
t.reset();

x = (res3);
print (x.min(), x.max())

plotTiling(numpy.dstack((10 * img, 10 * (img - res2))))

#seems not to work correctly -> scipy gets very slow for larger images (??)




"""
Test Speed of Correlation
"""


import scipy
from iDISCO.ImageProcessing.Filter.FilterKernel import filterKernel

from skimage.feature import match_template

from iDISCO.Utils.Timer import Timer;

timer = Timer();

#DoG filter
fdog = filterKernel(ftype = 'DoG', size = [7,7,5]);
img = dataset[:,:,1000:1016];

#timer.reset();
#res = scipy.signal.correlate(img, fdog);
#timer.printElapsedTime(head = 'scipy.signal');


#res = match_template(img, fdog);
#timer.printElapsedTime(head = 'skimage');

timer.reset();
res2 = scipy.ndimage.filters.correlate(img, fdog);
timer.printElapsedTime(head = 'scipy.ndimage');




dsname = "DataSetInfo/OME Image Tags"
ds = f.get(dsname)
























"""

import iDISCO.IO.Imaris as io


from multiprocessing import Pool


# test parallel reading of h5py file

def readD(fnz):
    fn = fnz[0];
    z = fnz[1];
    f = io.openFile(fn, mode = 'r');
    dataset = io.readData(f, resolution=0);    
    
    img = dataset[120:130,120:200,z];
    
    f.close();
    
    return img;
    
    
fn = '/home/ckirst/Science/Projects/BrainActivityMap/iDISCO_2015_04/test for spots added spot.ims'


argdata = [(fn,x) for x in range(50)];
pool = Pool(processes = 4);

results = pool.map(readD, argdata);
print results


"""






