import datetime

import laspy

import numpy as np
from math import *
import matplotlib.pyplot as plt
from h5_info.logger import Logger
from h5_info.errors import DataError
from h5_info import constants
from mpl_toolkits.mplot3d import Axes3D  # Don't remove this import


def imadjust(x, a, b, c, d, gamma=1):
    """Adjust image intensity values
       Similar to imadjust in MATLAB.
       Converts an image range from [a,b] to [c,d].
       The Equation of a line can be used for this transformation:
         y=((d-c)/(b-a))*(x-a)+c
       However, it is better to use a more generalized equation:
         y=((x-a)/(b-a))^gamma*(d-c)+c
       If gamma is equal to 1, then the line equation is used.
       When gamma is not equal to 1, then the transformation is not linear."""

    y = (((x - a) / (b - a)) ** gamma) * (d - c) + c
    return y


def csv_file_to_matrix(csv_file, dtype, separator=";"):
    """Reads a CSV file of matrix-like data of a certain type and returns a numpy array of shape nb_rows * nb_columns"""
    with open(csv_file, 'r') as file:
        line = file.readline()
        res = []
        while line:
            values = line.strip().split(separator)
            res.append(values)
            line = file.readline()
        return np.asarray(res, dtype=dtype)


def csv_file_to_numpy(csv_file, dtypes, keys=None):
    """Reads a CSV file of size N columns and M lines and returns a dict of arrays where keys are the CSV headers.
       Example:
                res = {
                    "key1":[value1, value2, ..., valueM],
                    "key2":[value1, value2, ..., valueM],
                    ...
                    "keyN":[value1, value2, ..., valueM],
                }
    """
    with open(csv_file, 'r') as file:
        items = {}
        res = {}
        headers = file.readline().strip().split(';')
        for key in headers:
            items[key] = []
        line = file.readline()
        while line:
            values = line.strip().split(';')
            for k, key in enumerate(headers):
                if k < len(values):
                    items[key].append(values[k])
            line = file.readline()

        for k, key in enumerate(headers):
            if (not keys or key in keys) and k < len(dtypes):
                res[key] = np.array(items[key], dtype=dtypes[k])
        return res


def numpy_to_ascii_file(path, data, keys, separator=";", skip_headers=False):
    try:
        with open(path, "w") as file:
            if not skip_headers:
                headers = separator.join(keys.values())
                file.write(headers + constants.END_LINE_W)
            i = 0
            while True:
                values = []
                for key in keys:
                    values.append(str(data[key][i]))
                line = separator.join(values)
                file.write(line + constants.END_LINE_W)
                i += 1
    except IndexError:
        pass


def wsg84_to_lambert93(longitude_wsg84, latitude_wsg84) -> tuple:
    if isinstance(longitude_wsg84, np.ndarray) and isinstance(latitude_wsg84, np.ndarray):
        return __wsg84_to_lambert93_vector(longitude_wsg84, latitude_wsg84)
    else:
        return __wsg84_to_lambert93_scalar(longitude_wsg84, latitude_wsg84)


def __wsg84_to_lambert93_vector(longitude_wsg84: np.ndarray, latitude_wsg84: np.ndarray) -> tuple:
    """Converts the given GPS coordinates in WSG84 referential to Lambert-93 referential.
        :param longitude_wsg84 longitude ndarray in the WSG84 referential
        :param latitude_wsg84 latitude ndarray in the WSG84 referential
        :return returns a tuple of converted longitude and latitude in the Lambert-93 referential
        Valid in France only
        See https://georezo.net/forum/viewtopic.php?id=94465 for reference"""

    # Check parameters validity
    if len(longitude_wsg84) == 0:
        raise DataError("Longitude array must not be empty")
    if len(latitude_wsg84) == 0:
        raise DataError("Latitude array must not be empty")
    if len(longitude_wsg84) != len(latitude_wsg84):
        raise DataError("Longitude and latitude arrays must have the same size")

    # Check Metropolitan Continental France territory
    if not (-4.7956 < np.mean(longitude_wsg84) < 8.2306 and 42.333 < np.mean(latitude_wsg84) < 51.072):
        Logger.warning("Set of coordinates not in the Metropolitan Continental France territory")

    # Define Constants
    cst_c = 11754255.426096  # Constante de projection
    cst_e = 0.0818191910428158  # Premiere excentricite de l'ellipsoide
    cst_n = 0.725607765053267  # Exposant de la projection
    cst_xs = 700000  # Coordonnees en projection du pole
    cst_ys = 12655612.049876  # Coordonnees en projection du pole

    lat_rad = latitude_wsg84 * pi / 180
    lat_iso = np.arctanh(np.sin(lat_rad)) - cst_e * np.arctanh(cst_e * np.sin(lat_rad))

    long_l93 = cst_c * np.exp(-cst_n * lat_iso) * np.sin(cst_n * (longitude_wsg84 - 3) / 180 * pi) + cst_xs
    lat_l93 = cst_ys - cst_c * np.exp(-cst_n * lat_iso) * np.cos(cst_n * (longitude_wsg84 - 3) / 180 * pi)

    return long_l93, lat_l93


def __wsg84_to_lambert93_scalar(longitude_wsg84: float, latitude_wsg84: float) -> tuple:
    """Converts the given GPS point coordinates in WSG84 referential to Lambert-93 referential
        :param longitude_wsg84 longitude in the WSG84 referential
        :param latitude_wsg84 latitude in the WSG84 referential
        :return returns a tuple of converted longitude and latitude in the Lambert-93 referential
        Valid in France only
        See https://georezo.net/forum/viewtopic.php?id=94465 for reference"""

    # Check Metropolitan Continental France territory
    if not (-4.7956 < longitude_wsg84 < 8.2306 and 42.333 < latitude_wsg84 < 51.072):
        Logger.warning("Set of coordinates not in the Metropolitan Continental France territory")

    # Define Constants
    cst_c = 11754255.426096  # Constante de projection
    cst_e = 0.0818191910428158  # Premiere excentricite de l'ellipsoide
    cst_n = 0.725607765053267  # Exposant de la projection
    cst_xs = 700000  # Coordonnees en projection du pole
    cst_ys = 12655612.049876  # Coordonnees en projection du pole

    lat_rad = latitude_wsg84 * pi / 180
    lat_iso = atanh(sin(lat_rad)) - cst_e * atanh(cst_e * sin(lat_rad))

    long_l93 = cst_c * exp(-cst_n * lat_iso) * sin(cst_n * (longitude_wsg84 - 3) / 180 * pi) + cst_xs
    lat_l93 = cst_ys - cst_c * exp(-cst_n * lat_iso) * cos(cst_n * (longitude_wsg84 - 3) / 180 * pi)

    return long_l93, lat_l93


def cos_d(alpha_deg):
    """Computes cosine value for an angle in degrees"""
    return cos(pi * alpha_deg / 180)


def sin_d(alpha_deg):
    """Computes sine value for an angle in degrees"""
    return sin(pi * alpha_deg / 180)


def plot_point_cloud(x, y, z, reflectivity):
    """Return the plot handle of the given point cloud"""
    Logger.debug("Plotting scatter point cloud")

    r_max = np.max(reflectivity)
    r_min = np.min(reflectivity)
    r_diff = r_max - r_min

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    cb = ax.scatter(x, y, z, c=reflectivity/r_diff, s=2, cmap='autumn_r')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.colorbar(cb)
    plt.title("Point Cloud Reflectivity")

    return plt


def compute_transformation_matrix(dx, dy, dz, yaw, pitch, roll):
    """Generates rotation and translation matrix from space translation and rotation values"""
    a = yaw
    b = pitch
    c = roll

    r_z = np.array([[cos(a), -sin(a), 0],
                    [sin(a), cos(a), 0],
                    [0, 0, 1]])
    r_y = np.array([[cos(b), 0, sin(b)],
                    [0, 1, 0],
                    [-sin(b), 0, cos(b)]])
    r_x = np.array([[1, 0, 0],
                    [0, cos(c), -sin(c)],
                    [0, sin(c), cos(c)]])

    rot_mat = r_z.dot(r_y).dot(r_x)
    rot_mat = np.row_stack([rot_mat, [0, 0, 0]])

    trans_mat = np.column_stack([rot_mat, [dx, dy, dz, 1]])

    return trans_mat


def create_las_file(path, x, y, z, reflectivity=None):
    """Create point cloud file in LAS format"""
    if reflectivity is None:
        reflectivity = []

    header = laspy.header.Header()
    with laspy.file.File(path, mode="w", header=header) as outfile:

        outfile.header.system_id = "Phenomobile V2 - LMS 400        "  # Must be 32 chars
        outfile.header.software_id = "4P Pheno Extraction LidarProcess"  # Must be 32 chars
        outfile.header.date = datetime.datetime.now()
        outfile.header.offset = [0, 0, 0]
        outfile.header.scale = [0.0001, 0.0001, 0.0001]

        if len(reflectivity) > 0:
            outfile.define_new_dimension(
                name="reflectivity",
                data_type=7,
                description="Signal Reflectivity"
            )
            outfile.reflectivity = reflectivity

        outfile.X = x * 1e4  # Must be long values (smallest possible scale 1e-4)
        outfile.Y = y * 1e4
        outfile.Z = z * 1e4
