/*--------------------------------------------------------------------------
 * voxelizeC.c script is used generate voxelized 3D image matrix from sparse points
 *
 ** Developed and maintained by Kannan Umadevi Venkataraju <kannanuv@cshl.edu>
 ** do not distribute without permission.
 *
 * Usage 
 * mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[])
 * vox = voxelize (nx, minx, maxx, ny, miny, maxy, nz, minz, maxz, distance, pointListFile)
 *---------------------------------------------------------------------------
 * History
 *---------------------------------------------------------------------------
 * Author   | Date         |Change
 *==========|==============|=================================================
 * kannanuv | 2011 May 01  |Initial Creation
 * kannanuv | 2015 Jun 15  |Exposed x, y, z scales
 *          |              |Write as 16-bit voxel images for higher range
 *----------------------------------------------------------------------------*/
#include <stdio.h>
#include <string.h>
#include "mex.h"
#include <math.h>

void mexFunction( int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
  int i1, iX, iY, iZ, iCentroid;
  int nx = 0;
  int ny = 0;
  int nz = 0;
  float minx = 0;
  float miny = 0;
  float minz = 0;
  float maxx = 0;
  float maxy = 0;
  float maxz = 0;
  int nCentroid = 0;
  float distance = 200;
  char* inputFileName;
  char* outputFileName;
  float* xVec;
  float* yVec;
  float* zVec;
  double* voxels;
  float xSpacing;
  float ySpacing;
  float zSpacing;
  float curx = 0;
  float cury = 0;
  float curz = 0;
  int loopxmin = 0;
  int loopxmax = 0;
  int loopymin = 0;
  int loopymax = 0;
  int loopzmin = 0;
  int loopzmax = 0;
  float xScale = 0;
  float yScale = 0;
  float zScale = 0;
  int voxelNature = 0;
  float l1x = 0;
  float l1y = 0;
  float l1z = 0;
  float l2 = 0;
  
  const mwSize  *dims;
  mwSize number_of_dimensions; 
  mwSize inputFileNameLength;
  mwSize outputFileNameLength;
  mwSignedIndex outputDimensions[3];

  (void) nlhs;     /* unused parameters */
  (void) plhs;
  
  nx = mxGetScalar(prhs[0]);
  minx = mxGetScalar(prhs[1]);
  maxx = mxGetScalar(prhs[2]);
  xScale = mxGetScalar(prhs[3]);
  
  ny = mxGetScalar(prhs[4]);
  miny = mxGetScalar(prhs[5]);
  maxy = mxGetScalar(prhs[6]);
  yScale = mxGetScalar(prhs[7]);
  
  nz = mxGetScalar(prhs[8]);
  minz = mxGetScalar(prhs[9]);
  maxz = mxGetScalar(prhs[10]);
  zScale = mxGetScalar(prhs[11]);
  distance = mxGetScalar(prhs[12]);
  
  inputFileName = mxCalloc (inputFileNameLength, sizeof (char));
  outputFileName = mxCalloc (outputFileNameLength, sizeof (char));
  
  inputFileName = mxArrayToString(prhs[13]);
  outputFileName = mxArrayToString(prhs[14]);
  
  voxelNature = mxGetScalar (prhs[15]);
  xVec = mxGetData (prhs[16]);
  yVec = mxGetData (prhs[17]);
  zVec = mxGetData (prhs[18]);
  dims = mxGetDimensions(prhs[16]);
  nCentroid = dims[0];
  
  mexPrintf ("nx, ny, nz = %d, %d, %d\n", nx, ny, nz);
  mexPrintf ("minx, miny, minz = %d, %d, %d\n", minx, miny, minz);
  mexPrintf ("maxx, maxy, maxz = %d, %d, %d\n", maxx, maxy, maxz);
  
  xSpacing = (((float)maxx - (float)minx))/(float)nx;
  ySpacing = (((float)maxy - (float)miny))/(float)ny;
  zSpacing = (((float)maxz - (float)minz))/(float)nz;
  
  minx = (int)((float)minx / xSpacing);
  maxx = (int)((float)maxx / xSpacing);
  miny = (int)((float)miny / ySpacing);
  maxy = (int)((float)maxy / ySpacing);
  minz = (int)((float)minz / zSpacing);
  maxz = (int)((float)maxz / zSpacing);
  
  mexPrintf ("nx, ny, nz = %d, %d, %d\n", nx, ny, nz);
  mexPrintf ("minx, miny, minz = %d, %d, %d\n", minx, miny, minz);
  mexPrintf ("maxx, maxy, maxz = %d, %d, %d\n", maxx, maxy, maxz);
  mexPrintf ("Spacing x, y, z = %f, %f, %f\n", xSpacing, ySpacing, zSpacing);
  mexPrintf ("distance = %f\n", distance);
  mexPrintf ("input file name = %s, output file name = %s\n", inputFileName, outputFileName);
  mexPrintf ("array dimensions = %d, %d\n", dims[0], dims[1]);
  
  outputDimensions[0] = nx;
  outputDimensions[1] = ny;
  outputDimensions[2] = nz;
  
  plhs[0] = mxCreateNumericArray(3, outputDimensions, mxDOUBLE_CLASS, mxREAL);
  voxels = mxGetPr (plhs[0]);
  
  for (iCentroid = 0; iCentroid < nCentroid; iCentroid++) {
  /*for (iCentroid = 0; iCentroid < 1; iCentroid++) {*/

      if ((iCentroid % 25000) == 0){
      /*mexPrintf ("\nProcessed %d/%d\n", iCentroid, nCentroid);*/
    }
    loopxmin = floor ((xVec[iCentroid] - distance/xScale - minx) / xSpacing);
    loopymin = floor ((yVec[iCentroid] - distance/yScale - miny) / ySpacing);
    loopzmin = floor ((zVec[iCentroid] - distance/zScale - minz) / zSpacing);
    loopxmax = ceil ((xVec[iCentroid] + distance/xScale - minx) / xSpacing);
    loopymax = ceil ((yVec[iCentroid] + distance/yScale - miny) / ySpacing);
    loopzmax = ceil ((zVec[iCentroid] + distance/zScale - minz) / zSpacing);

    if (loopxmin < minx) {
      loopxmin = minx;
    }
    if (loopymin < miny) {
      loopymin = miny;
    }
    if (loopzmin < minz) {
      loopzmin = minz;
    }
    if (loopxmax < minx) {
      loopxmax = minx;
    }
    if (loopymax < miny) {
      loopymax = miny;
    }
    if (loopzmax < minz) {
      loopzmax = minz;
    }

    if (loopxmin > maxx) {
      loopxmin = maxx;
    }
    if (loopymin > maxy) {
      loopymin = maxy;
    }
    if (loopzmin > maxz) {
      loopzmin = maxz;
    }
    if (loopxmax > maxx) {
      loopxmax = maxx;
    }
    if (loopymax > maxy) {
      loopymax = maxy;
    }
    if (loopzmax > maxz) {
      loopzmax = maxz;
    }

    for (iX = loopxmin; iX < loopxmax; iX++) {
      curx = minx + iX * xSpacing;
      for (iY = loopymin; iY < loopymax; iY++) {
        cury = miny + iY * ySpacing;
        for (iZ = loopzmin; iZ < loopzmax; iZ++) {
          curz = minz + iZ * zSpacing;
          /* switch should be used here ideally) */
          if (voxelNature == 0) { /*voxelNature = 0 for spherical)*/
            l2 = sqrt((xScale * xScale * (curx - xVec[iCentroid]) * (curx - xVec[iCentroid])) +
                      (yScale * yScale * (cury - yVec[iCentroid]) * (cury - yVec[iCentroid])) +
                      (zScale * zScale * (curz - zVec[iCentroid]) * (curz - zVec[iCentroid])));

            if (l2 < distance) {
                voxels[(iZ * ny * nx) + (iY * nx) + iX] = voxels[(iZ * ny * nx) + (iY * nx) + iX] + 1;
            }
          }
          if (voxelNature == 1) { /*voxelNature = 1 for cuboid)*/
            l1x = fabs(curx - xVec[iCentroid]);
            l1y = fabs(cury - yVec[iCentroid]);
            l1z = fabs(curz - zVec[iCentroid]);

            if (l1x < xSpacing/2) {
              if (l1y < ySpacing/2) {
                if (l1z < zSpacing/2) {
                  voxels[(iZ * ny * nx) + (iY * nx) + iX] = voxels[(iZ * ny * nx) + (iY * nx) + iX] + 1;
                }
              }
            }
          }
        }
      }
    }
  } 
}
