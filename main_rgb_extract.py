"""
Image extraction module

data_path correspond to the folder path where the .h5 files are located.
output_path correspond to the folder where sub-folder will be created 
wb_factors_path correspond to the folder localisation of the white balance factors files
"""

import time
import os
import glob

from rgb_image_extraction import extracting
from faure_utils import erase
from faure_utils import bye
from colorama import Fore, init, deinit, Style, Back

init()
timer_start = time.time()

with open('path.txt') as f:																	#Follow the path you entered in main_architecture or main_copy.
	data_path = f.read().splitlines()
	f.close()

data_path = data_path[0]
output_path = data_path + "/Tiff_brute"
wb_factors_path = os.getcwd()

#Checking which weather occured while imaging, pick the right number according to the weather.
print("\nVous allez devoir rentrer le numéro correspondant à la météo lors de l'acqusition :\n\tMétéo ensoleillée ==>  1\n\tMétéo mixte       ==>  2\n\tMétéo nuageuse    ==>  3\n")
meteo_type = input("Numéro de votre météo : ")
if meteo_type =='1':
	wb_filename = "wb_balance_ensoleillee.csv"
elif meteo_type =='2':
	wb_filename = "wb_balance_mixte.csv"
elif meteo_type =='3':
	wb_filename = "wb_balance_nuageuse.csv"
else:
	wb_filename = None
	print(Fore.RED + Back.WHITE + "Attention, vous n'avez pas choisi de balance des blancs.")
	print(Style.RESET_ALL)
	deinit()
print(f"La balance des blancs que vous avez choisi est celle-ci : {wb_filename}")


erase.erase_folder_and_files(output_path)

os.chdir(data_path)
h5_list = glob.glob('*.h5')

for h5_file in h5_list:
	
	extracting.get_rgb_image(h5_file,data_path,output_path,wb_factors_path,wb_filename)			#Call the rgb_image_extraction library to extract the images from each h5 file.
	os.chdir(data_path)
	
timer_end = time.time()

print("\nThe "+ str(len(h5_list)) +" .h5 archives for images extraction took " + str(int(timer_end - timer_start)) + " seconds.\n")

bye.bye()
