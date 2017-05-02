# author: Zach Crabtree zacharyc@alleninstitute.org

import numpy as np

from aicsimage.io import omeTifReader, cziReader


class AICSImage:
    """
    A wrapper class for ndarrays.

    Example:
        # valid ndarrays are between 1 and 5 dimensions
        >>> data4d = numpy.zeros((2, 25, 1024, 1024))
        >>> data2d = numpy.zeros((99, 100))
        # any dimension ordering of T, C, Z, Y, X is valid
        >>> image_from_4d = AICSImage(data4d, dims="TZYX")
        >>> image_from_2d = AICSImage(data2d, dims="YX")
        # now both images are expanded to contain all 5 dims
        # you can access it in any dimension ordering, no matter how nonsensical
        >>> image_to_5d_from_4d = image_from_4d.get_image_data("XYCZT")
        >>> image_to_5d_from_2d = image_from_2d.get_image_data("YCZTX")
        # you can also access specific slices from each dimension you leave out
        >>> image_to_1d_from_2d = image_from_2d.get_image_data("X", Y=12)

        # finally, AICSImage objects can be generated from ometifs and czis (could be removed in later revisions)
        >>> image_from_file = AICSImage("image_data.ome.tif")
        >>> image_from_file = AICSImage("image_data.czi")

    """
    default_dims = "TCZYX"

    def __init__(self, data, **kwargs):
        """
        Constructor for AICSImage class
        :param data: String with path to ometif/czi file, or ndarray with up to 5 dimensions
        :param kwargs: If ndarray is used for data, then you can specify the dim ordering
                       with dims arg (ie dims="TZCYX")
        """
        self.dims = AICSImage.default_dims
        if isinstance(data, str):
            # input is a filepath
            self.file_path = data

            # check for compatible data types
            czi_types = (".czi", ".CZI")
            ome_types = (".ome.tif", ".ome.tiff", ".OME.TIF", ".OME.TIFF")
            if data.endswith(czi_types):
                self.reader = cziReader.CziReader(self.file_path)
            elif data.endswith(ome_types):
                self.reader = omeTifReader.OmeTifReader(self.file_path)
            else:
                raise ValueError("CellImage can only accept OME-TIFF and CZI file formats!")

            # TODO remove this transpose call once reader output is changed
            self.data = self.reader.load().transpose(0, 2, 1, 3, 4)
            self.metadata = self.reader.get_metadata()
            # internal data should always be stored as TCZYX
            self._generate_size()

        elif isinstance(data, np.ndarray):
            # input is a data array
            self.data = data
            if self.is_valid_dimension(kwargs["dims"]):
                self.dims = kwargs["dims"]

            if len(self.dims) != len(self.data.shape):
                raise ValueError("Number of dimensions must match dimensions of array provided!")

            self._generate_size()
        self.size_t, self.size_c, self.size_z, self.size_y, self.size_x = tuple(self.shape)

    def is_valid_dimension(self, dimensions):
        if dimensions.strip(self.dims):
            # dims contains more than the standard 5 dims we're used to
            raise ValueError("{} contains invalid dimensions!".format(dimensions))

        count = {}
        for char in dimensions:
            if char in count:
                raise ValueError("{} contains duplicate dimensions!".format(dimensions))
            else:
                count[char] = 1

        return True

    def _generate_size(self):
        self.shape = []
        # create a map of dimensions -> value in the data array that was passed in originally
        dim_map = {self.dims[i]: self.data.shape[i] for i in range(len(self.dims))}
        for dim in AICSImage.default_dims:
            self.shape.append(dim_map.get(dim, 1))

    # TODO get_reference_data if user is not going to manipulate data
    # TODO (minor) allow uppercase and lowercase kwargs
    def get_image_data(self, out_orientation="TCZYX", **kwargs):
        """

        :param out_orientation: A string containing the dimension ordering desired for the returned ndarray
        :param kwargs: These can contain the dims you exclude from out_orientation (out of the set "TCZYX").
                       If you want all slices of ZYX, but only one from T and C, you can enter:
                       >>> image.get_image_data("ZYX", T=1, C=3)
                       Unspecified dimensions that are left of out the out_orientation default to 0.
        :return: ndarray with dimension ordering that was specified with out_orientation
        """
        image_data = self.data.copy()
        if out_orientation != self.dims and self.is_valid_dimension(out_orientation):
            # map each dimension (TCZYX) to its index in out_orientation
            match_map = {dim: out_orientation.find(dim) for dim in self.dims}
            slicer, transposer = [], []
            for dim in self.dims:
                if match_map[dim] == -1:
                    # only get the bottom slice of this dimension, unless the user specified another in the args
                    slice_value = kwargs.get(dim, 0)
                    if slice_value >= self.shape[self.dims.find(dim)] or slice_value < 0:
                        raise ValueError("{} is not a valid index for the {} dimension".format(slice_value, dim))
                    slicer.append(slice_value)
                else:
                    # append all slices of this dimension
                    slicer.append(slice(None, None))
                    transposer.append(match_map[dim])
            image_data = image_data[slicer].transpose(transposer)

        return image_data