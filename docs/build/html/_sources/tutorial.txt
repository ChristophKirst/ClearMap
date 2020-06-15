Tutorial
========

The goal of this tutorial is to explain the scripts we used to analyze samples. As an example, we will use a dataset from a Light Sheet imaged adult mouse brain stained for c-fos. The tutorial files also contain an autofluorescence file to enable the registration of the scan to the reference atlas. The tutorial files are found in the ClearMap/Scripts folder. They consist of :

   * `The Parameter File`_ This sets the parameters individually for each sample
   * `The Run File`_ This will run all the commands to process each sample individually
   * `Analysis Tools`_ This scripts will run the analysis tools and group statistics for all samples in the batch

A project will usually contain 1 parameter file for each sample, 1 run file for the whole experiment and 1 analysis file for the whole experiment.
      
The Parameter File
------------------

The parameter is a Python script that will contain all the necessary informations to process each sample. An example script, *parameter_file_template.py* is provided in the ClearMap/Scripts folder. Open this file to follow closely the tutorial. It contains the following sections:

====================== ===============================================================================
Section                Description
====================== ===============================================================================
`Import modules`_      load from ClearMap the functions used here
`Data parameters`_     points to the files used, their resolution and orientation
`Cell detection`_      parameters for the cell detection, and module used
`Heat map generation`_ to generate a voxelized map of the detected cells
`Config Parameters`_   the parameters for memory and processors management
`Run Parameters`_      you would usually not change these. They specify how the data will be processed
====================== ===============================================================================

`Import Modules`
^^^^^^^^^^^^^^^^
You would usually not change these. They are all the functions that will be used later either in the parameter file or in the  execution file.

`Data parameters`
^^^^^^^^^^^^^^^^^

This is where you point to the files used, their resolution and orientation. It also defines which atlas and annotation files to use.

To set the directory where all files will be read and written for this sample:

    >>> BaseDirectory = '/home/mtllab/pharmaco/sample1';

To set the image files used for the processing:

    >>> cFosFile = os.path.join(BaseDirectory, 'cfos/0_8x-cfos-Table Z\d{4}.ome.tif');
    >>> AutofluoFile = os.path.join(BaseDirectory, \
    >>>                             'autofluo/0_8xs3-autofluo-Table Z\d{4}.ome.tif');

Note the use of the command ``os.path.join`` to link the set ``BaseDirectory`` with the folder where the files are. On the LaVision ultramicroscope system, the images files are generated not as stacks, but as numbered files in the ome.tif format. Each Z stack will end by ``-Table Z0000.ome.tif``. The 0000 is the plane number. To indicate **ClearMap** to read the next planes, replace the 4 digits with the command ``\d{4}``. On our system, files for each channel (here, c-fos and background fluorescence) are saved in a different stack, in a different folder.

To restrict the range for the object detection:

    >>> cFosFileRange = {'x' : all, 'y' : (180, 2600), 'z' : all};

This range will only affect the region used for the cell detection. It will not be taken into account for the 3D image registration to the reference Atlas, nor for the voxelization or other analysis. This is useful to limit the amount of memory used. In our example, we use the full x range, the full z range, but restrict the y range. The camera on our system, an Andor sNEO CMOS, has a sensor size of 2160 x 2660. However, the lens used on for the acquisition, an Olympus 2X 0.5NA MVPLAPO, has a strong corner deformation, so we restrict the y range because no cells can be reliably detected outside of this range.

As a reminder, in the image files, the (0, 0, 0) coordinate corresponds to the upper left corner of the first plane. To the opposite, the (2160, 2660, 2400) coordinate will be the bottom right corner of the last plane (here 2400, but can vary).

When optimizing the parameters for the object detection, you should dramatically restrict the range to speed up the detection. We recommend using 500 planes, 500 pixels on each side:

     >>> cFosFileRange = {'x' : (500, 1000), 'y' : (500, 1000), 'z' : (500, 1000)};

But of course adapting the range to where the relevant objects are on your sample.

Next, to set the resolution of the original data (in µm / pixel):

     >>> OriginalResolution = (4.0625, 4.0625, 3);

In this example, this is set for a zoom factor of 0.8X on the LaVision system with the 2X lens. This information can be found in the metadata of the tif file usually. If you don’t know the pixel size, we recommend opening the stack with the plugin BioFormat on ImageJ, and going to « image » -> « show info » to read the metadata. On the LaVision file, this information is at the end of the list.

The orientation of the sample has to be set to match the orientation of the Atlas reference files. It is not mandatory to acquire the sample in the same orientation as the atlas. For instance, you can acquire the left side of the brain, and map it onto the right side of the atlas:

     >>> FinalOrientation = (1,2,3);

The convention is as follow (examples given, any configuration is possible):

=================== ========================================================
Value of the tuple  Description
=================== ========================================================
(1, 2, 3)           The scan has the same orientation as the atlas reference
(-1, 2, 3)          The x axis is mirrored compared to the atlas
(1, -2, 3)          The y axis is mirrored compared to the atlas
(2, 1, 3)           Performs a rotation by exchanging the x and y axis
(3, 2, 1)           Performs a rotation by exchanging the z and x axis
=================== ========================================================

For our samples, we use the following orientation to match our atlas files:

    * The right side of the brain is facing the objective, lateral side up.
    * The rostral side of the brain is up
    * The dorsal side is facing left
    * The ventral side is facing right

This means that in our scans, if we want to image the right hemisphere, we use (1, 2, 3) and if we want to image the left hemisphere, we use (-1, 2, 3).

To set the output for the voxelized heat map file:

    >>> VoxelizationFile = os.path.join(BaseDirectory, 'points_voxelized.tif');

To set the resolution of the Atlas Files (in µm/ pixel):

    >>> AtlasResolution = (25, 25, 25);

To choose which atlas files you would like to use:

    >>> PathReg        = '/home/mtllab/Documents/warping';
    >>> AtlasFile      = os.path.join(PathReg, 'half_template_25_right.tif');
    >>> AnnotationFile = os.path.join(PathReg, 'annotation_25_right.tif');

It is important to make sure that the Atlas used is in the correct orientation (see above), but also don’t contain too much information outside of the field of view. While the registration program can deal with a bit of extra « bleed » outside of the sample, this should be kept to a minimum. We usually prepare different crops of the atlas file to match the usual field of views we acquire.

`Cell detection`
^^^^^^^^^^^^^^^^

At this point, two detection methods exist: the ``SpotDetection`` and ``Ilastik``:

    * ``SpotDetection`` is designed for globular objects, such as neuron cell bodies or nuclei. This is the fastest method, and offers a greater degree of fine controls over the sensitivity of the detection. However, it is not well suited for complex objects.
    * ``Ilastik`` is a framework that relies on the user generating a classifier through the graphical interface of the Ilastik program, by painting over a few objects and over the background. The program will then learn to classify the pixels between objects or backgrounds based on the user indications. This is a very easy way to tune very complex filters to detect complex objects or textures. However, the classification is a black box, and very dependent of the user’s classification.

In this tutorial, we will use the SpotDetection method. To choose which method to use for the cell detection, set the variable as follows:

    >>> ImageProcessingMethod = "SpotDetection";

The parameters for the Spot Detection methods are then sorted in « dictionaries » by theme :

============================ =======================================================================================================================
Dictionary name              Description
============================ =======================================================================================================================
correctIlluminationParameter If you have an intensity profile for your microscope, you can correct variations in illuminations here  
removeBackgroundParameter    To set the background subtraction via morphological opening
filterDoGParameter           To set the parameters for the Difference of Gaussian filter
findExtendedMaximaParameter  If the object contains multiple peaks of intensity, this will collapse them into one peak
findIntensityParameter       Often, the center of the mass of an object is not the voxel of highest intensity. This is a correction for this
detectCellShapeParameter     This sets the parameters for the cell shape filling via watershed
============================ =======================================================================================================================


Correcting the illumination:
""""""""""""""""""""""""""""
Because of the Gaussian shape of the light sheet and of the objecting lens vignetting, the sample illumination is not uniform. While correcting the illumination can improve the uniformity of the cell detection, it is usually not really necessary if all samples where imaged the same way, as the same anatomical features will be positioned in the same region of the lens across samples. Nevertheless, to correct for variation in the illumination use:

    >>> correctIlluminationParameter = {
    >>>    "flatfield"  : None,  
    >>>    "background" : None,
    >>>    "scaling"    : "Mean", 
    >>>    "save"       : None,
    >>>    "verbose"    : True
    >>> }

For this tutorial, we will not use the correction, so the ``flatfield`` parameter is set to ``None``. Please note that you need to generate an intensity profile for your system if you wish to use this function.

Background Subtraction:
"""""""""""""""""""""""
This is the most important pre-treatment step, usually always turned on. The background subtraction via morphological opening is not very sensitive to the size parameter used, as long as it is in the range of the size of the objects detected. The parameters for the background subtraction are as follow:

    >>> removeBackgroundParameter = {
    >>>     "size"    : (7,7),
    >>>     "save"    : None,
    >>>     "verbose" : True       
    >>> }

The parameter ``size`` is a tuple with (x,y) in pixels and correspond to an ellipsoid of this size. Of importance, you can check the result of the background subtraction by setting the ``save`` parameter to a filename. This will output a series of tif images you can open with ImageJ to check the results. For instance you could set ``save`` like this:

    >>>     "save"    : os.path.join(BaseDirectory, 'background/background\d{4}.ome.tif');

You have to use the ``\d{4}`` notation to save the files as a series of images, otherwise only the first plane is saved!

.. note:: Only use the ``save`` function when you analyse a small subset of your data, otherwise the full stack will be written to the disk. Don’t forget to turn off this parameter when you’re done optimizing the filters.


Difference of Gaussians filter:
"""""""""""""""""""""""""""""""
This is an optional filter to improve the contrast of objects. This filter has a "Mexican Hat" shape that weighs negatively the intensity at the border of the objects. The main parameter to set here is the ``size``, as an (x,y,z) tuple, for instance ``(6,6,11)`` would work well for our example. However, we’ll bypass this filter and set it to ``None``:

   >>> filterDoGParameter = {
   >>>     "size"    : None,
   >>>     "sigma"   : None,
   >>>     "sigma2"  : None,
   >>>     "save"    : None,
   >>>     "verbose" : True
   >>> }

For this tutorial, we will not use the DoG filter, as it is unnecessary. The signal from a c-Fos nuclear staining has enough contrast and a simple shape that do not necessitate this additionnal filtering, but it could help increase the contrast of the relevant objects for other experiments.

.. note:: As for the background subtraction seen above, you can save the output of the filter to files in a folder. This is important in order to check that the settings you used are effective!

Extended Maxima:
""""""""""""""""
The extended maxima is another filter to use for objects that contain several peaks of intensity, like for instance a higher resolution view of a cell nucleus where you might have a more granular texture. In the case of our tutorial, the c-fos nuclear signal is imaged at low resolution, so the object only appears as a single peak, so we will turn off the extended maxima by setting the ``hMax`` parameter to ``None``:

   >>> findExtendedMaximaParameter = {
   >>>     "hMax"      : None,
   >>>     "size"      : 0,
   >>>     "threshold" : 0,
   >>>     "save"      : None,
   >>>     "verbose"   : True
   >>> }

.. note:: Saving the files for the output of this filter as explained above would overlay in red the extended maxima found on top of the DoG filtered image (we recommend using also DoG if you use the Extended Maxima).

Peak Intensity:
"""""""""""""""
By default, the code will look for the center of the 3D shape painted by the Extended Maxima and attribute the x,y,z to this coordinate. This is the coordinate that will be saved in the point file. However, we noticed that often, the pixel that contains the highest intensity (the peak) is not always the center of the volume. This is likely due to potential deformations of the shape of the nucleus by the objective lens. To look for the actual peak intensity for the detected object, we’ll use this function:

   >>> findIntensityParameter = {
   >>>     "method" : 'Max',
   >>>     "size"   : (3,3,3)
   >>> }

If the parameter ``method`` is set to ``None``, then the peak intensity will be also the pixel at the center of the volume. We’ll set the parameter to ``Max`` to look if there is a voxel around the center that has a higher intensity than the center. This will be done by looking around the center with a box of a certain ``size``, that we set here to (3,3,3), which indicates by how many pixels in each direction from the center the code will be looking for a peak of higher intensity.

Cell Volume:
""""""""""""

The cell shape is not used for the cell detection itself (which is just searching for local maxima in intensity), but measuring the cell volume will be important to later remove the local peaks detected that do not correspond to an actual cell. This is done by setting these parameters:

   >>> detectCellShapeParameter = {
   >>>     "threshold" : 700,
   >>>     "save"      : None,
   >>>     "verbose"   : True
   >>> }

The shape detection is done by a watershed, which will paint the volume of the cell from the detected center outwards. The only parameter to set is the ``threshold``. The threshold corresponds to the background intensity, and tells the watershed detection where to stop painting. This value is based on the background subtracted image here. If the ``threshold`` is set to ``None``, then the cell shape detection is bypassed.

.. note:: Saving the files for the output of this filter as explained above would show all detected objects. The most convenient is to open the folder of images generated with ImageJ, and apply a LUT (Lookup Table) to color each object differently, for instance using the LUT 3-3-2 RGB. The code will write on the image each detected object with a increasing intensity value, so you can make sure this way that adjacent cells are not blending together.


`Heat map generation`
^^^^^^^^^^^^^^^^^^^^^

The voxelization makes it easier to look at the results of the cell detection. The voxelization function will create an image of a specified size (usually the size of the Atlas file) and plot the detected cell centers. To make them visible easily, each point will be expanded into a sphere (or cube, or gaussian) of a given diameter. The intensity value of this sphere is set to 1 by default. So if many points are detected, the overlapping spheres will create a high intensity region.

To set the output for the voxelized heat map file (you would usually not change this):

    >>> VoxelizationFile = os.path.join(BaseDirectory, 'points_voxelized.tif');

And then let’s survey the parameters for the voxelization:

   >>> voxelizeParameter = {
   >>>     "method" : 'Spherical',
   >>>     "size" : (15,15,15),  
   >>>     "weights" : None
   >>> };

The ``method`` here is set to ``Spherical`` to paint the points as expanded spheres. the ``size`` of those spheres is set next, and is given in pixels. Here, we’ll choose ``(15,15,15)``, but feel free to experiment! Note that the size is in pixels in the final resolution. So for instance, here each sphere will have a diameter of 15 x 25 = 375µm. The ``weights`` parameter will be changed later, but is set to ``None`` at this point, meaning that each sphere has an intensity value of 1. The weights allows to change this by integrating the size or intensity of the cells when drawing each sphere.



`Config parameters`
^^^^^^^^^^^^^^^^^^^

There are two configuration parameter you should change to match the processing power of your workstation. The first one is the number of processors to be used for the resampling/rotation operations. As this process is not very demanding for the memory, just use the max number of parallel processes your configuration can handle. For instance, we have a 6 cores machine:

   >>> ResamplingParameter = {"processes": 12};

The next settings are for the cell detection. This is limited mainly by the amount of RAM memory you have, but will also change depending on how many filters you use, and their settings. Here is the setting we use on our machine, with 128Gb of RAM for this tutorial:

   >>> StackProcessingParameter = {
   >>>     "processes" : 6,
   >>>     "chunkSizeMax" : 100,
   >>>     "chunkSizeMin" : 50,
   >>>     "chunkOverlap" : 16,
   >>>     "chunkOptimization" : True,
   >>>     "chunkOptimizationSize" : all,
   >>>     "processMethod" : "parallel"   
   >>> };

For the cell detection, the full stack of images will be sliced in smaller chunks to be processed in parallel, and then fused back together. Although it would be tempting to use all the available parallel processing power from your machine, each chunk will take a significant amount of RAM while being analyzed, so the more chunks you process in parallel, the smaller they will be. Also, the chunks will need to overlap, so the smaller they are, the higher the number of overlaps. The size of a chunk is set by both ``chunkSizeMax`` and ``chunkSizeMin``. This is because the code will determine what is the ideal chunk size within that range, depending on the total number of chunks to process. When running the script, keep an eye on the amount of memory used by using the system’s activity monitor for instance. If too much data has to go in the swap memory (meaning the RAM is maxed out), reduce the chunk size, or reduce the number of parallel processes.


`Run Parameters`
^^^^^^^^^^^^^^^^

You usually would not change anything in this section of the parameter file. This section defines the name of the files generated during the run, and set the parameters for the various operations of resampling and alignment. Of note, you can check these parameters for the alignment:

   >>> RegistrationAlignmentParameter["affineParameterFile"] = \
   >>>                 os.path.join(PathReg, 'Par0000affine.txt');
   >>> RegistrationAlignmentParameter["bSplineParameterFile"] = \
   >>>                 os.path.join(PathReg, 'Par0000bspline.txt');

These point to the two files that will be used as parameter files for the alignment operation with Elastix. If you create new parameter files for the alignment based on your specific need, just make sure you link to the correct parameter file here.

We’re all set for the parameter file, now let’s explain how the run will proceed.


The Run File
------------

The run file consist of the list of operation to execute to analyze each sample. For our tutorial, it can be found in /ClearMap/Scripts/process_template.py. The run file starts by loading all the parameters from the parameter file:

   >>> execfile('./ClearMap/Scripts/parameter_file_template.py')

Make sure all the modules load correctly. Otherwise, try to install the missing modules. You might get a warning from the compiler the first time you load to parameter file on a new installation. The script shown in the tutorial will execute the following operations:

    * `Resampling operations`_
    * `Alignment operations`_
    * `Cell detection and thresholding`_
    * `Point coordinate transformation`_
    * `Heat map`_
    * `Table generation`_


`Resampling operations`
^^^^^^^^^^^^^^^^^^^^^^^
The first set of operations to run are the resampling, which will use the parameters set previously. The resampling is executed by the ``resampleData`` function:

   >>> resampleData(**CorrectionResamplingParameterCfos);
   >>> resampleData(**CorrectionResamplingParameterAutoFluo);
   >>> resampleData(**RegistrationResamplingParameter);

As you can notice, there are 3 sets of resampling operations. The first two are optional. They create files of intermediate size for the c-Fos and Autofluorescence channels to correct for eventual movements of the sample between the acquisition of those channels. The third resampling only concerns the auto-fluorescence channel and will generate the file used to align to the Atlas reference.

`Alignment operations`
^^^^^^^^^^^^^^^^^^^^^^

The alignment is done via Elastix, which is interfaced by ClearMap and is executed by the ``alignData`` function:

   >>> resultDirectory  = alignData(**CorrectionAlignmentParameter);
   >>> resultDirectory  = alignData(**RegistrationAlignmentParameter);

We again do two sets of alignments. The first one here is optional, and is using the files of intermediate resolution generated by the first two resampling operations to re-align the 2 channels in case the sample moved between acquisitions. The second alignment is done onto the Atlas.


`Cell detection and thresholding`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The cell detection is started by this command:

   >>> detectCells(**ImageProcessingParameter);

This should take a while, between 20 minutes to a few hours depending on your machine, the size of the stack, the filter used. If you're executing the cell detection for testing the parameter, consider restricting the range of the detection as described above with the ``cFosFileRange`` parameter.

The cell detection will create two files here: ``cells-allpoints.npy`` and ``intensities-allpoints.npy``. These two files will contain all the detected maxima, and need to be filtered, as most local peaks do not correspond to an actual cell.

.. note:: The coordinates in the files are in the original coordinates of the raw data, and are not transposed yet.

Once the cell detection is done, the points detected have to be filtered to retain only the genuine cells. This is the most important step of the cell detection. First, let's open the files ``cells-allpoints.npy`` and ``intensities-allpoints.npy``: 

   >>> points, intensities = io.readPoints(ImageProcessingParameter["sink"]);

Here, we use the function io.readPoints which opens the data related to points coordinates or intensities. In ClearMap scripts, the inputs are usually referred to as ``source`` and the output as ``sink``. ``ImageProcessingParameter["sink"]`` is defined in the parameter file described above, and is a tuple containing the location of both files for point coordinates and intensities. So here we're opening both files at the same time.

Then, we use the function ``thresholdPoints`` to threshold the points based on their size and save them to 2 files (coordinates and intensities):

   >>> points, intensities = thresholdPoints(points, intensities, \
   >>>                              threshold = (20, 900), row = (3,3));
   >>> io.writePoints(FilteredCellsFile, (points, intensities));

The way the ``thresholdPoints`` function work is by setting the ``threshold`` parameter as ``(lower limit, upper limit)``. If only one value is provided, it assumes this is the lower boundary. ``row`` defines for the (lower, higher) boundaries which column to use from the intensities array. We presented this array in the overview, but as a reminder:

======= ===================================================================================
Row     Description
======= ===================================================================================
0       Max intensity of the cell center in the raw data
1       Max intensity of the cell center after the DoG filtering.
2       Max intensity of the cell center after the background subtraction
3       Cell size in voxels after the watershed detection   
======= ===================================================================================
 
So here we use column 3 for both boundaries, which is the volume in voxel of each detected cell, which we set at 20.

.. note:: the size in voxels of each detected cell is defined by the watershed, which will greatly depend on the ``threshold`` parameter set previously for the cell detection, so if you change this parameter, you'll have to adjust threshold here as well.

Finally, you can now check that the cell detection worked as expected by plotting the result of the detection and thresholding onto the raw data. This should be disabled if you're running the detection on the whole stack, and should only be used while testing. Just delete or comment out (with #) if you don't need it. To run the cell detection check:

   >>> import iDISCO.Visualization.Plot as plt;
   >>> pointSource= os.path.join(BaseDirectory, FilteredCellsFile[0]);
   >>> data = plt.overlayPoints(cFosFile, pointSource, pointColor = None, **cFosFileRange);
   >>> io.writeData(os.path.join(BaseDirectory, 'cells_check.tif'), data);

You might get a warning that a non-standard tiff file is being written. ImageJ, with the plugin BioFormat, can open these files. The resulting ``cell_check.tif`` file has 2 channels, one with the original data and one with the detected cells shown as a single pixel pointing to the detected center. Browse through the stack to make sure there is only one center detected per cell, that there are no obvious false positive or false negatives.


`Point coordinate transformation`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The points coordinate are then resampled and transformed onto their final position in the Atlas reference space. Again, this is done twice: once for the correction between both channels, and then for the Atlas alignment.

The first step: correction (optional)
   >>> points = io.readPoints(CorrectionResamplingPointsParameter["pointSource"]);
   >>> points = resamplePoints(**CorrectionResamplingPointsParameter);
   >>> points = transformPoints(points, \
   >>>     transformDirectory = CorrectionAlignmentParameter["resultDirectory"], \
   >>>     indices = False, resultDirectory = None);
   >>> CorrectionResamplingPointsInverseParameter["pointSource"] = points;
   >>> points = resamplePointsInverse(**CorrectionResamplingPointsInverseParameter);

The points are first resampled with the function ``resamplePoints`` and then their coordinates are transformed based on the results of the alignment done by Elastix with the ``transformPoints`` function. This function works by interfacing with the Transformix mode of Elastix. The parameter ``indices``, here set to ``False`` indicate to keep the point coordinates with the decimals after the resampling, instead of using the integer coordinates, so prevent loosing information while sequentially re-sampling the point coordinates.

The second step: alignment of the points in the Atlas reference space
   >>> RegistrationResamplingPointParameter["pointSource"] = points;
   >>> points = resamplePoints(**RegistrationResamplingPointParameter);
   >>> points = transformPoints(points, \
   >>>     transformDirectory = RegistrationAlignmentParameter["resultDirectory"],\
   >>>     indices = False, resultDirectory = None);


Then writing the final point coordinates:
   >>> io.writePoints(TransformedCellsFile, points);

The points in their Atlas coordinates are written in the file ``cells_transformed_to_Atlas.npy`` and will be used for the region statistics and to generate the heat maps.


`Heat map`
^^^^^^^^^^

First, let's open the files generated previously:

   >>> points = io.readPoints(TransformedCellsFile)
   >>> intensities = io.readPoints(FilteredCellsFile[1])

Then, the heat map is generated by the ``voxelize`` command:

   >>> vox = voxelize(points, AtlasFile, **voxelizeParameter);
   >>> io.writeData(os.path.join(BaseDirectory, 'cells_heatmap.tif'), vox.astype('int32'));

The heat map is generated as a 32bit float file, so it may need to be down sampled in ImageJ. The second parameter, ``AtlasFile``, is only to pass the size of the Atlas file to the function.

.. note:: The heat map generated here will be used later for the voxel statistics.


`Table generation`
^^^^^^^^^^^^^^^^^^

The table will show the number of detected points according to the region annotations. It relies on having a labeled image, which is a nrrd or tif file. The function ``countPointsInRegions`` will use the intensity value of each point as defining the regions:

   >>> ids, counts = countPointsInRegions(points, labeledImage = AnnotationFile, \
   >>>                                    intensities = None, collapse = None);

The ``AnnotationFile`` is set in the parameter file as shown above, and should match the dimensions and orientation of the Atlas file used. The ``collapse`` function is here set to ``None``, but is used if you wish to group adjacent regions into larger regions if you feel that the AnnotationFile has too many subdivisions.

Then, a table of the results is generated:

   >>> table = numpy.zeros(ids.shape, \
   >>>                  dtype=[('id','int64'),('counts','f8'),('name', 'a256')])
   >>> table["id"] = ids;
   >>> table["counts"] = counts;
   >>> table["name"] = labelToName(ids);
   >>> io.writeTable(os.path.join(BaseDirectory, 'Annotated_counts.csv'), table);


.. note:: Contrary to the heat maps, the table generated here will not be used for the statistics later, so it is not necessary to execute this in most cases.

This concludes the part of the tutorial covering the settings and run parameters used to analyze the c-Fos dataset in the mouse brain. The next section will cover how to run the statistics on the results obtained after running the ``process_template.py`` script for all samples of the same experiment.


Analysis Tools
--------------

ClearMap provides different ways to analyze the results of the cell detection. In this tutorial, we will examine how to compare the c-Fos cell distribution in 2 groups of 4 brains each analyzed with the scripts shown above. The statistics package covers two sorts of statistical analysis:

   * `Voxel statistics`_: these are based on the heat map generated as above
   * `Regions statistics`_: these are using the annotation files to segment the detected cells into anatomical regions
   * `Automated region isolation`_: to visualize in 3D specific regions from the heat maps

In this example, we will compare a group of control mice injected with a saline solution against mice injected with Haloperidol, which is a psycho-active drug.

`Voxel statistics`
^^^^^^^^^^^^^^^^^^

First, let's import the modules necessary to run the statistics, and set the working directory:

   >>> import ClearMap.Analysis.Statistics as stat
   >>> import iDISCO.Analysis.Tools.MultipleComparisonCorrection as mc
   >>> import ClearMap.Analysis.Label as lbl
   >>> import ClearMap.IO.IO as io
   >>> import numpy, os
   >>> baseDirectory = '/home/mtllab/Documents/pharmaco/'

.. note:: Here we set the working directory to the folder containing all the samples for this experiment, while we were working inside the folders of individual samples previously.

Then, let's load the heat map image stacks from each sample into two groups:

   >>> group1 = ['/home/mtllab/Documents/pharmaco/sample1/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample2/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample3/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample4/cells_heatmap.tif'
   >>>           ];
   >>> group2 = ['/home/mtllab/Documents/pharmaco/sample5/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample6/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample7/cells_heatmap.tif',
   >>>           '/home/mtllab/Documents/pharmaco/sample8/cells_heatmap.tif'
   >>>           ];
   >>> g1 = stat.readDataGroup(group1);
   >>> g2 = stat.readDataGroup(group2);

We can then generate average heat maps for each group, as well as standard deviation maps:

   >>> g1m = numpy.mean(g1,axis = 0);
   >>> io.writeData(os.path.join(baseDirectory, 'saline_mean.mhd'), \
   >>>                                          io.sagittalToCoronalData(g1m));
   >>> g1s = numpy.std(g1,axis = 0);
   >>> io.writeData(os.path.join(baseDirectory, 'saline_std.mhd'), 
   >>>                                          io.sagittalToCoronalData(g1s));

The same thing will be done for group 2. Instead of writing directly the result as an image (here we wrote the file as a raw ``.mhd`` file), we used the function ``io.sagittalToCoronalData`` which is a convenient way to reorient the data in coronal plane, which is a more usual way to look at anatomical data (the scans and atlases are in sagittal orientation originally). Open the ``.mhd`` files in ImageJ. Don't forget that the ``.mhd`` file is just the header, and that the actual image comes in the companion ``.raw`` file.

We can now generate the *p* values map:

   >>> pvals, psign = stat.tTestVoxelization(g1.astype('float'), g2.astype('float'),\
   >>>                                       signed = True, pcutoff = 0.05);
   >>> pvalscolor = stat.colorPValues(pvals, psign, positive = [0,1], negative = [1,0]);
   >>> io.writeData(os.path.join(baseDirectory, 'pvalues.tif'), \
   >>>              io.sagittalToCoronalData(pvalscolor.astype('float32')));

We used here a cutoff of 5%. The first function ``stat.tTestVoxelization`` generates the *p* values using a T test with the unequal variance hypothesis set by default. The 
``stat.colorPValues`` function will attribute a color to each pixel of the *p* value map depending on whether the difference of the means between group1 and group2 is significantly positive or negative. You may get a warning that a non-standard tiff file is being written. You may also get warnings from the statistics library during the test calculation, just ignore them.

You have now generated 5 image stacks: 2 average heat maps, 2 standard deviation maps (one for each group) and 1 *p* values map.


`Regions statistics`
^^^^^^^^^^^^^^^^^^^^

The region statistics use an annotation image file that defines the anatomical regions:

   >>> ABAlabeledImage = '/home/mtllab/atlas/annotation_25_right.tif'; 

For the region statistics, we will load the point coordinates instead. We'll use the file that contains the coordinates transformed to the Atlas:

   >>> group1 = ['/home/mtllab/Documents/pharmaco/sample1/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample2/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample3/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample4/cells_transformed_to_Atlas.npy'
   >>>           ];
   >>> group2 = ['/home/mtllab/Documents/pharmaco/sample5/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample6/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample7/cells_transformed_to_Atlas.npy',
   >>>           '/home/mtllab/Documents/pharmaco/sample8/cells_transformed_to_Atlas.npy'
   >>>           ];

Then we'll count the number of cells per region for each group:

ids, counts1 = stat.countPointsGroupInRegions(group1, intensityGroup = None, returnIds = True, labeledImage = ABAlabeledImage, returnCounts = True, collapse = None);
counts2 = stat.countPointsGroupInRegions(group2, intensityGroup = None, returnIds = False, labeledImage = ABAlabeledImage, returnCounts = True, collapse = None);

The function ``stat.countPointsGroupInRegions`` can return 1, 2 or 3 results depending on the parameters set:

=============== =================================================================================================================================================
Parameter       Description
=============== =================================================================================================================================================
intensityGroup  You can, on top of a cell coordinate group, create groups containing the intensity data, to include the intensity information in the statistics
returnIds       To set the function to return the region identity found in the labeled file. You only have to do it for one of the two groups
collapse        You can set regions to be fused into larger regions from the table file containing the region names and hierarchy
=============== =================================================================================================================================================

Then you can calculate the *p* values for the significance of the difference of the mean for each region. Those tests are independent:

   >>> pvals, psign = stat.tTestPointsInRegions(counts1, counts2, pcutoff = None, \
   >>>                                          signed = True, equal_var = False);

Optionally, you can also attribute a "q" value to the *p* values, to estimate the false discovery rate, as we're performing a lot of tests:

   >>> qvals = mc.estimateQValues(pvals);

And then you can generate a table containing those results (see the included script file for generating the table).


`Automated region isolation`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also apply the Annotation file to the heat maps instead of the detected cells. This will generate 3D crops of the heat maps to only show specific regions according to the annotation file. Start by importing the modules as shown above, as well as setting the annotation file you wish to use as shown previously. We'll generate then a variable containing the list of all the labels IDs present in the annotation file:

   >>> label = io.readData(annotationFile);
   >>> label = label.astype('int32');
   >>> labelids = numpy.unique(label);

Then, we'll create a map, ``outside`` of everything we want to exclude. For example, to exclude every structure of the brain except the cortex, let's do:

   >>> for l in labelids:
   >>>    if not lbl.labelAtLevel(l, 3) == 688:
   >>>        outside = numpy.logical_or(outside, label == l);

Here, we're using the function ``lbl.labelAtLevel`` which returns the identity of the parent of a region at a given level of hierarchy. The regions IDs are annotated in a table in ClearMap with for each region of the brain the identity of its parent region containing it. For instance, the layer 4 of the barrel cortex is 8 levels deep in the hierarchy and has the ID 1047, and is contained in the barrel cortex (329) which is itself in the cortex (688). ``lbl.labelAtLevel(x, n)`` will return the ID of the region at the level ``n`` containing the region ``x``. So if ``x`` is 5 levels deep in the hierarchy of all regions, then when ``n`` is larger than 5, the function will return ``x``. Otherwise, if ``n`` is smaller than 5, it returns the ID of the region of level ``n`` containing ``x``.

So now, the variable outside contains a boolean array for each voxel (True or False) whether that voxel belongs to the cortex or not in the reference space (True means it is not cortex). Let's then open our average heat map:

   >>> heatmap = io.readData('/home/mtllab/pharmaco/saline_mean.mhd');

Then, let's set all the voxels outside of the cortex to 0 and write the result:

   >>> heatmap[outside] = 0;
   >>> io.writeData('/home/mtllab/Documents/pharmaco/saline_cortex.mhd', heatmap);

In the same fashion, you can include or exclude regions easily by using the annotation files. You can then open the stacks saved in ImageJ for instance and use one of the 3D viewers to look at the region isolated in 3D.

This concludes this tutorial, which should contain enough information to get you started. The next chapter will show a few examples of the effect of the various filters included in ClearMap for cell detection, and the following chapter is a reference that covers in detail all the included functions of ClearMap.