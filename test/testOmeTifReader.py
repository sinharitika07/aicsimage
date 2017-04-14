#!/usr/bin/env python

# authors: Dan Toloudis     danielt@alleninstitute.org
#          Zach Crabtree    zacharyc@alleninstitute.org

import os
import unittest

import numpy as np

import imageio
from imageio.omeTifReader import OmeTifReader


class OmeTifReaderTestGroup(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        imageio.init()
        cls.dir_path = os.path.dirname(os.path.realpath(__file__))
        with OmeTifReader(os.path.join(cls.dir_path, 'img', 'img40_1.ome.tif')) as reader:
            cls.load = reader.load()
            cls.slice = reader.load_slice()
            cls.load_image = np.ndarray([reader.size_t(), reader.size_z(), reader.size_c(), reader.size_y(),
                                         reader.size_x()])
            for i in range(reader.size_t()):
                for j in range(reader.size_z()):
                    for k in range(reader.size_c()):
                        cls.load_image[i, j, k, :, :] = reader.load_slice(t=i, z=j, c=k)

    @classmethod
    def tearDownClass(cls):
        imageio.close()

    def test_omeTifLoadShapeCorrectDimensions(self):
        self.assertEqual(len(self.load.shape), 5)

    def test_omeTifLoadSliceShapeCorrectDimensions(self):
        self.assertEqual(len(self.slice.shape), 2)

    def test_omeTifLoadCompareLoadImage(self):
        self.assertTrue(np.array_equal(self.load, self.load_image))

    def test_omeTifEmptyFileError(self):
        with self.assertRaises(Exception):
            with OmeTifReader('fakefile') as reader:
                reader.load()

    def test_notOmeTifFile(self):
        with self.assertRaises(Exception):
            with OmeTifReader(os.path.join(self.dir_path, 'img', 'T=5_Z=3_CH=2_CZT_All_CH_per_Slice.czi')) as reader:
                reader.load()