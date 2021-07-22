import os
import time
import glob
import sys
from colorama import Fore, init, deinit, Style, Back

from faure_utils import bye, string_param

init()																					#Initialising for colorama package
timer_start = time.time()
control = False

if len(sys.argv) == 2:																	#Checking here the fact that two system arguments are inputed while laucnhing the program. 
	output_folder = sys.argv[1]
	output_folder = string_param.suppress_string_char(output_folder,"--")

	print("")
	if os.path.isdir(output_folder) == True: 											#Checking existence of the folder path you inputed in command window.
		print("Output folder of h5 files reached.\n")
		output_control = True
	else:
		output_control = False
		print("Erroc occured while tring to reach data folder, probably a wrong adress...")

	if output_control == True:
		with open('path.txt', 'w') as f: 												#Making a copy of the output folder path for the following programs (LiDAR, rgb extract et correct et concatenate).
		    f.write(output_folder)
		    f.close()

		os.chdir(output_folder)
		if os.path.isdir("LiDAR") == True: 												#Vérification de l'existence du dossier "LiDAR" et de son contenu
			temp_path = output_folder + "/LiDAR"
			os.chdir(temp_path)
			file_presence1= glob.glob("*")
			if len(file_presence1) != 0:												#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'LiDAR' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("LiDAR")
			print("'LiDAR' folder created.")


		if os.path.isdir("Tiff_brute") == True:											#Vérification de l'existence du dossier "Tiff_brute" et de son contenu
			temp_path = output_folder + "/Tiff_brute"
			os.chdir(temp_path)
			file_presence2= glob.glob("*")
			if len(file_presence2) != 0:												#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'Tiff_brute' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("Tiff_brute")
			print("'Tiff_brute' folder created.")


		if os.path.isdir("Tiff_corrige") == True:										#Vérification de l'existence du dossier "Tiff_corrige" et de son contenu
			temp_path = output_folder + "/Tiff_corrige"
			os.chdir(temp_path)
			file_presence3= glob.glob("*")
			if len(file_presence3) != 0:												#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'Tiff_corrige' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("Tiff_corrige")
			print("'Tiff_corrige' folder created.")

		if os.path.isdir("Tiff_panorama") == True:										#Vérification de l'existence du dossier "Tiff_panorama" et de son contenu
			temp_path = output_folder + "/Tiff_panorama"
			os.chdir(temp_path)
			file_presence4= glob.glob("*")
			if len(file_presence4) != 0:												#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'Tiff_panorama' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("Tiff_panorama")
			print("'Tiff_panorama' folder created.")

		if os.path.isdir("LiDAR") == True and os.path.isdir("Tiff_brute") == True and os.path.isdir("Tiff_corrige") == True and os.path.isdir("Tiff_panorama") == True:
			print("\n-Every folder expected are present in your main folder, no folder created, mandatory folders for the processing is ok...")

		timer_end = time.time()
		global_time = timer_end-timer_start
		print("\nProgram successfully created or checked the mandatory data architecture and wrote the path.txt file in " + str(global_time) + " seconds")

	elif output_control == False:
		print("End of program.\n")

elif len(sys.argv) < 2:																#Error handling for less system arguments than expected
	print(Fore.RED + Back.WHITE + '\nMissing at least one argument from system command, expected 2, such as : main_architecture_h5.py "--C:\\your\\h5\\output\\folder\\path" ')
	print("End of program. ")
elif len(sys.argv) > 2:																#Error handling for more system arguments than expected
	print(Fore.RED + Back.WHITE + '\nToo many arguments from system command, expected 2, such as : main_architecture_h5.py "--C:\\your\\h5\\output\\folder\\path" ')
	print("End of program. ")	


bye.bye() 
