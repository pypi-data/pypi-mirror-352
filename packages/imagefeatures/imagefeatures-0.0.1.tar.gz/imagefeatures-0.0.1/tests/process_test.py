"""Tests for the process function."""
import os
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal
import requests_mock
import requests

from imagefeatures.process import process


class TestProcess(unittest.TestCase):

    def setUp(self):
        self.session = requests.Session()
        self.dir = os.path.dirname(__file__)

    def test_process(self):
        image_url = "https://www.image.com/image.png"
        image_col = "image"
        with requests_mock.Mocker() as m:
            with open(os.path.join(self.dir, "1006130.png"), "rb") as f:
                m.get(image_url, content=f.read())
            df = pd.DataFrame(data={image_col: [image_url]})
            df = process(df, {image_col}, self.session)
        print(df)
        df.to_parquet("expected.parquet")
        #expected_features_df = pd.read_parquet(os.path.join(self.dir, "expected.parquet"))
        #assert_frame_equal(df, expected_features_df)
