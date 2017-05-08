#!/usr/bin/env python

# author: Zach Crabtree zacharyc@alleninstitute.org

import unittest

from aicsimage.io.tifReader import TifReader
from aicsimage.processing.aicsImage import AICSImage
from aicsimage.processing.segmentation import nucleusSegmentation


class NucleusSegmentationTestGroup(unittest.TestCase):

    def test_Segmentation(self):
        cell_index_im = TifReader("img/segmentation/input_1_cellWholeIndex.tiff").load()
        nuc_index_im = TifReader("img/segmentation/input_2_nucWholeIndex.tiff").load()
        original_im = TifReader("img/segmentation/input_3_nuc_orig_img.tiff").load()

        image = nucleusSegmentation.fill_nucleus_segmentation(cell_index_im, nuc_index_im, original_im)