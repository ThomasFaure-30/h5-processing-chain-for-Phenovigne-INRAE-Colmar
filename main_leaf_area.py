import os
import glob
import time
import sys
import cv2 as cv
import csv

from colorama import Fore, init, deinit, Style, Back
from faure_utils import bye, image, string_param
init()

# ============ Program supposely to only works for a folder containing images with "TH" in name  ============ #
if len(sys.argv) == 2:																				#Checking here the fact that two system arguments are inputed while laucnhing the program. 

	image_count = 0
	folder_count =0
	timer_start = time.time()
	current_directory = os.getcwd()
	main_folder_path = sys.argv[1]
	main_folder_path = string_param.suppress_string_char(main_folder_path,"--")
	os.chdir(main_folder_path)

	if os.path.isfile('results.txt') == True: 														#Checking the presence of the 'results.txt' file, creation is automatically made when opening it if it does  ot exist.
		print("File 'results.txt' found...\n")
	else:
		print("File 'results.txt' not found, begin creation of the file...\n")
		
	header = 'Nom', "Population", "PU", "Orientation", '%Leaf area', '%BG area'
	with open('results.txt', mode = 'w+', newline ='') as csvfile:									#Writing the headers for the wannabe csv file. the 'w+' mode automatically ERASE all the contents inside the file if it allready existed.
		writer = csv.writer(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)

	folder_list = glob.glob("*_1")																	#Identifying the difference between a folder of sub folders or a folder of images.
	if len(folder_list) == 0:
		folder_list_control = False
	elif len(folder_list) != 0:
		folder_list_control = True

	image_list = glob.glob("*BG*")
	if len(image_list) == 0:
		image_list_control = False
	elif len(image_list) != 0:
		image_list_control = True


	if folder_list_control == True:																	#Processing for a folder of subfolder
		for folder in sorted(folder_list):
			folder_count += 1
			if folder_count % 2 == 0:
				print(f"There has been {folder_count} folders processed so far, still going...")	#Counting to indicate that the program is still successfully processing the folders 

			image_folder_path = main_folder_path + '/' + folder
			os.chdir(image_folder_path)

			image_list = glob.glob("*_BG*")
			image_count += len(image_list)

			for image_name in image_list:
				os.chdir(image_folder_path)
								
				current_image = cv.imread(image_name)
				total_pix = current_image.shape[1] * current_image.shape[0]							#Retrieving the number of pixels of the images using the dimensions of the array (image). 
				black_pix = int((current_image == 0).sum()/3)										#Counting all the 0 pixels value in each channel (then divided by 3 of course...).
				white_pix = total_pix - black_pix													#Counting everything which is not a balck pixel.
				leaf_area_percent = float((white_pix )/total_pix)*100								#Percentage of everything which is not a black pixel over the overall pixel number of the image, considered as leaf area.
				bg_area_percent = float((black_pix )/total_pix)*100									#Percentage of background over the total pixels.
				
				plot = string_param.get_plot(image_name) 											#definition created to retrieve plot number from image name with name such as : uplot_32201002_camera_2_1_RGB_WB_V_U_TH.jpg
				population = string_param.get_population(plot)										#return the population of the Plot ID

				presence_1 = image_name.count('001_')												#Identifying the orientation of the plot, count return 1 if the string chain is found in the name.
				presence_2 = image_name.count('002_')
				if presence_1 != 0:
					orientation = "Nord"
				elif presence_2 != 0:
					orientation = "Sud"
				elif presence_1 == 0 and presence_2 == 0:
					orientation = "Na"

				os.chdir(main_folder_path)
				with open('results.txt', mode = 'a+', newline ='') as csvfile:						#Write the 5 informations for each image processed, 'a+' allows to append a new line each time it is run.
					writer = csv.writer(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
					writer.writerow([image_name, population, plot, orientation, leaf_area_percent, bg_area_percent])

	if image_list_control == True:																	#Same process as before but for a folder of images.
		for image_name in sorted(image_list):
			image_count += 1
			if image_count % 4 == 0:
				print(f"There has been {image_count} images processed so far, still going...")
			os.chdir(main_folder_path)

			current_image = cv.imread(image_name)
			total_pix = current_image.shape[1] * current_image.shape[0]
			black_pix = int((current_image == 0).sum()/3)
			white_pix = total_pix - black_pix
			leaf_area_percent = float((white_pix )/total_pix)*100
			bg_area_percent = float((black_pix )/total_pix)*100
			
			plot = string_param.get_plot(image_name) 				#definition created to retrieve plot number from image name with name such as : uplot_32201002_camera_2_1_RGB_WB_V_U_TH.jpg
			population = string_param.get_population(plot)			#return the population of the Plot ID

			presence_1 = image_name.count('001_')
			presence_2 = image_name.count('002_')
			if presence_1 != 0:
				orientation = "Nord"
			elif presence_2 != 0:
				orientation = "Sud"
			elif presence_1 == 0 and presence_2 == 0:
				orientation = "Na"

			with open('results.txt', mode = 'a+', newline ='') as csvfile:
				writer = csv.writer(csvfile, delimiter = ';', quotechar = '"', quoting=csv.QUOTE_MINIMAL)
				writer.writerow([image_name, population, plot, orientation, leaf_area_percent, bg_area_percent])

	timer_end = time.time()
	global_time = timer_end - timer_start
	print(f"\nLe programme a calculé la surface foliaire de {image_count} images, ce qui a pris {str(global_time)} secondes.")
	
elif len(sys.argv) < 2:												#Error handling for less system arguments than expected.
	print(Fore.RED + Back.WHITE + '\nMissing at least one argument from system command, expected 2, such as : main_leaf_area.py "--C:\\your\\data\\folder\\path" ')
	print("End of program. ")
elif len(sys.argv) > 2:												#Error handling for more system arguments than expected.
	print(Fore.RED + Back.WHITE + '\nToo many arguments from system command, expected 2, such as : main_leaf_area.py "--C:\\your\\data\\folder\\path"  ')
	print("End of program. ")
