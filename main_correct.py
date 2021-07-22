import cv2 as cv
import numpy as np
import pandas as pd
import time
import shutil
import os
import os.path
import glob
import tifffile as tiff
from colorama import Fore, init, deinit, Style, Back

from faure_utils import string_param
from faure_utils import reshape
from faure_utils import erase
from faure_utils import bye
from distorsion import distorsion

timer_start = time.time()
image_count = 0
correction_matrix_rgb = np.ones((3000,4096,3), dtype = float)
init()
current_directory = os.getcwd()

with open('path.txt') as f:										#Read the path of the main folder where the images will be stored in one of the subfolders, path you entered in main_architecture or main_copy.
	main_folder_path = f.read().splitlines()
	f.close()

main_folder_path = main_folder_path[0]
# Folder where the folders of images are stored.
source_image_folder_path = main_folder_path + "/Tiff_brute"

# Folder where you want your processed images to be stored.
image_output_path = main_folder_path + "/Tiff_corrige"

chessboard_filename = "Test_01_06_1.jpg"         				# Image name to use for distorsion correction.
vignet_matrix_filename = 'correction_matrix.csv'				# CSV filename to use for vigneting correction.

if os.path.isfile(chessboard_filename) == True: 
	chessboard_path = glob.glob(chessboard_filename)    		#retrieving the image, not an elegant way
	chessboard_file = str(chessboard_path[0])					#Useless but still there, chessboard_path[0] is allready a string.
	chessboard = cv.imread(chessboard_file)
	print("Chessboard file reading...")
	ret, mtx, dist, rvecs, tvecs = distorsion.get_Cam_Matrix(chessboard)
else:
	print("\nSample file for distorsion correction not found...\nNo correction will be applied...")


if os.path.isfile(vignet_matrix_filename) == True: 
	csv_file_path = glob.glob(vignet_matrix_filename)   		#retrieving the csv file
	csv_file = str(csv_file_path[0])							#Useless but still there, csv_file_path[0] is allready a string.
	print("CSV file reading...")
	correction_matrix_rgb[:,:,0] = pd.read_csv(csv_file, header = None)
	correction_matrix_rgb[:,:,1], correction_matrix_rgb[:,:,2] = correction_matrix_rgb[:,:,0], correction_matrix_rgb[:,:,0]
else:
	print("CSV file not found...\nNo vigneting correction will be applied...")



os.chdir(source_image_folder_path)
folder_list = glob.glob('*_1')									#Creating folder list for each folder ending with a '_1' string chain.
erase.erase_folder_and_files(image_output_path)
os.chdir(current_directory)

if os.path.isfile(chessboard_file) == True or os.path.isfile(csv_file) == True:
	for folder in folder_list:
		image_path = source_image_folder_path + '/' + folder 	#Creation of the folders adresses
		output_path = image_output_path + '/' + folder

		print("Folder currently processed : " + folder)

		os.chdir(image_path)
		image_list = glob.glob('*.tif') 						#Creation of the tif image list of the current folder
		if len(image_list) == 0:
			image_list = glob.glob('*.jpg')

		os.chdir(image_output_path)
		os.makedirs(folder)										#Creation of the sub-folder output for the processing images
		os.chdir(image_path)

		json_filename = glob.glob('*.json')						#Metadata file copy to new folder
		try:
			shutil.copy(json_filename[0],output_path)
			json = True
		except PermissionError:
			print("Permission denied.")
			json = False
		except:
			print("Erroc occured while copying the JSON file.")
			json = False

		for image in image_list:

			os.chdir(image_path)
			image_to_be_corrected = tiff.imread(image)

			if image_to_be_corrected.shape != correction_matrix_rgb.shape:
				print("Different dimensions between image and matrix, starting image resize processus ...")
				image_to_be_corrected = reshape.resize(image, correction_matrix_rgb.shape[:])

			image_corrected = image_to_be_corrected									#Copying the image array into another
			image_corrected = (image_to_be_corrected * correction_matrix_rgb)		#Mathematical operation of the image, size dependent of the input csv matrix
			#quantile = np.quantile(image_corrected,0.99)							#Calculating the outliers for a raw estimation of abberation created, to use when experimenting with the matrix
			#if quantile > 65535*0.99:
			#	print(f"Quantile = {quantile}")
			image_corrected[image_corrected[:,:,:] > 65535] = 65535					#Outlier thresholding, converting the pixel triplet over 65535 into white pixels 
			image_corrected = np.uint16(image_corrected)							#Making the array a 16-bit int array.
			

			os.chdir(current_directory)
			if os.path.isfile(csv_file) == True:
				corrected_name = string_param.suppress_string_char(image,'.tif')	#Getting rid of the file extension name
				new_name = corrected_name + "_V.tif"								#Adding "_V" to filename for a fast read information of vigneting effect corrected.
			if os.path.isfile(chessboard_file) == True:
				if os.path.isfile(csv_file) == False:
					new_name = image			
				new_name, image_corrected = distorsion.get_undistort_image(image_corrected, new_name,mtx, dist, output_path) 	#Retrieving from distorsion library the corrected matrix of its distorsion effect AND adding "_U" to filename for a fast read information of undistortion.
			os.chdir(output_path)
			tiff.imwrite(new_name,image_corrected)
			image_count += 1

timer_end = time.time()
global_time = timer_end-timer_start
print("\nProgram took " + str(global_time)+" seconds to fix vignetting effect and distorsion on "+ str(image_count) +" images.")
os.chdir(current_directory)

# Section for raising alert with colorama
if os.path.isfile(chessboard_file) == False and os.path.isfile(csv_file) == False:
	print(Fore.RED + Back.WHITE + "\n//!\\\\ Be careful, none of your files have been used. The program did nothing to your images... //!\\\\\n")
elif os.path.isfile(chessboard_file) == True and os.path.isfile(csv_file) == False:
	print(Fore.RED + Back.WHITE + "\n//!\\\\ Be careful, the csv file for the vigneting correction have not been used (file not found), The program did only half of its job... //!\\\\\n")
elif os.path.isfile(chessboard_file) == False and os.path.isfile(csv_file) == True:
	print(Fore.RED + Back.WHITE + "\n//!\\\\ Be careful, the chessboard image for the distorsion correction have not been used (file not found), The program did only half of its job... //!\\\\\n")
print(Style.RESET_ALL)
deinit()

bye.bye()
