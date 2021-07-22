"""
LiDAR extraction module

"""

import time
import os
import glob

from lidar_extract import extracting
from faure_utils import bye,erase,string_param

timer_start = time.time()
count = 0

with open('path.txt') as f:
	data_path = f.read().splitlines()
	f.close()
output_path = data_path[0] + '/LiDAR'

os.chdir(data_path[0])
h5_list = glob.glob('*.h5')

for h5_file in h5_list:
	extracting.get_lidar_files(h5_file,output_path)
	os.chdir(data_path[0])
	count += 6

timer_end = time.time()
global_time = timer_end-timer_start
print(f"\nThe "+ str(len(h5_list)) +" LiDAR files extraction took " + str(global_time) + " seconds and created " + str(count) + "files.")

bye.bye()
