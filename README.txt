Pretreatment chain for Phénovigne output - INRAE Colmar

This chain does all the work, started from copying the h5 files (from external hard drive) to correcting vigneting and distorsioneffect of the images. Further programs has been added 
The program does not take care from the amount of data that it has to process. All the programs has to be in the same folder to be correctly used.


1 ==> main_copy_h5.py :
	This program (the first to be executed) takes two input while launching it from terminal. It expects the data folder of the raw output from the Phenovigne 
	and the output folder for the h5 files. It expects something like this : main_copy_h5.py "--C:\\your\\data\\folder\\path" "--C:\\your\\output\\folder\\path"
	The program create the mandatory data architecture for your output folder, which is used in the following programs.

2 ==> main_rgb_extract.py
	This program extract the images from the h5 archives and save them as a tif image, it also apply a chosen white balance. 
	You can execute it directly from the terminal. It only takes one input, at the beginning of the execution, to choose a white balance.

3 ==> main_correct.py
	This program correct the distorsion and vigneting effect on images, it requires two sample to do so.
	You can execute it directly from the terminal, it does not take any input.

4 ==> main_lidar_extract.py
	This program extract from h5 archives the LiDAR data to create .las files. It also gives the metadata of the many acquisitions. 
	You can execute it directly from the terminal, it does not take any input.

OPTIONNAL :
* ==> main_concatenate.py :
	This program allow you to make a simple concatenation of your images in your subfolders regardless to the image amount nor folder amount.
	Ths program does not take any input, it follows what "path.txt" provides him as a path. 
	It will only deal the images present in Tiff_corrige folder and save them in Tiff_panorama folder (created by program).

* ==> main_tiff_to_jpg.py :
	This program allow you to convert yout tiff-16bit depth tiff image into a 8-bit depth jpg image.
	This program takes one input while launching it from terminal.
	It expects something like this : main_tiff_to_jpg.py "--C:\\your\\data\\folder\\path" 

* ==> main_HSV_mask.py :
	This program allows you to generate mask of your jpg images using a threshold of your image in HSV colorspace.
	This program takes one input while launching it from terminal.
	It expects something like this : main_HSV_mask.py "--C:\\your\\data\\folder\\path"
	This program will process your images in your main folder or subfolders regardless to the image amount nor folder amount.
	The output images will be saved in "Mask" folder (created by program).
	
* ==> main_leaf_area.py :
	This program allows you to calculate the % leaf area over a black background (assuming you have thresholded your image).
	This program takes one input while launching it from terminal. 
	It expects something like this : main_HSV_mask.py "--C:\\your\\data\\folder\\path"
	It will be executed regardless that your information (images) is stored directly in your folder path nor in subfolders.
	It will creat an output 'results.txt' to store your data in the folder you indicated. It also assume that you image name contains the plot ID.

# =========================== LIBRARIES =========================== #

To easy install the libraries there is a ' requirements.txt ' file in this folder.
In your terminal, go to this folder adress and then enter ' pip install -r requirements.txt ' in terminal.
It should install all the wanted libraries at once, with the correct version of them.

The used libraries are the following ones :

-	colour-demosaicing       0.1.6
-	colorama                 0.4.4
-	ExifRead                 2.3.2
-	h5-info-pkg-inra-phenome 1.1.8
-	imagecodecs              2021.6.8
-	laspy                    1.7.0
-	numpy                    1.20.2
-	opencv-contrib-python    4.5.1.48
-	opencv-python            4.5.1.48
-	panda                    0.3.1
-	pandas                   1.2.4
-	Pillow                   8.2.0
-	scipy                    1.6.2
-	tifffile                 2021.4.8
-	tqdm                     4.60.0
-	matplotlib               3.4.1
