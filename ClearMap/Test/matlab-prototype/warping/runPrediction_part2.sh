export SVN_REVISION=SVNREVNO
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/MCR/v80/bin/glnxa64:.
export MCR_DIRECTORY=/usr/local/MCR/v80
export INSTALL_PREFIX=`expr /usr/local/prototype_matlab/V"$SVN_REVISION"`

export DATASET_HOME=/home/anagendran/Desktop/Testing_environment/130913_cert_0542/
export DATASET_PREFIX=130913_cert_0542
IS_TWO_CHANNEL=0 # put 1 for 2chnl and 0 for 1chnl prediction #
IS_50MICRONSPACING_DATASET=1 # put 1 for 50 micron spacing and 0 for 100 micron spacing
DO_SUBTRACTED_CHANNEL_PREDICTION=1 #put 1 if you are using subtracted channels for prediction 0 otherwise
export DO_INVERT_IMAGE_FIJI_CELL_SEPARATION=0
export CH1_MEAN=428
export CH1_VARIANCE=148
export CH2_MEAN=421
export CH2_VARIANCE=166
export WARPABLERANGE_START=5
export WARPABLERANGE_END=280
export GPU_ID=0
export NETWORK_ID=164
export CONTRASTRANGE_MIN=0
export CONTRASTRANGE_MAX=1000
export VOXEL_NATURE=0
if [ $IS_50MICRONSPACING_DATASET -eq 1 ]
then
export MOVINGIMAGE=/usr/local/prototype_matlab/data/OstenRef_ARA_v2.tif
export LABELIMAGEFILE=/usr/local/prototype_matlab/data/ORL_ARA_v2.3_bi_rotated.tif
else
export MOVINGIMAGE=/usr/local/prototype_matlab/data/OstenRef_ARA_v2_150.tif
fi
export WRITE_OVERLAYIMAGES=0  # put 1 to write overlay images and 0 to skip write overlay images #
export DETECT_CIRCLES=0  # put 1 to detect circles and 0 to skip detect circles #
export DO_BINARY_WATERSHED=0  # put 1 to do watershed and 0 for not doing it
export DETECT_WRITECENTROID=0 # put 1 to write detected centriod and 0 to skip write detected centroid #
export AREA_SIZE=50
export THRESHOLD=0.98
export NTHREADS=1

export CH1_PREFIX=ch1
export CH2_PREFIX=ch2
export CH1_STITCHED_DIR=`expr "$DATASET_HOME"stitchedImage_"$CH1_PREFIX"`
export CH2_STITCHED_DIR=`expr "$DATASET_HOME"stitchedImage_"$CH2_PREFIX"`
export CH1_CLEANUP_DIR=`expr "$CH1_STITCHED_DIR"/"$NETWORK_ID"/cleanup/`

if [ $DO_SUBTRACTED_CHANNEL_PREDICTION -eq 1 ]
then
export SUBTRACTED_CHANNEL_DIR=`expr "$CH2_STITCHED_DIR"/subtractedChannel/`
export CH1_CLEANUP_DIR=`expr "$CH2_STITCHED_DIR"/subtractedChannel/"$NETWORK_ID"/cleanup/`
fi
export CH2_CLEANUP_DIR=`expr "$CH2_STITCHED_DIR"/"$NETWORK_ID"/cleanup/`
export WARPING_DIR=`expr "$DATASET_HOME"warping`
export CH1_CENTROIDS_DIR=`expr "$CH1_CLEANUP_DIR"centroids`
export CH2_CENTROIDS_DIR=`expr "$CH2_CLEANUP_DIR"centroids`
export ELASTIX_OUTPUT_DIR=`expr "$WARPING_DIR"/elastixOutput/`
export TRANSFORMIX_OUTPUT_DIR=`expr "$WARPING_DIR"/transformixOutput/`

# Cell detection
export ONECHNL_PREDICTION_EXE=`expr "$INSTALL_PREFIX"/bin/PredictLabels/src/run_PredictLabels.sh`
export TWOCHNL_PREDICTION_EXE=`expr "$INSTALL_PREFIX"/bin/PredictLabels2Channel/src/run_PredictLabels2Channel.sh`

# cell separation by Fiji binary watershed
export FIJI_EXE=/usr/local/Fiji.app/fiji-linux64
export BINARY_WATERSHED_SCRIPT=`expr "$INSTALL_PREFIX"/bin/BinaryCellSeparationFijiMacro2.py`
export BINARY_WATERSHED_INPUTDIR=VARIABLE_SET_LATER
export BINARY_WATERSHED_OUTPUTDIR=VARIABLE_SET_LATER

# writeCentroids
export WRITECENTROIDS_EXE=`expr "$INSTALL_PREFIX"/bin/run_writeCentroidsFiles.sh`
export XSPACING=1
export YSPACING=1
if [ $IS_50MICRONSPACING_DATASET -eq 1 ] # put 1 for 50 micron spacing and 0 for 100 micron spacing
then
export ZSPACING=50
else
export ZSPACING=100
fi

# creating warpable elastix file
export CH1_WARPABLE_MAT=`expr "$CH1_CENTROIDS_DIR"/"$DATASET_PREFIX".mat`
export CH2_WARPABLE_MAT=`expr "$CH2_CENTROIDS_DIR"/"$DATASET_PREFIX".mat`
export WARPABLE_ELASTIX_EXE=`expr "$INSTALL_PREFIX"/bin/run_createWarpableElastixFile.sh`

# creating warpable image
export P05_FILEPATH=`expr "$WARPING_DIR"/"$DATASET_PREFIX"_"$CH1_PREFIX"_p05.tif`
export WARPABLEIMAGE_EXE=`expr "$INSTALL_PREFIX"/bin/run_createWarpableImage.sh`
export WARPABLE_XSIZE=450
export WARPABLE_YSIZE=650
if [ $IS_50MICRONSPACING_DATASET -eq 1 ] # put 1 for 50 micron spacing and 0 for 100 micron spacing
then
export WARPABLE_ZSIZE=300
else
export WARPABLE_ZSIZE=150
fi

# elastix 
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/elastix/lib/
export ELASTIX=/usr/local/elastix/bin/elastix
export FIXEDIMAGE=`expr "$WARPING_DIR"/"$DATASET_PREFIX"_"$CH1_PREFIX"_p05_warpable.tif`
export AFFINEPARFILE=/usr/local/elastix/data/Par0000affine.txt
export BSPLINEPARFILE=/usr/local/elastix/data/Par0000bspline.txt

# transformix
export TRANSFORMIX=/usr/local/elastix/bin/transformix
export CH1_POINTLISTFILE=`expr "$CH1_CENTROIDS_DIR"/"$DATASET_PREFIX"_elastix_warpable.txt`
export CH2_POINTLISTFILE=`expr "$CH2_CENTROIDS_DIR"/"$DATASET_PREFIX"_elastix_warpable.txt`
export ELASTIX_TRANSFORM_FILE=`expr "$ELASTIX_OUTPUT_DIR"TransformParameters.1.txt`

# convert from transformix output format to point list format
export TRANSFORMIXOUTPUT_FILE=`expr "$TRANSFORMIX_OUTPUT_DIR"outputpoints.txt`
export TRANSFORMIX2ELASTIX_EXE=`expr "$INSTALL_PREFIX"/bin/run_writeTransformixToElastixFile.sh`

# Voxelization
export NX=450
export MINX=0
export MAXX=450
export XSCALE=20
export NY=650
export MINY=0
export MAXY=650
export YSCALE=20
if [ $IS_50MICRONSPACING_DATASET -eq 1 ] # put 1 for 50 micron spacing and 0 for 100 micron spacing
then
export NZ=300
export MAXZ=300
export ZSCALE=50
else
export NZ=150
export MAXZ=150
export ZSCALE=100
fi
export MINZ=0
export DISTANCE=100
export VOXELIZATION_EXE=`expr "$INSTALL_PREFIX"/bin/run_voxelize.sh`
export POINTLIST_MAT=`expr "$TRANSFORMIX_OUTPUT_DIR"outputpoints_pointList.mat`

if [ $IS_TWO_CHANNEL -eq 1 ]
  then
    export FLUO_CHANNEL_DIR=$CH2_STITCHED_DIR
    echo "Running Two channel prediction on:" $FLUO_CHANNEL_DIR
    $TWOCHNL_PREDICTION_EXE $MCR_DIRECTORY $GPU_ID $NETWORK_ID $CH1_STITCHED_DIR $CH2_STITCHED_DIR $CONTRASTRANGE_MIN $CONTRASTRANGE_MAX $CH1_MEAN $CH1_VARIANCE $CH2_MEAN $CH2_VARIANCE $WRITE_OVERLAYIMAGES
  else
    if [ $DO_SUBTRACTED_CHANNEL_PREDICTION -eq 1 ]
      then
        export FLUO_CHANNEL_DIR=$SUBTRACTED_CHANNEL_DIR
        echo "Running Subtracted channel prediction on:" $FLUO_CHANNEL_DIR
        $ONECHNL_PREDICTION_EXE $MCR_DIRECTORY $GPU_ID $NETWORK_ID $SUBTRACTED_CHANNEL_DIR $CONTRASTRANGE_MIN $CONTRASTRANGE_MAX $CH1_MEAN $CH1_VARIANCE $WRITE_OVERLAYIMAGES $AREA_SIZE $THRESHOLD
      else
        export FLUO_CHANNEL_DIR=$CH1_STITCHED_DIR
        echo "Running One channel prediction on:" $FLUO_CHANNEL_DIR
        $ONECHNL_PREDICTION_EXE $MCR_DIRECTORY $GPU_ID $NETWORK_ID $CH1_STITCHED_DIR $CONTRASTRANGE_MIN $CONTRASTRANGE_MAX $CH1_MEAN $CH1_VARIANCE $WRITE_OVERLAYIMAGES $AREA_SIZE $THRESHOLD
    fi
fi
# If binary cell separation
if [ $DO_BINARY_WATERSHED -eq 1 ]
then
export BINARY_WATERSHED_INPUTDIR=$CH1_CLEANUP_DIR
export BINARY_WATERSHED_OUTPUTDIR=$CH1_CLEANUP_DIR
$FIJI_EXE $BINARY_WATERSHED_SCRIPT $BINARY_WATERSHED_INPUTDIR $BINARY_WATERSHED_OUTPUTDIR $DO_INVERT_IMAGE_FIJI_CELL_SEPARATION
fi
$WRITECENTROIDS_EXE $MCR_DIRECTORY $CH1_CLEANUP_DIR $FLUO_CHANNEL_DIR/ $DATASET_PREFIX $DETECT_CIRCLES $DETECT_WRITECENTROID $AREA_SIZE $XSPACING $YSPACING $ZSPACING $NTHREADS $LABELIMAGEFILE

$WARPABLE_ELASTIX_EXE $MCR_DIRECTORY $CH1_WARPABLE_MAT $WARPABLERANGE_START $WARPABLERANGE_END $NZ
$WARPABLEIMAGE_EXE $MCR_DIRECTORY $P05_FILEPATH $WARPABLERANGE_START $WARPABLERANGE_END $WARPABLE_XSIZE $WARPABLE_YSIZE $WARPABLE_ZSIZE
mkdir $ELASTIX_OUTPUT_DIR
$ELASTIX -threads 16 -m $MOVINGIMAGE -f $FIXEDIMAGE -p  $AFFINEPARFILE -p $BSPLINEPARFILE -out $ELASTIX_OUTPUT_DIR
mkdir $TRANSFORMIX_OUTPUT_DIR
$TRANSFORMIX -threads 24 -tp $ELASTIX_TRANSFORM_FILE -out $TRANSFORMIX_OUTPUT_DIR -def $CH1_POINTLISTFILE
$TRANSFORMIX2ELASTIX_EXE $MCR_DIRECTORY $TRANSFORMIXOUTPUT_FILE $NZ $LABELIMAGEFILE
$VOXELIZATION_EXE $MCR_DIRECTORY $NX $MINX $MAXX $XSCALE $NY $MINY $MAXY $YSCALE $NZ $MINZ $MAXZ $ZSCALE $DISTANCE $VOXEL_NATURE $POINTLIST_MAT
cd $TRANSFORMIX_OUTPUT_DIR
mv outputpoints_pointList.mat "$DATASET_PREFIX"_"$CH1_PREFIX"_pointList.mat
mv outputpoints_pointList_voxelImage.tif "$DATASET_PREFIX"_"$CH1_PREFIX"_voxelImage.tif
mv outputpoints_pointList_pointList.txt "$DATASET_PREFIX"_"$CH1_PREFIX"_pointList.txt
