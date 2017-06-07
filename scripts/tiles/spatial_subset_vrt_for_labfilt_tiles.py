# -*- coding: utf-8 -*-
"""
Created on Mon May  1 10:44:41 2017

@author: braatenj
"""

import json
import subprocess
from glob import glob
import os
import multiprocessing



def get_bounds(feature, buff):
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
  
  return [min(x)-buff, max(y)+buff, max(x)+buff, min(y)-buff]


def get_tile_id(tile):
    idNum = tile['properties']['id']
    if idNum < 10: 
      idStr = '000'+str(idNum)
    elif idNum < 100: 
      idStr = '00'+str(idNum)
    elif idNum < 1000: 
      idStr = '0'+str(idNum)
    else:
      idStr = str(idNum)
    
    return idStr
    

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
tileFile = '/vol/v1/proj/cms/womi/vector/cms_womi_aoi_epsg_tiles.geojson'
outDir = '/vol/v1/proj/cms/womi/raster/tiles_seg/'
setOutBoundsZero = 1
doFTV = 1

# check dir paths for proper end and existence - make is not
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

# find the VRT files for the types previously defined
vrts = [glob(vrtDir+vrtName+'*'+thisType)[0] for thisType in vrtTypes]
if len(vrts) != len(vrtTypes):
  print('Error - did not find all the files types needed') 
  raise SystemExit

# open the geojson tile file and pull the features out
with open(tileFile) as f:
  tiles = json.load(f)

tiles = tiles['features']

# loop through the features pulling out the bounds and the tile ID 
tileInfo = {'tileID':[], 'projwin':[]}
for i in range(len(tiles)):
  tileID = get_tile_id(tiles[i])  
  bounds = get_bounds(tiles[i], 300)
  projwin = ' '.join([str(coord) for coord in bounds])
  tileInfo['tileID'].append(tileID)
  tileInfo['projwin'].append(projwin)

# loop through and create spatial subsets for all the data types
cmds = []
for i in range(len(tileInfo['projwin'])):  
  for j in range(len(vrtTypes)):
    tileID = tileInfo['tileID'][i]
    outFile = outDir+tileID+'/'+tileID+'_'+os.path.basename(vrts[j]).replace('.vrt', '.bsq')
    outFileDir = os.path.dirname(outFile)
    if not os.path.exists(outFileDir):
      os.makedirs(outFileDir)
    cmd = 'gdal_translate -q --config GDAL_DATA "/usr/lib/anaconda/share/gdal" -of ENVI -projwin '+tileInfo['projwin'][i]+' '+ vrts[j] + ' ' + outFile 
    cmds.append(cmd)


# run the commands in parallel 
pool = multiprocessing.Pool(processes=3)
pool.map(run_cmd, cmds)  
pool.close()



#for outFile in outFiles:
#  nBands = gdal.Open(outFile).RasterCount
#  bands = ' '.join(['-b '+str(band) for band in range(1,nBands+1)])
#  cmd = 'gdal_rasterize -i -burn 0 '+bands+' '+clipFile+' '+outFile
#  run_cmd(cmd)

