"""
Class TiffImageHandler

This class handles Tiff image data and metadata

Based on these Exif specifications: http://www.cipa.jp/std/documents/e/DC-008-2012_E.pdf

Author: Eric David (Ephesia)
Initial Date: April 2020
"""
import numpy as np
from PIL.ExifTags import GPSTAGS as GPS_TAGS
from PIL.ExifTags import TAGS as EXIF_TAGS
from PIL.TiffTags import TAGS as TIFF_TAGS
from fractions import Fraction
import xml.etree.ElementTree as ElTree


class TiffImageHandler:
    """This class handles Tiff image data and metadata. Typical use is:

       data = <image data in bytes>
       img_hdl = TiffImageHandler(data)
       metadata = img_hdl.get_metadata()
       pixels = img_hdl.get_pixels()

       # Read metadata (see list of tags at the end of this file)
       width = metadata[TiffImageHandler.TiffTag_ImageWidth]
       exposure_time = metadata[TiffImageHandler.ExifTag_ExposureTime]

       # Do something with pixels
       ...
       pixels2 = ...

       img_hdl.set_pixels(pixels2)
       img_hdl.save(path)
    """

    def __init__(self, data):

        self._metadata = {}  # Contains readable Tiff and Exif metadata only
        self._pixel_bytes = None  # Contains pixel bytes only
        self._pixel_bytes_offset = 0
        self._data = data  # Contains the original complete binary data

        try:
            byte_order = TiffImageHandler._get_byte_order(data)
            tiff_ifd_offset = TiffImageHandler._get_offset_0th_ifd(data, byte_order)
            exif_ifd_offset = 0
            gps_ifd_offset = 0

            # READ TIFF TAGS
            nb_tiff_fields = int.from_bytes(data[tiff_ifd_offset:tiff_ifd_offset + 2], byte_order)
            offset = tiff_ifd_offset + 2
            for field in range(0, nb_tiff_fields):
                tag_id = int.from_bytes(data[offset + 0:offset + 2], byte_order)
                if tag_id not in TIFF_TAGS:
                    raise TiffDataParseError("TiffTag with id '" + str(tag_id) + "' is invalid")
                tag = TIFF_TAGS[tag_id]
                if tag == 'ExifIFD':
                    exif_ifd_offset = int.from_bytes(data[offset + 8:offset + 12], byte_order)
                elif tag == 'GPSInfoIFD':
                    gps_ifd_offset = int.from_bytes(data[offset + 8:offset + 12], byte_order)
                else:
                    (tag_type, size) = TiffImageHandler._get_type_size(
                        int.from_bytes(data[offset + 2:offset + 4], byte_order))
                    count = int.from_bytes(data[offset + 4:offset + 8], byte_order)
                    value = int.from_bytes(data[offset + 8:offset + 12], byte_order)
                    if count * size <= 4:
                        res = value
                        self._metadata["Tiff." + tag] = res
                    else:
                        if tag == 'XMP':
                            xmp_dict = TiffImageHandler._get_xmp_values(data[value:value + count * size])
                            for xmp_key in xmp_dict:
                                self._metadata[xmp_key] = xmp_dict[xmp_key]
                        else:
                            res = TiffImageHandler._get_value((tag_type, size), count, data[value:value + count * size],
                                                              byte_order)
                            self._metadata["Tiff." + tag] = res
                offset += 12

            # READ EXIF TAGS
            nb_exif_fields = int.from_bytes(data[exif_ifd_offset:exif_ifd_offset + 2], byte_order)
            offset = exif_ifd_offset + 2
            for field in range(0, nb_exif_fields):
                tag_id = int.from_bytes(data[offset + 0:offset + 2], byte_order)
                if tag_id not in EXIF_TAGS:
                    raise TiffDataParseError("ExifTag with id '" + str(tag_id) + "' is invalid")
                tag = EXIF_TAGS[tag_id]
                (tag_type, size) = TiffImageHandler._get_type_size(
                    int.from_bytes(data[offset + 2:offset + 4], byte_order))
                count = int.from_bytes(data[offset + 4:offset + 8], byte_order)
                value = int.from_bytes(data[offset + 8:offset + 12], byte_order)
                if count * size <= 4:
                    res = value
                else:
                    res = TiffImageHandler._get_value((tag_type, size), count, data[value:value + count * size],
                                                      byte_order)
                self._metadata["Exif." + tag] = res
                offset += 12

            # READ GPS TAGS
            nb_gps_fields = int.from_bytes(data[gps_ifd_offset:gps_ifd_offset + 2], byte_order)
            offset = gps_ifd_offset + 2
            for field in range(0, nb_gps_fields):
                tag_id = int.from_bytes(data[offset + 0:offset + 2], byte_order)
                if tag_id not in GPS_TAGS:
                    raise TiffDataParseError("GPSTag with id '" + str(tag_id) + "' is invalid")
                tag = GPS_TAGS[tag_id]
                (tag_type, size) = TiffImageHandler._get_type_size(
                    int.from_bytes(data[offset + 2:offset + 4], byte_order))
                count = int.from_bytes(data[offset + 4:offset + 8], byte_order)
                value = int.from_bytes(data[offset + 8:offset + 12], byte_order)
                if count * size <= 4:
                    res = value
                else:
                    res = TiffImageHandler._get_value((tag_type, size), count, data[value:value + count * size],
                                                      byte_order)
                self._metadata["GPSInfo." + tag] = res
                offset += 12

            # GET PIXELS DATA
            self._pixel_bytes_offset = self._metadata['Tiff.StripOffsets'][0]
            self._pixel_bytes = data[self._pixel_bytes_offset:]

        except TiffDataParseError as error:
            raise error
        except Exception as error:
            message = type(error).__name__ + ": " + str(error)
            raise TiffDataParseError(message)

    def get_metadata(self):
        """Gets the TIFF/EXIF metadata of the image as a dict.
        Keys are available as constants in the TiffImageHandler class"""
        return self._metadata

    def get_pixels(self):
        """Gets the list of pixels of the image as a 16-bit Numpy Array of size imageWidth * imageHeight"""
        return np.frombuffer(self._pixel_bytes, dtype=np.uint16)

    def get_pixels_bytes(self):
        """Gets the list of pixels of the image as a 16-bit Numpy Array of size imageWidth * imageHeight"""
        return self._pixel_bytes

    def set_pixels(self, pixels: np.ndarray):
        self._pixel_bytes = pixels.flatten().tobytes()

    def save(self, path):
        data_to_save = self._data[:self._pixel_bytes_offset] + self._pixel_bytes
        with open(path, 'wb') as file:
            file.write(data_to_save)

    @staticmethod
    def _get_byte_order(data):

        byte_order = data[0:2].decode("utf-8")

        if byte_order != 'II' and byte_order != 'MM':
            raise TiffDataParseError("Byte order '" + byte_order + "' invalid (must be II or MM)")

        return 'little' if data[0:2].decode("utf-8") == 'II' else 'big'

    @staticmethod
    def _get_offset_0th_ifd(data, byte_order):
        return int.from_bytes(data[4:8], byte_order)

    @staticmethod
    def _get_type_size(tag_type) -> tuple:
        """Return the size in bytes of the given type"""
        if tag_type == 1:
            return 'BYTE', 1
        elif tag_type == 2:
            return 'ASCII', 1
        elif tag_type == 3:
            return 'SHORT', 2
        elif tag_type == 4:
            return 'LONG', 4
        elif tag_type == 5:
            return 'RATIONAL', 8
        elif tag_type == 7:
            return 'UNDEFINED', 1
        elif tag_type == 9:
            return 'SLONG', 4
        elif tag_type == 10:
            return 'SRATIONAL', 8
        else:
            return 'UNDEFINED', 1

    @staticmethod
    def _get_value(type_size_tuple, count, bytes, byte_order):
        (tag_type, size) = type_size_tuple
        if tag_type == 'SHORT' or tag_type == 'LONG':
            res = []
            for i in range(0, count):
                res.append(int.from_bytes(bytes[i * size:(i + 1) * size], byte_order))
            return res
        elif tag_type == 'ASCII':
            return bytes.decode('utf-8').replace('\x00', '')
        elif tag_type == 'RATIONAL':
            res = []
            for i in range(0, count):
                offset = i * size
                num = int.from_bytes(bytes[offset:offset + 4], byte_order)
                denum = int.from_bytes(bytes[offset + 4:offset + 8], byte_order)
                res.append(Fraction(num, denum))
            return res
        else:
            return bytes

    @staticmethod
    def _get_xmp_values(bytes):

        root = ElTree.fromstring(bytes.decode('utf-8'))

        namespaces = {
            "http://pix4d.com/camera/1.0/": 'Camera',
            "http://pixinov.com/xmp/pxn/1.0/": 'PXN'
        }

        res = {}

        for child0 in root:
            for child1 in child0:
                for key in child1.attrib:
                    try:
                        arr = key[1:].split('}')
                        ns = arr[0]
                        tag = arr[1]
                        value = child1.attrib[key]
                        res['XMP.' + namespaces[ns] + '.' + tag] = value
                    except KeyError:
                        continue

        return res

    # TIFF TAGS CONSTANTS
    TiffTag_ImageWidth = 'Tiff.ImageWidth'
    TiffTag_ImageLength = 'Tiff.ImageLength'
    TiffTag_BitsPerSample = 'Tiff.BitsPerSample'
    TiffTag_Compression = 'Tiff.Compression'
    TiffTag_PhotometricInterpretation = 'Tiff.PhotometricInterpretation'
    TiffTag_DocumentName = 'Tiff.DocumentName'
    TiffTag_ImageDescription = 'Tiff.ImageDescription'
    TiffTag_Make = 'Tiff.Make'
    TiffTag_Model = 'Tiff.Model'
    TiffTag_StripOffsets = 'Tiff.StripOffsets'
    TiffTag_Orientation = 'Tiff.Orientation'
    TiffTag_SamplesPerPixel = 'Tiff.SamplesPerPixel'
    TiffTag_RowsPerStrip = 'Tiff.RowsPerStrip'
    TiffTag_StripByteCounts = 'Tiff.StripByteCounts'
    TiffTag_PlanarConfiguration = 'Tiff.PlanarConfiguration'
    TiffTag_Software = 'Tiff.Software'
    TiffTag_DateTime = 'Tiff.DateTime'
    TiffTag_Artist = 'Tiff.Artist'
    TiffTag_HostComputer = 'Tiff.HostComputer'

    # XMP TAGS CONSTANTS
    XMPTag_Camera_BandName = 'XMP.Camera.BandName'
    XMPTag_Camera_CentralWavelength = 'XMP.Camera.CentralWavelength'
    XMPTag_Camera_RigCameraIndex = 'XMP.Camera.RigCameraIndex'
    XMPTag_Camera_VignettingCenter = 'XMP.Camera.VignettingCenter'
    XMPTag_Camera_VignettingPolynomial = 'XMP.Camera.VignettingPolynomial'
    XMPTag_PXN_AutoGain = 'XMP.PXN.AutoGain'
    XMPTag_PXN_Gain = 'XMP.PXN.Gain'
    XMPTag_Camera_SensorTemperature = 'XMP.Camera.SensorTemperature'

    # EXIF TAGS CONSTANTS
    ExifTag_ExposureTime = 'Exif.ExposureTime'
    ExifTag_FNumber = 'Exif.FNumber'
    ExifTag_ExifVersion = 'Exif.ExifVersion'
    ExifTag_FocalLength = 'Exif.FocalLength'
    ExifTag_SubsecTime = 'Exif.SubsecTime'
    ExifTag_FocalPlaneXResolution = 'Exif.FocalPlaneXResolution'
    ExifTag_FocalPlaneYResolution = 'Exif.FocalPlaneYResolution'
    ExifTag_FocalPlaneResolutionUnit = 'Exif.FocalPlaneResolutionUnit'
    ExifTag_ExposureMode = 'Exif.ExposureMode'

    # GPD TAGS CONSTANTS
    GPSInfoTag_GPSVersionID = 'GPSInfo.GPSVersionID'
    GPSInfoTag_GPSLatitudeRef = 'GPSInfo.GPSLatitudeRef'
    GPSInfoTag_GPSLatitude = 'GPSInfo.GPSLatitude'
    GPSInfoTag_GPSLongitudeRef = 'GPSInfo.GPSLongitudeRef'
    GPSInfoTag_GPSLongitude = 'GPSInfo.GPSLongitude'
    GPSInfoTag_GPSAltitudeRef = 'GPSInfo.GPSAltitudeRef'
    GPSInfoTag_GPSAltitude = 'GPSInfo.GPSAltitude'
    GPSInfoTag_GPSTimeStamp = 'GPSInfo.GPSTimeStamp'
    GPSInfoTag_GPSStatus = 'GPSInfo.GPSStatus'
    GPSInfoTag_GPSMeasureMode = 'GPSInfo.GPSMeasureMode'
    GPSInfoTag_GPSDOP = 'GPSInfo.GPSDOP'
    GPSInfoTag_GPSSpeedRef = 'GPSInfo.GPSSpeedRef'
    GPSInfoTag_GPSSpeed = 'GPSInfo.GPSSpeed'
    GPSInfoTag_GPSTrackRef = 'GPSInfo.GPSTrackRef'
    GPSInfoTag_GPSTrack = 'GPSInfo.GPSTrack'
    GPSInfoTag_GPSDateStamp = 'GPSInfo.GPSDateStamp'


class TiffDataParseError(Exception):
    """Exception raised for errors during a Tiff data parsing."""

    def __init__(self, message=None):
        self._message = message

    def __str__(self):
        if self._message is None:
            return "Tiff image data is corrupted or invalid"
        else:
            return "Tiff image data error: (" + self._message + ")"
