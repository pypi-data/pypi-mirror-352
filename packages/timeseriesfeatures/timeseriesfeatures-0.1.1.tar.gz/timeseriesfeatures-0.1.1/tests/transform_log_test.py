"""Tests for the log transform"""
import os
import unittest

import pandas as pd

from timeseriesfeatures.transform_log import log_transform


class TestLogTransform(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_log_transform(self):
        series = pd.Series(data=[10.0, 20.0, 30.0])
        transformed_series = log_transform(series)
        self.assertListEqual(transformed_series.to_list(), [2.3978952727983707, 3.044522437723423, 3.4339872044851463])
