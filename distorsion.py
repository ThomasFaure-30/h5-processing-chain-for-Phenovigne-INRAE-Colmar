
import numpy as np
import cv2 as cv
import glob
import time
import os
import tifffile as tiff
from faure_utils import string_param

class distorsion:
    @staticmethod
    def get_Cam_Matrix(file):
        # termination criteria
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)


        # ======================================================================= #
        # ======================================================================= #

        x=8     # Numbers of corners of the chessboard squares following the x axis
        y=6     # Numbers of corners of the chessboard squares following the y axis

        # ======================================================================= #
        # ======================================================================= #


        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((x*y,3), np.float32)                                            # nombre de corners à détecter exemple : x,y corners
        objp[:,:2] = np.mgrid[0:x,0:y].T.reshape(-1,2)                                  # changer np.mgrid[0:9,0:6] par np.mgrid[0:x,0:y]

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        img = file

        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

        # Find the chess board corners
        ret, corners = cv.findChessboardCorners(gray, (x,y), None)                      # remplacer (gray, (9,6), None) par (gray, (x,y), None)
        # print("Debug only, ret value : "+str(ret))                 

        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)

            corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners)

            # Draw and display the corners
            # cv.drawChessboardCorners(img, (x,y), corners2, ret)                        # remplacer (img, (x,y), corners2, ret)  par (img, (x,y), corners2, ret) 
            # cv.imshow('img', img)
            # cv.waitKey(0)


            ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            
            mean_error = 0
            for i in range(len(objpoints)):
                imgpoints2, _ = cv.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
                error = cv.norm(imgpoints[i], imgpoints2, cv.NORM_L2)/len(imgpoints2)
                mean_error += error
            print( "Total error of pixel deviance (closest to 0 is better) : {}".format(mean_error/len(objpoints)) + "\n")
            
            return ret, mtx, dist, rvecs, tvecs

    def get_undistort_image(file, file_name, mtx, dist, output_path):
        img = file
        dim = img.shape
        dim = (dim[1],dim[0])
        h, w = img.shape[:2]
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))

        # undistort
        dst = cv.undistort(img, mtx, dist, None, newcameramtx)

        # location to save the new image
        os.chdir(output_path)

        # crop the image
        x, y, w, h = roi
        dst = dst[y:y+h, x:x+w]

        # Back to original size
        dst = cv.resize(dst, dim, interpolation = cv.INTER_AREA)

        # naming and saving the image
        corrected_name = string_param.suppress_string_char(file_name,'.tif')
        new_name = corrected_name + "_U.tif"
        return new_name,dst