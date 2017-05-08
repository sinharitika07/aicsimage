# author: Zach Crabtree zacharyc@alleninstitute.org

import unittest
import numpy as np
import random
import os

from aicsimage.processing import aicsImage


class AicsImageTestGroup(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.__init__(self)

    def runTest(self):
        # this method has to be included in a testgroup in order for it be run
        self.assertTrue(True)

    def test_transposedOutput(self):
        # arrange
        input_shape = random.sample(range(1, 10), 5)
        stack = np.zeros(input_shape)
        image = aicsImage.AICSImage(stack, dims="TCZYX")
        # act
        output_array = image.get_image_data("XYZCT")
        stack = stack.transpose((4, 3, 2, 1, 0))
        # assert
        self.assertEqual(output_array.all(), stack.all())

    def test_slicedOutput(self):
        # arrange
        input_shape = random.sample(range(1, 20), 5)
        t_max, c_max = input_shape[0], input_shape[1]
        t_rand, c_rand = random.randint(0, t_max-1), random.randint(0, c_max-1)
        stack = np.zeros(input_shape)
        stack[t_rand, c_rand] = 1
        image = aicsImage.AICSImage(stack, dims="TCZYX")
        # act
        output_array = image.get_image_data("ZYX", T=t_rand, C=c_rand)
        # assert
        self.assertEqual(output_array.all(), 1)

    def test_fewDimensions(self):
        input_shape = random.sample(range(1, 20), 3)
        stack = np.zeros(input_shape)
        image = aicsImage.AICSImage(stack, dims="CTX")
        self.assertEqual(image.data.shape, image.shape)

    def test_fromFileName(self):
        # arrange and act
        dir_path = os.path.dirname(os.path.realpath(__file__))
        image = aicsImage.AICSImage(os.path.join(dir_path, 'img', 'img40_1.ome.tif'))
        # assert
        self.assertIsNotNone(image)

    def test_fromInvalidFileName(self):
        # arrange, act, assert
        with self.assertRaises(AssertionError):
            aicsImage.AICSImage("fakeimage.ome.tif")
