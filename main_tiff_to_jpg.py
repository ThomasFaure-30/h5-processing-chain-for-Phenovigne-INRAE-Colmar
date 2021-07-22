import os
import glob
import cv2 as cv
import time
import sys

from faure_utils import string_param

print("\nCe programme est conçu pour convertir des images au format Tiff vers des images au format jpg.")
print("Il va chercher d'une part, de multiples dossiers dont la terminaison est par '_1', \nou d'autre part directement les fichiers .tif dans le dossier que vous avez indiqué.\n")

if len(sys.argv) == 2:																			#Checking here the fact that two system arguments are inputed while laucnhing the program. 

	main_folder_path = sys.argv[1]
	main_folder_path = string_param.suppress_string_char(main_folder_path,"--")

	if os.path.isdir(main_folder_path) == True: 												#Checking existence of the folder path you inputed in command window.
		print("Dossier principal atteint...")
		data_control = True
	else:
		data_control = False
		print("Erroc occured while tring to reach main folder, probably a wrong adress...")
		print("End of program. ")

	decision = input("Souhaitez vous que les images tif soient supprimées automatiquement ? [y/n] ")
	decision_control = True
	while decision_control == True:																#Asking if Tiff images should be deleted (one by one) or not after beeing converted into a jpg image.
		if decision == 'n':
			erase_control = False
			decision_control = False
		elif decision =='y':
			erase_control = True
			decision_control = False
		else:
			print("\nMauvaise entrée, répondez correctement...")
			decision = input("Souhaitez vous que les images tif soient supprimées automatiquement ? [y/n] ")

	print("") # purement visuel
	timer_start = time.time()
	if data_control == True:																	#If folder entered as folder path is detected, try to detect if the folder is folder of subfolder or a folder of images
		os.chdir(main_folder_path)

		folder_list = glob.glob("*_1")
		if len(folder_list) == 0:
			folder_list_control = False
		elif len(folder_list) != 0:
			folder_list_control = True

		tiff_list = glob.glob("*.tif*")
		if len(tiff_list) == 0:
			tiff_list_control = False
		elif len(tiff_list) != 0:
			tiff_list_control = True

	if folder_list_control == True:																#If folder is a folder of subfolders
		folder_count, image_count = 0,0

		for folder in folder_list:
			folder_count += 1
			print(f"Dossier en train d'être traitée : {folder}")
			current_folder_path = main_folder_path + '/' + folder
			os.chdir(current_folder_path)
			image_list = glob.glob("*.tif")

			for image in image_list:
				image_count += 1
				temp_image = cv.imread(image)													#loading the tif image
				name = string_param.suppress_string_char(image,".tif")
				new_name = name + ".jpg"
				cv.imwrite(new_name, temp_image)												#saving the tif image as jpg

				if erase_control == True:														#remove tiff image if erase control is true
					os.remove(image)

		timer_end = time.time()
		global_time = timer_end - timer_start
		print(f"\nLe programme a converti {image_count} images en images jpg dans {folder_count} dossiers, ce qui a pris {str(global_time)} secondes.")


	if tiff_list_control == True:
		image_count = 0
		image_list = glob.glob("*.tif")
		
		for image in image_list:
			image_count += 1
			temp_image = cv.imread(image)
			name = string_param.suppress_string_char(image,".tif")
			new_name = name + ".jpg"
			cv.imwrite(new_name, temp_image)
			if image_count % 4 ==0:
				print(f"{image_count} images ont été converties.")
			if erase_control == True:
				os.remove(image)

		timer_end = time.time()
		global_time = timer_end - timer_start
		print(f"\nLe programme a converti {image_count} images en images jpg, ce qui a pris {str(global_time)} secondes.")

	if tiff_list_control == False and folder_list_control == False:
		print("\nVous avez choisi un dossier qui ne contenait ni dossier à traiter, ni d'images au format Tiff...")




elif len(sys.argv) < 2:
	print('\nMissing at least one argument from system command, expected 2, such as : main_tiff_to_jpg.py "--C:\\your\\data\\folder\\path"  ')
	print("End of program. ")
elif len(sys.argv) > 2:
	print('\nToo much argument from system command, expected 2, such as : main_tiff_to_jpg.py "--C:\\your\\data\\folder\\path"  ')
	print("End of program. ")