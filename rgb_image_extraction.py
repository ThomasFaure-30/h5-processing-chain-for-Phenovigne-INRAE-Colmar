"""
RGB extract module

This module extracts and processes the raw images from RGB sensor to RGB images

Author: Eric David (Ephesia)
Initial Date: October 2019

v2 : Updated for naming directory after the h5 file used 
	 Pointing at a specific directory for where to extract the files.
	 Time used for creating all the files

v3 : Goal is to transform this program into a class to use from the interface
     Other changes ...

"""
import os
import sys
from sre_parse import SubPattern

import numpy as np
import time

import tifffile as tiff

from colour_demosaicing import demosaicing_CFA_Bayer_bilinear

from h5_info import H5Info
from h5_info.logger import Logger
from h5_info.errors import DataError
from h5_info import constants
from utils import csv_file_to_numpy
from utils import imadjust
from checker import Checker, ArgumentError, ERROR_CODE

class extracting:

    @staticmethod
    def get_rgb_image(file,data_path,output,wb_path,wb_filename):
        COMMAND_LINE = "path/to/hdf5.file path/to/output/folder --WBFactorsFile path/to/wb/factors/file.csv --gamma 0.5 --debug true"

        PARAM_GAMMA = "--gamma"
        PARAM_WB_FACTORS = "--WBFactorsFile"
        PARAM_DEBUG = "--debug"

        MANDATORY_ARG_LIST = [file, output]

        OPTIONAL_ARG_LIST = {
            PARAM_GAMMA: 'Gamma contrasting factor for image rescaling (numeric value, default = 0.5)',
            PARAM_WB_FACTORS: 'Path to white balance factors file (default = 1 for each factor)',
            PARAM_DEBUG: 'Flag for displaying debug level logs (true or false)'
        }

        # DEBUG ONLY
        # sys.argv.append('D:\\tests-pheno\\test-toulouse.h5')
        # sys.argv.append('D:\\tests-pheno\\output')
        # sys.argv.append('--gamma')
        # sys.argv.append('0.5')
        # sys.argv.append('--WBFactorsFile')
        # sys.argv.append('D:\\tests-pheno\\camera_wb_factors.csv')
        # sys.argv.append('--debug')
        # sys.argv.append('false')

        timer_start = time.time()

        try:
            # CHECKING PARAMETERS
            Logger.info("Validating module input parameters...")

            optional_args = {}
            mandatory_args = [file, output]
            Checker.check_input_arguments(sys.argv,
                                        mandatory_args, optional_args,
                                        MANDATORY_ARG_LIST, OPTIONAL_ARG_LIST,
                                        COMMAND_LINE)

            h5_file = mandatory_args[0]
            Checker.check_file_exists(h5_file)

            sensor_names = ["Camera"]
            h5_info = H5Info()
            h5_info.load_data(h5_file, sensor_names)

            path_output= output   # Directory to choose for results extracted
            os.chdir(path_output)
            Newfolder="uplot_" + h5_info.plot.id + "_1"
            os.makedirs(Newfolder)

            output_folder=Newfolder
            Checker.check_folder_exists(output_folder, True)

            if Checker.is_optional_param_true(PARAM_DEBUG, optional_args, False):
                Logger.init(True)
                Logger.debug("Debug logs will be displayed")

            gamma = Checker.get_optional_numeric_param(PARAM_GAMMA, optional_args, 0.5)

            
            if wb_filename is not None:
                os.chdir(wb_path)
                print("White balance file path is: "+ wb_filename )
                wb_factors_path = wb_path + "/" + wb_filename
            else:
                wb_factors_path = None
                print("No White Balance factors found...")

            os.chdir(path_output)
            # EXTRACTING HDF5 INFORMATION
            Logger.info("Reading file '"+h5_file+"'...")
            Logger.info("Loading HDF5 meta-information and raw data...")

            plot_prefix = "uplot_" + h5_info.plot.id + "_"

            h5_info.save_metadata(output_folder + "/" + plot_prefix + "rgb_metadata.json")

            # READING CAMERA IMAGES
            Logger.info("Reading camera raw images...")
            images = []
            for sensor in h5_info.sensors:
                if sensor.type == constants.TYPE_CAMERA:
                    for image in sensor.images:
                        Logger.debug("Image found: " + image.name)
                        images.append(image)

            # LOAD WHITE BALANCE FACTORS
            os.chdir(wb_path)
            wb_factor_sensors = {}
            if wb_factors_path is not None:
                Logger.info("Reading White Balance factors '" + wb_factors_path + "' file...")
                keys = ['camera_id', 'red_green_wb_factor', 'blue_green_wb_factor']
                dtypes = [np.int, np.float, np.float]
                wb_factors = csv_file_to_numpy(wb_factors_path, dtypes, keys)
                nb_cams = np.size(wb_factors['camera_id'])

                for line_idx in range(0, nb_cams):
                    try:
                        cam_id = wb_factors['camera_id'][line_idx]
                        red_factor = wb_factors['red_green_wb_factor'][line_idx]
                        blue_factor = wb_factors['blue_green_wb_factor'][line_idx]
                        wb_factor_sensors[cam_id] = np.array([red_factor, 1.0, blue_factor])
                    except KeyError as error:
                        Logger.warning("Cannot read white balance factors due to a Key Error: {0}".format(error))
                        continue
                    except ValueError as error:
                        Logger.warning("Cannot read white balance factors due to a Value Error: {0}".format(error))
                        continue

            # DEMOSAIC, WHITE BALANCE AND EXTRACT
            os.chdir(path_output)
            for sensor in h5_info.sensors:
                wb_factor = np.array([1.0, 1.0, 1.0])
                if sensor.id in wb_factor_sensors:
                    wb_factor = wb_factor_sensors[sensor.id]
                else:
                    Logger.warning("No white balance reference factors were found for Camera ID '" + str(sensor.id) + "'. The default value 1.0 will be used instead.")

                for image in sensor.images:
                    if sensor.type == constants.TYPE_CAMERA:
                        try:
                            Logger.info("Pre-processing RGB image '" + image.name + "'...")
                            Logger.debug("Reading data image " + image.name)
                            pixels = np.frombuffer(image.image.tobytes(), dtype=np.uint16)
                            pixels = np.reshape(pixels, (image.height, image.width))

                            Logger.debug("Demosaicing image " + image.name)
                            pixels = demosaicing_CFA_Bayer_bilinear(pixels, 'RGGB')

                            Logger.debug("Adjusting image white balance and intensity " + image.name)
                            pixels = pixels.flatten()
                            for t in range(0, 3):
                                pixels[t::3] *= wb_factor[t]

                            pixels = imadjust(pixels, np.amin(pixels), np.amax(pixels), 0, 65535, gamma)
                            pixels = np.reshape(pixels, (image.height, image.width, 3))
                            if wb_factors_path is not None:
                                new_name = image.name + "_RGB_WB.tif"
                            else:
                                new_name = image.name + "_RGB.tif"

                            Logger.debug("Extracting RGB image " + new_name)
                            pixels = np.uint16(pixels)
                            # print(pixels[0,0,0])
                            date = h5_info.session.date
                            plot = h5_info.plot.id
                            machine = h5_info.vector.id
                            img_desc = {
                                'RescalingGammaFactor': gamma,
                                'RedGreenRefWBFactor': wb_factor[0],
                                'BlueGreenRefWBFactor': wb_factor[2],
                                'camera' : 'Baumer VCXG 124C',
                                'datetime': str(date),
                                'plot' : str(plot),
                                'machine' : str(machine),

                            }

                            tiff.imwrite(output_folder + "/" + plot_prefix + new_name, pixels, photometric='rgb', metadata=img_desc, software="Pheno RGB Extraction Module by INRAE")

                        except ValueError as error:
                            raise DataError(error)
        except ArgumentError as error:
            Logger.error(error)
            Logger.error("RGB Extraction failed")
            sys.exit(ERROR_CODE)
        except DataError as error:
            Logger.error(error)
            Logger.error("RGB Extraction of {0} failed".format(h5_file))
        finally:
            timer_end = time.time()
            Logger.debug("RGB pre-processing took " + str(int(timer_end - timer_start)) + " seconds")
        print("The extraction process for this h5 file took "+str(int(timer_end - timer_start)) + " seconds.\n")