Ilastik Interface
=================


Ilastik Installation
--------------------

- install ilastik version 0.5 from

https://github.com/ilastik/ilastik-0.5/archive/v0.5.12.tar.gz

overwrite files from
./Interface/Ilastik/Ilastik
to
PATH_TO_ILASTIK_0.5/modules/classification/core/classifiers/


Vigra Installation
------------------

- install vigra / vigranumpy


under linux:

download vigra from:

http://ukoethe.github.io/vigra/doc-release/vigra/Installation.html

cmake -DLIB_SUFFIX=64
make 
make install

check ldconfig / /etc/ld.so.conf to make sure /usr/local/lib64 is in the library path


h5py Installation
------------------

* install h5py

  under linux:
  download repository
  
* matlab uses its own outdata version lighdf5.so.6
  to make h5py in matlab 2014b work:

* locate libhdf5.so.XXX typically in /usr/lib64

* relink 
  /usr/local/MATLAB/R2014b/sys/os/glnxa64/libhdf5.so.6 
  to the libhdf5.so.XXX, e.g.
  /usr/lib64/libhdf5.so.8

  and
  libhdf5_hl.so.6 
  to 
  /usr/lib64/libhdf5_hl.so.8



Ilastik under Matlab
--------------------

    initialize
    ilinitialize

then use

    ilclassify

see

    ./Interface/Ilastik/Test/testIlastik.m

for exmaples










Install Illastik on MAC
-----------------------

xcode
mac ports
apple command line developer tools

via app store

get administrator root rights / enable root user (if not done)

run 

su 

on terminal to login as root

run

port selfupdate

port select --set python python27

port install py27-pyqt4
port install py27-h5py
port install boost +python27
port install vigra +numpy
port install py27-scipy

overwrite the ilastik python files classifierXXX.py in the ilastik 0.5 source
delte corresponding .pyo files

run ilastik 0.5 directly once to recompile the modules


to run ijn terminal to start matlab

export DYLD_INSERT_LIBRARIES=/opt/local/lib/libtiff.5.dylib
export PYTHONPATH=/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python27.zip:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/plat-darwin:/opt/local/Library/Frameworks/:/Versions/2.7/lib/python2.7/plat-mac:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/plat-mac/lib-scriptpackages:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-tk:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-old:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/readline:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/lib-dynload:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/site-packages/PyObjC:/Library/Python/2.7/site-packages
/Applications/MATLAB_R2013b.app/bin/matlab


then

ilinitialize

and use test script to test


notes
-----

python version s under mac are at various places, so be sure to use correct one
that finds vigra, also tell matlab to use the correct python version







