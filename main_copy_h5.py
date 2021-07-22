import os
import time
import sys
import glob
import shutil
from colorama import Fore, init, deinit, Style, Back

from faure_utils import bye, string_param

init()																								#Initialising for colorama package
timer_start = time.time()
file_counting = 0
control = False

if len(sys.argv) == 3:																				#Checking here the fact that three system arguments are inputed while laucnhing the program.
	source_file_folder = sys.argv[1]
	output_folder = sys.argv[2]
	source_file_folder = string_param.suppress_string_char(source_file_folder,"--")
	output_folder = string_param.suppress_string_char(output_folder,"--")

	print("")
	if os.path.isdir(source_file_folder) == True: 													#Checking existence of the source folder path you inputed in command window.
		print("Data folder reached.")
		data_control = True
	else:
		data_control = False
		print("Erroc occured while tring to reach data folder, probably a wrong adress...")

	if os.path.isdir(output_folder) == True: 														#Checking existence of the output folder path you inputed in command window.
		print("Output folder for h5 files reached.\n")
		output_control = True
	else:
		output_control = False
		print("Erroc occured while tring to reach data folder, probably a wrong adress...")

	if data_control == True and output_control == True:
		with open('path.txt', 'w') as f: 															#Making a copy of the output folder path for the following programs (LiDAR, rgb extract et correct et concatenate).
		    f.write(output_folder)
		    f.close()

		os.chdir(output_folder)
		if os.path.isdir("LiDAR") == True: 															#Vérification de l'existence du dossier "LiDAR" et de son contenu
			temp_path = output_folder + "/LiDAR"
			os.chdir(temp_path)
			file_presence1= glob.glob("*")
			if len(file_presence1) != 0:															#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'LiDAR' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("LiDAR")


		if os.path.isdir("Tiff_brute") == True:														#Vérification de l'existence du dossier "Tiff_brute" et de son contenu
			temp_path = output_folder + "/Tiff_brute"
			os.chdir(temp_path)
			file_presence2= glob.glob("*")
			if len(file_presence2) != 0:															#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'Tiff_brute' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("Tiff_brute")


		if os.path.isdir("Tiff_corrige") == True:													#Vérification de l'existence du dossier "Tiff_corrige" et de son contenu
			temp_path = output_folder + "/Tiff_corrige"
			os.chdir(temp_path)
			file_presence3= glob.glob("*")
			if len(file_presence3) != 0:															#Raise a warning if any file are detected inside this specific folder.
				control = True
				print(Fore.RED + Back.WHITE + "\nAttention, le dossier 'Tiff_corrige' contient des données, veuillez les supprimer et relancez le programme.")
				print(Style.RESET_ALL)
			os.chdir(output_folder)
		else:
			os.makedirs("Tiff_corrige")


		os.chdir(source_file_folder)
		h5_folder_list = glob.glob('*_1') 															# Retrieving the folder (ending with a '_1') list present in your source file folder.

		if control == False:
			for folder in h5_folder_list:
				print("Current folder is : " + folder)
				os.chdir(source_file_folder + '/' + folder)

				h5_file = glob.glob('*_1.h5') 														#H5 files detection

				for file in h5_file:
					print("File currently processed : " + file)
					shutil.copy(file, output_folder) 												#Copying the h5 file to the output folder.
					file_counting = file_counting + 1

		os.chdir(source_file_folder)
		try:																						#Retrieving the log file along.
			shutil.copy('roslogs.csv',output_folder)
			roslog = True
		except PermissionError:
		    print("Permission denied.")
		    roslog = False
		except:
			print("Erroc occured while copying the roslog file.")
			roslog = False

		timer_end = time.time()
		global_time = timer_end-timer_start
		print("\n" + str(file_counting)+ " h5 files were copied from directory " + source_file_folder + " and took " + str(global_time) + " seconds")

		# Section for raising alert with colorama
		if roslog == True: 
			print("Roslog file has been copied to output folder")
		elif roslog == False:
			print(Fore.RED + Back.WHITE + "Roslog file has not been copied.")
		if file_counting == 0 and control == False:
			print(Fore.RED + Back.WHITE + "\n//!\\\\ Be careful, there was no h5 files extracted using this program, you must have took the wrong folder... //!\\\\")
		print(Style.RESET_ALL)
		deinit()
	else:
		print(Fore.RED + Back.WHITE + "\nSomething went wrong for reaching one or the two folders, you're not allowed to pursue.")
		print(Style.RESET_ALL)
		deinit()
elif len(sys.argv) < 3:																				#Error handling for less system arguments than expected
	print(Fore.RED + Back.WHITE + '\nMissing at least one argument from system command, expected 3, such as : main_copy.py "--C:\\your\\data\\folder\\path" "--C:\\your\\output\\folder\\path" ')
	print("End of program. ")
elif len(sys.argv) > 3:																				#Error handling for more system arguments than expected
	print(Fore.RED + Back.WHITE + '\nToo many arguments from system command, expected 3, such as : main_copy.py "--C:\\your\\data\\folder\\path" "--C:\\your\\output\\folder\\path" ')
	print("End of program. ")	


bye.bye() 