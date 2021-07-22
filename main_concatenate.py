import numpy as np
import os
import time
import glob
import tifffile as tiff

from colorama import Fore, init, deinit, Style, Back
from faure_utils import erase, bye, string_param


init()
control = False
print_recap_values = False
timer_start = time.time()


with open('path.txt') as f:									#Read the path of the main folder where the images will be stored in one of the subfolders, path you entered in main_architecture or main_copy.
	data_path = f.read()
	f.close()

source_image_folder_path = data_path + "/Tiff_corrige"
panorama_output_path = data_path + "/Tiff_panorama"
#erase.erase_files(panorama_output_path)

os.chdir(data_path)
if os.path.isdir("Tiff_panorama") == True: 					#Vérification de l'existence du dossier "Tiff_panorama" et de son contenu
	os.chdir(panorama_output_path)
	file_presence1 = glob.glob("*")
	if len(file_presence1) != 0:							#Raise a warning if any file are detected inside this specific folder.
		control = True
		print(Fore.RED + Back.WHITE + "\n //!\\\\Attention, le dossier 'Tiff_panorama' contient des données, veuillez les supprimer et relancez le programme. ")
		print(Style.RESET_ALL)
else:
	print("Création du dossier 'Tiff_panorama' ...")
	os.makedirs("Tiff_panorama")


os.chdir(source_image_folder_path)

folder_list = glob.glob('*_1')								#Creating folder list for each folder ending with a '_1' string chain.
folder_number = 0

if control == False:
	print_recap_values = True
	print("")
	for folder in folder_list:

		folder_number += 1
		if folder_number % 4.0 == 0:
			print(f"Allready {folder_number} folder processed, remaining {str(len(folder_list)-folder_number)}.")

		current_folder_path = source_image_folder_path + "/" + folder
		os.chdir(current_folder_path)

		image_cam1_list = sorted(glob.glob('*camera_1*'))		#Spliting the top camera from the lower one.
		image_cam2_list = sorted(glob.glob('*camera_2*'))
		panorama_1, panorama_2 = None, None

		for i in range(1, len(image_cam1_list), 1):				#Processing the first camera images. Only load two images at once.
			image_2 = tiff.imread(image_cam1_list[i])
					
			if panorama_1 is not None:
				panorama_1 = np.concatenate((image_2,panorama_1), axis = 1)

			if panorama_1 is None:
				image_1 = tiff.imread(image_cam1_list[0])
				panorama_1 = np.concatenate((image_2,image_1), axis = 1)

		folder_name_1 = string_param.suppress_string_char(folder,"_1")
		name_1 = folder_name_1 + '_camera_1.tif'				#Saving the image with a right name, lacking information about _U _V _RGB _WB, maybe to be added later.
		os.chdir(panorama_output_path)
		tiff.imwrite(name_1,panorama_1)							#Saving the concatenated image as a Tiff, pretty much a big file at this moment.
		os.chdir(current_folder_path)

		for i in range(1, len(image_cam2_list), 1):				#Processing the second camera images. Same thing as for the previous camera list
			image_2 = tiff.imread(image_cam2_list[i])
					
			if panorama_2 is not None:
				panorama_2 = np.concatenate((image_2,panorama_2), axis = 1)

			if panorama_2 is None:
				image_1 = tiff.imread(image_cam2_list[0])
				panorama_2 = np.concatenate((image_2,image_1), axis = 1)

		folder_name_2 = string_param.suppress_string_char(folder,"_1")
		name_2 = folder_name_2 + '_camera_2.tif'
		os.chdir(panorama_output_path)
		tiff.imwrite(name_2,panorama_2)

os.chdir(panorama_output_path)
panorama_list = glob.glob("*.tif")

timer_end = time.time()
global_time = timer_end-timer_start
print("\nProgram completion took " + str(global_time) + " seconds")

if print_recap_values == True:
	print(f"Number of folders listed : {len(folder_list)} ")
	print(f"Number of panorama created : {len(panorama_list)} ")
	print(f"Number of panorama expected : {str(2*len(folder_list))} \n")

deinit()
bye.bye()