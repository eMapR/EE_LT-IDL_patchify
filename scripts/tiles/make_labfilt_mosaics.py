# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 16:46:10 2017

@author: braatenj
"""


import subprocess
import os
import fnmatch
import json


def get_feature_bounds(feature):
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


  
#################################################################################################### 
####################################################################################################
####################################################################################################

tileDir = '/vol/v1/proj/cms/womi/raster/tiles_label'
fileSearch = ['*lt_ee_conus_nbr_20170417_greatest_disturbance_mmu11_tight.bsq']
descript = 'cms_womi'
outDir = '/vol/v1/proj/cms/womi/raster/mosaics_label/'
clipFile = '/vol/v1/proj/cms/womi/vector/cms_womi_aoi_epsg5070_buffer150m.geojson'

#################################################################################################### 
####################################################################################################
####################################################################################################


bandNames = ['yod',
             'mag',
             'dur',
             'preval',
             'postyr',
             'postmag',
             'postdur',
             'postval']

# make sure dirname is proper
if outDir[-1] != '/':
  outDir += '/'

# make dir if not exist
if not os.path.isdir(outDir):
  os.mkdir(outDir)

# loop through the files requested for mosaicing
for search in fileSearch:
  # find the tile files
  files = []
  for root, dirnames, filenames in os.walk(tileDir):
    for filename in fnmatch.filter(filenames, search):
      files.append(os.path.join(root, filename))
  # make a list of tile bsqs 
  fileBase = search.replace('*','').replace('.bsq','')
  tileListFile = outDir+descript+'_filelist_'+fileBase+'.txt'
  tileList = open(tileListFile, 'w')
  
  # make a tile file list for building a vrt  
  for fn in files:
    tileList.write(fn+'\n')
  tileList.close()

  # load the feature file that defines the cropping bounds
  with open(clipFile) as f:
    features = json.load(f)
  
  # get the bounds of the feature as a -projwin argument to gdal_translate
  feature = features['features'][0]
  bounds = get_feature_bounds(feature)
  projwin = ' '.join([str(coord) for coord in bounds])
  
  #loop through the bands to make mosaics of each
  for band, bandName in zip(range(1,8),bandNames):  
    outFileVRT = outDir+descript+'_mosaic_'+fileBase+'_'+bandName+'.vrt'
    cmd = 'gdalbuildvrt -input_file_list '+tileListFile+' -b '+str(band)+' '+outFileVRT
    subprocess.call(cmd, shell=True)
    
    outFileBSQ = outFileVRT.replace('.vrt', '.bsq')
    #cmd = 'gdal_translate -ot Int16 -of ENVI '+outFileVRT+' '+outFileBSQ
    cmd = 'gdal_translate -q --config GDAL_DATA "/usr/lib/anaconda/share/gdal" -of ENVI -projwin '+projwin+' '+ outFileVRT + ' ' + outFileBSQ
    subprocess.call(cmd, shell=True)

    cmd = 'gdal_rasterize -i -burn 0 '+clipFile+' '+outFileBSQ
    subprocess.call(cmd, shell=True)

  # TODO could delete the vrt and tile file txt 