"""Tests for the process function."""
import json
import os
import unittest

import pandas as pd

from tsuniverse.process import process


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.dir = os.path.dirname(__file__)

    def test_process(self):
        df = pd.read_parquet(os.path.join(self.dir, "universe.parquet"))
        features = list(process(df, [df.columns.values.tolist()[0]], 30))
        #with open(os.path.join(self.dir, "expected.json"), "w") as handle:
        #    json.dump(features, handle)
        with open(os.path.join(self.dir, "expected.json")) as handle:
            expected_features = json.load(handle)
            self.assertListEqual(features, expected_features)
