import cv2 as cv
import argparse
import cv2 as cv
import numpy as np
import glob
import os
import time
import sys

from colorama import Fore, init, deinit, Style, Back
from faure_utils import string_param, bye, image
# ======================== Section reserved for functions for HSV adjustement of image thresholding ======================== #

# This program allows to create one or two HSV mask for the whole one or two set of images in dynamic way with a GUI. 
# Therefore the mask will be applied to each and every images regardless the efficacity of the mask, expect if it has the defalut values.
# Mask in RGB and Graysacle color will be created according to the image name, and will be saved into the 'Masque' folder which will be created isinde the folder you entered in command line. 

# ======================== Section reserved for functions for HSV adjustement of image thresholding ======================== #


init()
control = True

if len(sys.argv) == 2:																				#Checking here the fact that two system arguments are inputed while laucnhing the program.
	main_folder_path = sys.argv[1]
	main_folder_path = string_param.suppress_string_char(main_folder_path,"--")

	# ======================== Section reserved for functions for HSV adjustement of image thresholding ======================== #

	max_value = 255
	max_value_H = 360//2
	low_H = 0
	low_S = 0
	low_V = 0
	high_H = max_value_H
	high_S = max_value
	high_V = max_value

	window_capture_name = 'Video Capture'
	window_detection_name = 'Object Detection'
	low_H_name = 'Low H'
	low_S_name = 'Low S'
	low_V_name = 'Low V'
	high_H_name = 'High H'
	high_S_name = 'High S'
	high_V_name = 'High V'

	def on_low_H_thresh_trackbar(val):
	    global low_H
	    global high_H
	    low_H = val
	    low_H = min(high_H-1, low_H)
	    cv.setTrackbarPos(low_H_name, window_detection_name, low_H)

	def on_high_H_thresh_trackbar(val):
	    global low_H
	    global high_H
	    high_H = val
	    high_H = max(high_H, low_H+1)
	    cv.setTrackbarPos(high_H_name, window_detection_name, high_H)

	def on_low_S_thresh_trackbar(val):
	    global low_S
	    global high_S
	    low_S = val
	    low_S = min(high_S-1, low_S)
	    cv.setTrackbarPos(low_S_name, window_detection_name, low_S)

	def on_high_S_thresh_trackbar(val):
	    global low_S
	    global high_S
	    high_S = val
	    high_S = max(high_S, low_S+1)
	    cv.setTrackbarPos(high_S_name, window_detection_name, high_S)

	def on_low_V_thresh_trackbar(val):
	    global low_V
	    global high_V
	    low_V = val
	    low_V = min(high_V-1, low_V)
	    cv.setTrackbarPos(low_V_name, window_detection_name, low_V)

	def on_high_V_thresh_trackbar(val):
	    global low_V
	    global high_V
	    high_V = val
	    high_V = max(high_V, low_V+1)
	    cv.setTrackbarPos(high_V_name, window_detection_name, high_V)


	def bg_settings(image_path):
	    cv.namedWindow(window_capture_name)
	    cv.namedWindow(window_detection_name)
	    cv.createTrackbar(low_H_name, window_detection_name , low_H, max_value_H, on_low_H_thresh_trackbar)
	    cv.createTrackbar(high_H_name, window_detection_name , high_H, max_value_H, on_high_H_thresh_trackbar)
	    cv.createTrackbar(low_S_name, window_detection_name , low_S, max_value, on_low_S_thresh_trackbar)
	    cv.createTrackbar(high_S_name, window_detection_name , high_S, max_value, on_high_S_thresh_trackbar)
	    cv.createTrackbar(low_V_name, window_detection_name , low_V, max_value, on_low_V_thresh_trackbar)
	    cv.createTrackbar(high_V_name, window_detection_name , high_V, max_value, on_high_V_thresh_trackbar)

	    frame = cv.imread(image_path)
	    frame = cv.resize(frame,(int(frame.shape[1]/6),int(frame.shape[0]/6)))

	    while True:        
	        if frame is None:
	            break

	        frame_HSV = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
	        frame_threshold = cv.inRange(frame_HSV, (low_H, low_S, low_V), (high_H, high_S, high_V))
	        
	        cv.imshow(window_capture_name, frame)
	        cv.imshow(window_detection_name, frame_threshold)
	        key = cv.waitKey(30)

	        if key == ord('q') or key == 27:
	            cv.destroyAllWindows()
	            break

	    return (low_H, low_S, low_V), (high_H, high_S, high_V)

	# ======================== End of definitions for adjustement of image thresholding ======================== #

	# ======================== Section for selecting the right settings for each or both cams ======================== #

	print(Fore.BLUE + Back.WHITE + "\n Your settings will be saved once you quit the adjustment window... ")
	print(Fore.BLUE + Back.WHITE + " To quit the adjustment window just press 'q'... \n")
	print(Style.RESET_ALL)

	os.chdir(main_folder_path)

	folder_list = glob.glob("*_1")															#This part to the if condition allows to set the HSV threshold values with an image inside the first folder detected, or directly for images inside that folder
	if len(folder_list) != 0:
		image_folder_path = main_folder_path + "/" + folder_list[0]
		os.chdir(image_folder_path)
		image_list_1 = glob.glob("*camera_1*")
		image_list_2 = glob.glob("*camera_2*")
	elif len(folder_list) == 0:
		image_list_1 = glob.glob("*camera_1*")
		image_list_2 = glob.glob("*camera_2*")

	image_file_1 = image_list_1[0]
	image_file_2 = image_list_2[0]
	low_bound_cam1, high_bound_cam1 = bg_settings(image_file_1)
	default_low, default_high = (0,0,0), (180,255,255)


	if low_bound_cam1 == default_low and high_bound_cam1 == default_high:
		print(" //!\\\\ You have saved the default parameters for camera 1 images... //!\\\\ ")
		decision = input("Do you wish to continue ? [y/n] ")
		decision_control = True
		while decision_control == True:
			if decision == 'n':
				control_1 = False
				decision_control = False
			elif decision =='y':
				control_1 = True
				decision_control = False
			else:
				print("\nWrong input, please answer correctly...")
				decision = input("Do you wish to continue ? [y/n] ")
	else:
		print(f"\nYou have saved this parameters for camera 1 : \n\t Hue : ranging {low_bound_cam1[0]}-{high_bound_cam1[0]} \n\t Saturation : ranging {low_bound_cam1[1]}-{high_bound_cam1[1]} \n\t Value : ranging {low_bound_cam1[2]}-{high_bound_cam1[2]}\n")

	decision = input("Do you want other settings for the lower camera ? [y/n] ")
	print(Style.RESET_ALL)
	decision_control = True

	while decision_control == True:
		if decision == 'n':
			control_2 = False
			decision_control = False
		elif decision =='y':
			control_2 = True
			decision_control = False
		else:
			print("Wrong input, please answer correctly...")
			decision = input("Do you wish to continue ? [y/n] ")

	if control_2 == True:
		print(Fore.BLUE + Back.WHITE + "\n Your settings will be saved once you quit the adjustment window... ")
		print(Fore.BLUE + Back.WHITE + " To quit the adjustment window just press 'q'... \n")
		print(Style.RESET_ALL)
		low_bound_cam2, high_bound_cam2 = bg_settings(image_file_2)
	elif control_2 == False:
		low_bound_cam2 = low_bound_cam1
		high_bound_cam2 = high_bound_cam1

	if low_bound_cam2 == default_low and high_bound_cam2 == default_high:
		print(" //!\\\\ You have saved the default parameters for camera 2 images... //!\\\\ ")
		decision = input("Do you wish to continue ? [y/n] ")
		decision_control = True
		while decision_control == True:
			if decision == 'n':
				control = False
				decision_control = False
			elif decision =='y':
				control = True
				decision_control = False
			else:
				print("\nWrong input, please answer correctly...")
				decision = input("Do you wish to continue ? [y/n] ")
	else:
		print(f"\nYou have saved this parameters for camera 2: \n\t Hue : ranging {low_bound_cam2[0]}-{high_bound_cam2[0]} \n\t Saturation : ranging {low_bound_cam2[1]}-{high_bound_cam2[1]} \n\t Value : ranging {low_bound_cam2[2]}-{high_bound_cam2[2]}\n")

	# ======================== End of section for selecting the image parameters thresholding ======================== #

	# remember to check for control_1 and control_2 boolean value before entering thresholding section ! if both are default values, end program
	# maybe use a try/except method ?

	# ======================== Section for thresholding the images ======================== #

	timer_start = time.time()
	image_count = 0

	program_directory = os.getcwd()
	os.chdir(main_folder_path)
	
	if os.path.isdir("Masque") == False: 					#Vérification de l'existence du dossier "Tiff_panorama" et de son contenu
		print("Création du dossier 'Masque' ...")
		os.makedirs("Masque")

	output_folder = main_folder_path + '/Masque'

	os.chdir(main_folder_path)
	folder_list = glob.glob("*_1")							#Detecting if sub folders are present.
	image_list = glob.glob("*camera*")						#Detecting if images are present.

	if control == True and control_1 == True:				#Condition if the threshold settings are decided to be save.
		if len(folder_list) != 0:							#Entering the loop if folders are detected
			for folder in folder_list:

				print(f"Folder currently processed : {folder}")
				image_folder_path = main_folder_path + "/" + folder
				os.chdir(image_folder_path)											#while in folder loop, changing directory to the directory to be processed.
				image_list_1 = glob.glob("*camera_1*")								#Spliting the images in two diffeent list according to their corresponding camera.
				image_list_2 = glob.glob("*camera_2*")
				image_count += len(image_list_1) + len(image_list_2)				

				for image in image_list_1:

					os.chdir(image_folder_path)
					current_image_adress = image_folder_path + "/" + image
					current_image = cv.imread(current_image_adress, cv.IMREAD_UNCHANGED)					#reading the image

					current_image_HSV = cv.cvtColor(current_image, cv.COLOR_BGR2HSV)						#switching the colorspace of the image from RGB to HSV
					thresholded_image = cv.inRange(current_image_HSV, low_bound_cam1, high_bound_cam1)		#Retrieve the thresholded image in grayscale.

					img_type = current_image.dtype															#According to the image type, retrieve the max value, actually useless cause all the images HAVE to be in a jpg format.
					if img_type == 'uint8':
						maxi = 255
					elif img_type =='uint16':
						maxi = 65535

					image_without_bg = np.zeros_like(current_image) 										# Setting array full of maxi value
					image_without_bg_good_colors = np.full_like(current_image,maxi) 						# Setting array full of maxi value

					for i in range (0,3,1):
						image_without_bg[:,:,i] = thresholded_image * current_image[:,:,i]					#For the HSV image, simply multiply the mask and the image to get an rgb image without the background.

					image_without_bg_good_colors = image_without_bg_good_colors - image_without_bg 			#Creating the good colors (RGB) from the HSV image.
					image_without_bg_good_colors[image_without_bg_good_colors[:,:,:] == maxi] = 0 			#Simply converting every white pixel into a black pixel. Not the best solution, every saturated pixel is automatically considered as background with this method, improvement has to be made.

					#thresholded_image = cv.rotate(thresholded_image, cv.ROTATE_180)
					#image_without_bg_good_colors = cv.rotate(image_without_bg_good_colors, cv.ROTATE_180)	

					os.chdir(output_folder)

					prename_th = string_param.suppress_string_char(image,".jpg")
					name_th = prename_th + '_TH.jpg'
					prename_bg = string_param.suppress_string_char(image,".jpg")
					name_bg = prename_bg + '_BG.jpg'
					cv.imwrite(name_th,thresholded_image)													#Saving the images with a flag into their name according if they are a black and white mask or a RGb image with no background.
					cv.imwrite(name_bg,image_without_bg_good_colors)

				for image in image_list_2:																	#Same process as describe for the previous image list.

					os.chdir(image_folder_path)
					current_image_adress = image_folder_path + "/" + image
					current_image = cv.imread(current_image_adress, cv.IMREAD_UNCHANGED)

					current_image_HSV = cv.cvtColor(current_image, cv.COLOR_BGR2HSV)
					thresholded_image = cv.inRange(current_image_HSV, low_bound_cam2, high_bound_cam2)

					img_type = current_image.dtype
					if img_type == 'uint8':
						maxi = 255
					elif img_type =='uint16':
						maxi = 65535

					image_without_bg = np.zeros_like(current_image) 				# Setting array full of maxi value
					image_without_bg_good_colors = np.full_like(current_image,maxi) # Setting array full of maxi value

					for i in range (0,3,1):
						image_without_bg[:,:,i] = thresholded_image * current_image[:,:,i]

					image_without_bg_good_colors = image_without_bg_good_colors - image_without_bg
					image_without_bg_good_colors[image_without_bg_good_colors[:,:,:] == maxi] = 0

					#thresholded_image = cv.rotate(thresholded_image, cv.ROTATE_180)
					#image_without_bg_good_colors = cv.rotate(image_without_bg_good_colors, cv.ROTATE_180)	

					os.chdir(output_folder)

					prename_th = string_param.suppress_string_char(image,".jpg")
					name_th = prename_th + '_TH.jpg'
					prename_bg = string_param.suppress_string_char(image,".jpg")
					name_bg = prename_bg + '_BG.jpg'
					cv.imwrite(name_th,thresholded_image)
					cv.imwrite(name_bg,image_without_bg_good_colors)



		elif len(image_list) != 0:																			#Loop if the folder is only composed of images. The process is exactly the same as describe before.

			print("Only images in this folder, begin image processing...")
			image_list_1 = glob.glob("*camera_1*")
			image_list_2 = glob.glob("*camera_2*")
			image_count1 = 0
			image_count += len(image_list_1) + len(image_list_2)

			for image in image_list_1:
				
				image_count1 += 1
				if image_count1 % 4 == 0:
					print(f"{image_count1} images processed so far, still going...")
				os.chdir(main_folder_path)
				current_image_adress = main_folder_path + "/" + image
				current_image = cv.imread(current_image_adress, cv.IMREAD_UNCHANGED)

				current_image_HSV = cv.cvtColor(current_image, cv.COLOR_BGR2HSV)
				thresholded_image = cv.inRange(current_image_HSV, low_bound_cam1, high_bound_cam1)

				img_type = current_image.dtype
				if img_type == 'uint8':
					maxi = 255
				elif img_type =='uint16':
					maxi = 65535

				image_without_bg = np.zeros_like(current_image) 				# Setting array full of maxi value
				image_without_bg_good_colors = np.full_like(current_image,maxi) # Setting array full of maxi value

				for i in range (0,3,1):
					image_without_bg[:,:,i] = thresholded_image * current_image[:,:,i]

				image_without_bg_good_colors = image_without_bg_good_colors - image_without_bg
				image_without_bg_good_colors[image_without_bg_good_colors[:,:,:] == maxi] = 0

				#thresholded_image = cv.rotate(thresholded_image, cv.ROTATE_180)
				#image_without_bg_good_colors = cv.rotate(image_without_bg_good_colors, cv.ROTATE_180)	

				os.chdir(output_folder)

				prename_th = string_param.suppress_string_char(image,".jpg")
				name_th = prename_th + '_TH.jpg'
				prename_bg = string_param.suppress_string_char(image,".jpg")
				name_bg = prename_bg + '_BG.jpg'
				cv.imwrite(name_th,thresholded_image)
				cv.imwrite(name_bg,image_without_bg_good_colors)

			for image in image_list_2:
			
				image_count1 += 1
				if image_count1 % 4 ==0:
					print(f"{image_count1} images processed so far, still going...")
				os.chdir(main_folder_path)
				current_image_adress = main_folder_path + "/" + image
				current_image = cv.imread(current_image_adress, cv.IMREAD_UNCHANGED)

				current_image_HSV = cv.cvtColor(current_image, cv.COLOR_BGR2HSV)
				thresholded_image = cv.inRange(current_image_HSV, low_bound_cam2, high_bound_cam2)

				img_type = current_image.dtype
				if img_type == 'uint8':
					maxi = 255
				elif img_type =='uint16':
					maxi = 65535

				image_without_bg = np.zeros_like(current_image) 				# Setting array full of maxi value
				image_without_bg_good_colors = np.full_like(current_image,maxi) # Setting array full of maxi value

				for i in range (0,3,1):
					image_without_bg[:,:,i] = thresholded_image * current_image[:,:,i]

				image_without_bg_good_colors = image_without_bg_good_colors - image_without_bg
				image_without_bg_good_colors[image_without_bg_good_colors[:,:,:] == maxi] = 0

				#thresholded_image = cv.rotate(thresholded_image, cv.ROTATE_180)
				#image_without_bg_good_colors = cv.rotate(image_without_bg_good_colors, cv.ROTATE_180)	

				os.chdir(output_folder)

				prename_th = string_param.suppress_string_char(image,".jpg")
				name_th = prename_th + '_TH.jpg'
				prename_bg = string_param.suppress_string_char(image,".jpg")
				name_bg = prename_bg + '_BG.jpg'
				cv.imwrite(name_th,thresholded_image)
				cv.imwrite(name_bg,image_without_bg_good_colors)


	os.chdir(output_folder)
	output_image_list = glob.glob("*")												#Check the amount of images created.

	timer_end = time.time()
	global_time = timer_end-timer_start
	print("\nProgram took " + str(global_time)+" seconds.")

	if len(folder_list) != 0:
		print(f"It parsed {len(folder_list)} directories.")							#Indicates the number of folder parsed and processed if sub-folders are detected.
	else:
		print(f"It only parsed the main directory.")								#Indicates if only the main folder has been parsed and processed.
	print(f"The program processed {image_count} sample images and created {len(output_image_list)} RGB image and mask out of those samples.")	#Allow to verify the quantity of data processed, help to check if processd and expected to be processed are the same.

	bye.bye()

elif len(sys.argv) < 2:												#Error handling for less system arguments than expected
	print(Fore.RED + Back.WHITE + '\nMissing at least one argument from system command, expected 2, such as : main_HSV_mask.py "--C:\\your\\data\\folder\\path" ')
	print("End of program. ")
elif len(sys.argv) > 2:												#Error handling for more system arguments than expected
	print(Fore.RED + Back.WHITE + '\nToo many arguments from system command, expected 2, such as : main_HSV_mask.py "--C:\\your\\data\\folder\\path"  ')
	print("End of program. ")
