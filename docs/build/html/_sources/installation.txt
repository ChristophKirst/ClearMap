Installation
============

Requirements
^^^^^^^^^^^^

ClearMap is written in Python 2.7. It should run on any Python environment, but it also relies on external softwares such as `Elastix <http://elastix.isi.uu.nl>`_ which may not run optimally on Windows or Apple systems.
For typical use, we recommend a workstation running Ubuntu 14 or later with at least 4 CPU cores, 64Gb of RAM and SSD disks. 128Gb of RAM and 6 cores or above will have much increased performances. The processing time however will depend greatly on the parameters set, so your experience may be different. Also, large hard drives may be needed to host the raw data, although 1 to 4Tb of storage space should be enough for most users.

Installation
^^^^^^^^^^^^

To install ClearMap, first create a folder to contain all the files for the program. Download the scripts from the latest version of ClearMap from `The iDISCO website <https://www.idisco.info>`_ and extract them in the ClearMap folder. You also need to download individually the following softwares:

  * To do the alignement, you should download `Elastix <http://elastix.isi.uu.nl>`_ (http://elastix.isi.uu.nl)

  * If you wish to use the machine learning filters, download `Ilastik <http://ilastik.org>`_ (http://ilastik.org). This is an optional download, only if you wish to use this more complete object detection framework for complex objects.

If you’re starting from a fresh Ubuntu 16.04LTS install, for instance, here are the steps to complete the installation. Open a terminal window and type the following instructions:

- Installation tools:
.. code-block:: bash
    
    $ sudo apt-get update
    $ sudo apt-get install git
    $ sudo apt-get install python-pip
    $ sudo -H pip install --upgrade pip

- Download ClearMap:
.. code-block:: bash
    
    $ git clone https://github.com/ChristophKirst/ClearMap.git


- Install Spyder:
.. code-block:: bash

    $ sudo apt-get install spyder

- Install the necessary libraries:
.. code-block:: bash

    $ sudo apt-get install python-opencv
    $ sudo apt-get install cython
    $ sudo apt-get install python-tifffile
    $ sudo apt-get install python-h5py
    $ sudo apt-get install python-natsort
    $ sudo -H pip install scikit-image
   
We use `Spyder <https://pythonhosted.org/spyder/>`_ to run the code. Set the project explorer and working environment in the ClearMap folder.

Configuration
^^^^^^^^^^^^^

Open the file ``ClearMap/Settings.py`` to set the paths of installations for Ilastik and Elastix:

    >>> IlastikPath = '/yourpath/ilastik';
    >>> ElastixPath = '/yourpath/elastix';

Note that Ilastik is optional. If you haven’t installed it, you can set the path to ``None``. You can also set the installation to run on multiple machines by setting a host specific path:

    >>> if hostname == 'kagalaska.nld':  #Christoph’s Laptop 
    >>>     IlastikPath = '/home/ckirst/programs/ilastik/';
    >>>     ElastixPath = '/home/ckirst/programs/elastix/';
    >>> elif hostname == 'mtllab-Ubuntu': #Nico’s Workstation
    >>>     IlastikPath = '/usr/local/ilastik';
    >>>     ElastixPath = '/usr/local/elastix';       

Additionnal Informations:
^^^^^^^^^^^^^^^^^^^^^^^^^
We run ClearMap on Ubuntu 16.04LTS using the following libraries:

- Matplotlib 1.5.1
- Numpy 1.11.0
- Scipy 0.16.0
- Skimage 0.12.3
- Mahotas 1.3.0 (`website <http://luispedro.org/software/mahotas/>`_)
- h5py 2.6.0 (for Imaris files input/output only)
- openCV 2.4.9.1
- PyQt4
- tifffile 0.6.2
- Cython 0.23.1


