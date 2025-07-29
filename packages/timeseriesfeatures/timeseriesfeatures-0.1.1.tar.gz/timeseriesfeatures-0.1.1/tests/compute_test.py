"""Tests for the compute function."""
import datetime
import os
import unittest
import json

import pandas as pd
from pandas.testing import assert_frame_equal

from timeseriesfeatures.compute import compute
from timeseriesfeatures.process import process


class TestCompute(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_compute(self):
        rows = 500
        df = pd.DataFrame(data={
            "feature1": [float(x) for x in range(rows)],
            "feature2": [float(x + 1) for x in range(rows)],
        }, index=[
            datetime.datetime(2022, 1, 1) + datetime.timedelta(x) for x in range(rows)
        ])
        features = compute(df, 30, 14)
        #with open("expected.json", "w") as handle:
        #    json.dump(features, handle)
        with open(os.path.join(self.dir, "expected.json")) as handle:
            expected_features = json.load(handle)
        self.assertListEqual(features, expected_features)
        df = process(df, features)
        print(df)
        #df.to_parquet("compute.parquet")
        expected_features_df = pd.read_parquet(os.path.join(self.dir, "compute.parquet"))
        assert_frame_equal(df, expected_features_df)
