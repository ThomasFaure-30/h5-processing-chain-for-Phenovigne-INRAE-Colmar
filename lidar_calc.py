import numpy as np
import utils
import math
import matplotlib.pyplot as plt

from scipy.optimize import fmin
from h5_info.logger import Logger


class LidarCalc:

    @staticmethod
    def get_lidar_xy(x_raw_ref: np.ndarray, y_raw_ref: np.ndarray, x_raw: np.ndarray, y_raw: np.ndarray):
        """Gets lidar X and Y coordinates after rotation to align x-axis on the path of acquisition of phenomobile"""
        # The function below compute X-distance between first and last position after rotation alpha
        rot_func = lambda alpha: utils.cos_d(alpha) * x_raw_ref[0] - utils.sin_d(alpha) * y_raw_ref[0] + \
                                 utils.cos_d(alpha) * x_raw_ref[-1] - utils.sin_d(alpha) * y_raw_ref[-1]

        # The minimum of rot_func is the rotation resulting in an alignment of computed X-axis with path, but in the
        # opposite direction of the direction of acquisition
        #  A -180 rotation orients computed X-axis with the direction of acquisition
        r_opt = fmin(func=rot_func, x0=[0], disp=False) - 180

        rot_matrix = np.array([[utils.cos_d(r_opt), -utils.sin_d(r_opt)], [utils.sin_d(r_opt), utils.cos_d(r_opt)]])

        m_in = [x_raw, y_raw]
        return rot_matrix.dot(m_in)

    @staticmethod
    def compute_lidar_positions(lidar_ref, lidar, geo, lidar3=False, isLidar3Reversed=False):
        # INTERPOLATE GEO LOCALISATION TO LIDAR TIME
        Logger.debug("Interpolating geo localisation to lidar time")
        lidar['longitude'] = np.interp(lidar['date'], geo['date'], geo['longitude'])
        lidar['latitude'] = np.interp(lidar['date'], geo['date'], geo['latitude'])
        lidar['tray_height'] = np.interp(lidar['date'], geo['date'], geo['tray_height'])
        lidar['heading'] = np.interp(lidar['date'], geo['date'], geo['heading'])
        lidar['course'] = np.interp(lidar['date'], geo['date'], geo['course'])
        lidar['roll'] = np.interp(lidar['date'], geo['date'], geo['roll'])
        lidar['pitch'] = np.interp(lidar['date'], geo['date'], geo['pitch'])
        lidar['sog'] = np.interp(lidar['date'], geo['date'], geo['sog'])

        # CONVERSION FROM WSG84 TO LAMBERT-93 REFERENTIAL
        Logger.debug("Converting geo coordinates from WSG84 to lambert-93")
        (x0, y0) = utils.wsg84_to_lambert93(lidar_ref['longitude'][0], lidar_ref['latitude'][0])
        (x, y) = utils.wsg84_to_lambert93(lidar['longitude'], lidar['latitude'])

        lidar['x_raw'] = x0 - x
        lidar['y_raw'] = y0 - y

        # ROTATION TO ALIGN X-AXIS ON THE PHENOMOBILE ACQUISITION PATH
        Logger.debug("X-axis rotation alignment to path")
        m_out = LidarCalc.get_lidar_xy(lidar_ref['x_raw'], lidar_ref['y_raw'], lidar['x_raw'], lidar['y_raw'])
        lidar['x'] = m_out[0]
        lidar['y'] = m_out[1]

        t_0 = lidar['tray_height'][0]
        if t_0 < 0:
            Logger.warning('Height of the Tray is not available and therefore set to 0. '
                           'Vertical tray oscillations will not be corrected.')

        lidar['z'] = lidar['tray_height'] - t_0

        # COMPUTE RELATIVE POSITIONS TO FIRST POINT OF ACQUISITION
        Logger.debug("Computing relative position to first acquisition point")

        pt_x = lidar['distance'] * np.sin(lidar['pitch'] * math.pi / 180) + lidar['x']
        pt_y = lidar['distance'] * np.sin(lidar['angle'] + lidar['roll'] * math.pi / 180)
        if not lidar3 or not isLidar3Reversed:
            pt_y = -pt_y
        pt_y += lidar['y']
        pt_z = -lidar['distance'] * np.cos(lidar['angle'] + lidar['roll'] * math.pi / 180) + lidar['z']

        return {
            'pt_x': pt_x,
            'pt_y': pt_y,
            'pt_z': pt_z,
            'reflectivity': lidar['reflectivity']
        }

    @staticmethod
    def apply_transformation_matrix(mat: np.ndarray, x: np.ndarray, y: np.ndarray, z: np.ndarray):

        # Yaw=180 rotation induces a X inversion. Rotation must be done around the center point in X
        # Y and Z offset are also induced and must be corrected after the transformation
        x_min = np.min(x)
        x_max = np.max(x)
        x_mid = (x_max - x_min) / 2.0
        offset = np.array([x_mid, 0, 0]).dot(mat[0:3, 0:3].conj().transpose())

        # Take the 3 first columns of the matrix and add a 0, 0, 0, 1 column
        mat_rot = np.column_stack([mat[:, 0:3], [0, 0, 0, 1]])

        temp_rotated = np.column_stack([
            x - x_mid,
            y,
            z,
            np.ones((len(x)))
        ]).dot(mat_rot.conj().transpose())

        # Add the last column of the matrix to a 0 and 1 symetric matrix
        mat_trans = np.array([
            [1, 0, 0, mat[0, 3]],
            [0, 1, 0, mat[1, 3]],
            [0, 0, 1, mat[2, 3]],
            [0, 0, 0, mat[3, 3]]])

        temp_merged = temp_rotated.dot(mat_trans.conj().transpose())

        return temp_merged[:, 0] + abs(offset[0]), temp_merged[:, 1] + offset[1], temp_merged[:, 2] + offset[2]
