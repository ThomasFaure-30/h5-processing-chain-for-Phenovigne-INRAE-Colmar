import re
import glob
import sys
import os
import cv2 as cv
import PySimpleGUI as sg



class theme:

	def program_begin_theme():
		sg.theme_background_color('grey70')
		sg.theme_text_element_background_color ('grey70')
		sg.theme_text_color('Royalblue4')
		#sg.theme_border_width('')
		sg.theme_button_color('black')
		sg.theme_element_background_color('')
		sg.theme_element_text_color('DarkGoldenrod1')
		sg.theme_input_background_color('white')
		sg.theme_input_text_color('black')
		#sg.theme_progress_bar_border_width('')
		#sg.theme_progress_bar_color('')
		#sg.theme_slider_border_width('')
		#sg.theme_slider_color('')



	def program_end_theme():
		sg.theme_background_color('grey70')
		sg.theme_text_element_background_color ('grey70')
		sg.theme_text_color('forest green')
		#sg.theme_border_width('')
		sg.theme_button_color('black')
		sg.theme_element_background_color('')
		sg.theme_element_text_color('DarkGoldenrod1')
		sg.theme_input_background_color('white')
		sg.theme_input_text_color('white')
		#sg.theme_progress_bar_border_width('')
		#sg.theme_progress_bar_color('')
		#sg.theme_slider_border_width('')
		#sg.theme_slider_color('')

	def program_alert_theme():
		sg.theme_background_color('grey80')
		sg.theme_text_element_background_color ('grey80')
		sg.theme_text_color('Royalblue4')
		#sg.theme_border_width('')
		sg.theme_button_color('dark red')
		sg.theme_element_background_color('')
		sg.theme_element_text_color('DarkGoldenrod1')
		sg.theme_input_background_color('white')
		sg.theme_input_text_color('white')
		#sg.theme_progress_bar_border_width('')
		#sg.theme_progress_bar_color('')
		#sg.theme_slider_border_width('')
		#sg.theme_slider_color('')

class image:

	def show(image,name='image'):
		string = name + ' ---- Enter to quit image displaying'
		cv.imshow(string, image)
		cv.waitKey(0)

class string_param:

	@staticmethod
	def suppress_string_char(file_name,char):
			new_name = file_name.replace(char, "")
			return new_name

	def get_plot(file_name):
		plot = file_name.replace("uplot_","")
		plot = plot.replace("_camera","")
		plot = plot.replace(".jpg","")
		plot = plot.replace(".tif","")
		plot = plot.replace("_RGB","")
		plot = plot.replace("_WB","")
		plot = plot.replace("_U","")
		plot = plot.replace("_V","")
		plot = plot.replace("_BG","")
		plot = plot.replace("_TH","")
		plot = plot.replace("_1","")
		plot = plot.replace("_2","")
		plot = plot.replace("_3","")
		plot = plot.replace("_4","")
		plot = plot.replace("_5","")
		plot = plot.replace("_6","")
		plot = plot.replace("_7","")
		plot = plot.replace("_8","")
		length = len(plot) - 3
		plot = plot[0:length]
		plot = int(plot)
		return plot

	def get_population(plot):
		plot = float(plot)

		if plot >= 32201 and plot <= 32640:
			population = "Pop_50025"
		elif plot >= 32701 and plot <= 32754:
			population = "Bordure_Pop_50025"
		elif plot >= 27661 and plot <= 28123:
			population = "Pop_Riesling_Gewurtz"
		else:
			population = "Na"


		return population

class erase:
	
	@staticmethod
	def erase_files(main_folder_path):
		print("Starting cleaning the output folder...")
		os.chdir(main_folder_path)
		file_list = glob.glob('*')
		file_count = 0
		for file in file_list:					# Supprime tous les FICHIERS détectés par le glob.glob dans le sous-dossier folder indiqué par le path
			file_path = main_folder_path + '/' + file
			os.remove(file_path)
			file_count += 1
		print("Program erased "+ str(file_count) +" files from the output folder. ")


	@staticmethod
	def erase_folder_and_files(main_folder_path):
		os.chdir(main_folder_path)
		print("")
		print("Folder currently processed : " + main_folder_path)

		folder_list = glob.glob('*_1')
		folder_count = 0
		file_count = 0

		for folder in folder_list:				# Supprime tous les DOSSIERS détectés par le glob.glob dans le dossier
			folder_path = main_folder_path + '/' + folder
			os.chdir(folder_path)
			file_list = glob.glob('*')

			for file in file_list:					# Supprime tous les FICHIERS détectés par le glob.glob dans le sous-dossier folder indiqué par le path
				file_path = folder_path + '/' + file
				os.remove(file_path)
				file_count = file_count + 1

			os.chdir(main_folder_path)
			os.rmdir(folder_path)
			folder_count = folder_count + 1

		print("Program erased "+ str(file_count) +" files inside "+ str(folder_count) +" folders, and supressed the folders. ")

class reshape:

	@staticmethod
	def resize(image_path, shape, message=True):

		image = image_path 
		source = cv.imread(image)
		dim = shape

		new_image = cv.resize(source, dim, interpolation = cv.INTER_AREA)
		if message == True:
			print("Resized dimension : ", new_image.shape)
		return new_image

class bye:

	@staticmethod
	def bye():
		byebye = input("Press Enter to exit : ")
		if byebye:
			sys.exit("Fin du programme.")

class image:

	def show(image, name='image'):
		string = name + ' ---- Enter to quit image displaying'
		cv.imshow(string, image)
		cv.waitKey(0)
