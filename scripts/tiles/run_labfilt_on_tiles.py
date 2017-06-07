# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 16:46:10 2017

@author: braatenj
"""



from glob import glob
import subprocess
import multiprocessing


def run_cmd(cmd):
  print(cmd)
  subprocess.call(cmd, shell=True)

  
#################################################################################################### 
####################################################################################################
####################################################################################################

tileDir = '/vol/v1/proj/cms/womi/raster/tiles_seg'
LTlabFiltParams = '/vol/v1/proj/cms/womi/scripts/label_filter_params.txt'
LTlabFiltStatic = '/vol/v1/code/landtrendr/EE_LT-IDL_patchify/scripts/lt_label_batch_static.txt'
runFileDir = '/vol/v1/proj/cms/womi/scripts/lt_labfilt_run_files/'


paths = glob(tileDir+'/*/')

cmds = []
for inPath in paths:
  tileID = inPath.split('/')[-2]
  outPath = inPath.replace('tiles_seg', 'tiles_label')
  paramFile = runFileDir+tileID+'_labfilt_runfile.pro'
  
  fn = open(paramFile, 'w') 
  fn.write(str('in_path = "'+inPath+'"\n'))  
  fn.write(str('out_path = "'+outPath+'"\n'))

  filenames = [LTlabFiltParams, LTlabFiltStatic]
  for fname in filenames:
      with open(fname) as infile:
          fn.write(infile.read())

  fn.close() 

  cmds.append('idl -e @'+paramFile)


#subprocess.call(cmd, shell=True)

# run the commands in parallel 
pool = multiprocessing.Pool(processes=10)
pool.map(run_cmd, cmds)  
pool.close()