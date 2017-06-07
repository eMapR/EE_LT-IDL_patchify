# -*- coding: utf-8 -*-
"""
Created on Mon May  1 10:44:41 2017

@author: braatenj
"""

import gdal
import json
import subprocess
from glob import glob
import os



def get_feature_bounds(coords):
  x = []
  y = []  
  if feature['geometry']['type'] == 'Polygon':  
    level1 = feature['geometry']['coordinates']
    for i in range(len(level1)):     
      level2 = level1[i]
      for j in range(len(level2)):    
          coord = level2[j]
          x.append(coord[0]) #level1[i][j][0]
          y.append(coord[1]) #level1[i][j][1]
          
  elif feature['geometry']['type'] == 'MultiPolygon':  
    level1 = feature['geometry']['coordinates']
    for i in range(len(level1)):     
      level2 = level1[i]
      for j in range(len(level2)):    
        level3 = level2[j]    
        for k in range(len(level3)):
          coord = level3[k]
          x.append(coord[0]) #level1[i][j][k][0]
          y.append(coord[1]) #level1[i][j][k][1]
  
  return [min(x), max(y), max(x), min(y)]

def run_cmd(cmd):
  print(cmd)
  subprocess.call(cmd, shell=True)




#############################################################################################################
#############################################################################################################
#############################################################################################################

# inputs
vrtDir = '/vol/v2/conus_tiles/vrts/'
vrtName = 'lt_ee_conus_nbr_20170417'
clipFile = '/vol/v1/proj/cms/womi/vector/cms_womi_aoi_epsg5070_buffer150m.geojson'
tileFile = '/vol/v1/general_files/datasets/spatial_data/conus_tile_system/conus_tile_system_15_sub_epsg5070.geojson'
outDir = '/vol/v1/proj/cms/womi/raster/lt_seg/'
outName = 'cms_womi'
setOutBoundsZero = 1
doFTV = 1

# check dir paths
if vrtDir[-1] != '/':
  vrtDir += '/'
  
if outDir[-1] != '/':
  outDir += '/'  

if not os.path.exists(outDir):
    os.makedirs(outDir)

# make a list of VRT types to work with depending on whether FTV was requested
vrtTypes = ['vert_yrs.vrt',
         'vert_fit.vrt']
  
# add in the FTV files if requested       
if doFTV == 1:
  vrtTypes += ['ftv_tcb.vrt',
           'ftv_tcg.vrt',
           'ftv_tcw.vrt']

# make a list of output types
outFiles = [outDir+outName+'_'+thisType.replace('.vrt', '.bsq') for thisType in vrtTypes]

# find the VRT files for the types previously defined
vrts = [glob(vrtDir+vrtName+'*'+thisType)[0] for thisType in vrtTypes]
if len(vrts) != len(vrtTypes):
  print('Error - did not find all the files types needed') 
  raise SystemExit

# load the feature file that defines the cropping bounds
with open(clipFile) as f:
  features = json.load(f)

# get the bounds of the feature as a -projwin argument to gdal_translate
feature = features['features'][0]
bounds = get_feature_bounds(feature)
projwin = ' '.join([str(coord) for coord in bounds])

# loop through and create spatial subsets for all the data types
for i in range(len(vrtTypes)):  
  cmd = 'gdal_translate -q --config GDAL_DATA "/usr/lib/anaconda/share/gdal" -of ENVI -projwin '+projwin+' '+ vrts[i] + ' ' + outFiles[i]  
  run_cmd(cmd)

# loop through and set background values for all the data types
for outFile in outFiles:
  nBands = gdal.Open(outFile).RasterCount
  bands = ' '.join(['-b '+str(band) for band in range(1,nBands+1)])
  cmd = 'gdal_rasterize -i -burn 0 '+bands+' '+clipFile+' '+outFile
  run_cmd(cmd)

