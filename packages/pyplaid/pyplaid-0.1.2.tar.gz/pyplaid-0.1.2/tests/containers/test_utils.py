# -*- coding: utf-8 -*-
#
# This file is subject to the terms and conditions defined in
# file 'LICENSE.txt', which is part of this source code package.
#
#

# %% Imports

import pytest

import numpy as np

from pathlib import Path

from plaid.containers.utils import get_number_of_samples, get_sample_ids

# %% Fixtures

@pytest.fixture()
def current_directory():
    return Path(__file__).absolute().parent

# %% Tests

class Test_Container_Utils():

    def test_get_sample_ids(self, current_directory):
        dataset_path = current_directory / "dataset"
        assert get_sample_ids(dataset_path) == list(np.arange(0, 3))

    def test_get_number_of_samples(self, current_directory):
        dataset_path = current_directory / "dataset"
        assert get_number_of_samples(dataset_path) == 3

    def test_get_sample_ids_with_str(self, current_directory):
        dataset_path = current_directory / "dataset"
        assert get_sample_ids(str(dataset_path)) == list(np.arange(0, 3))

    def test_get_number_of_samples_with_str(self, current_directory):
        dataset_path = current_directory / "dataset"
        assert get_number_of_samples(str(dataset_path)) == 3
