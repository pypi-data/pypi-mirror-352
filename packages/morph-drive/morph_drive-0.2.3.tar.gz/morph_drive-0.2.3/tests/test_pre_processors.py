import unittest

import numpy as np

from morph_drive.pre_processors.BasicDataPreprocessor import BasicDataPreprocessor


class TestBasicDataPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = BasicDataPreprocessor(quantum=1.0, min_threshold=0.5)

    def test_process_string_normal_case_n3(self):
        obs = self.preprocessor.process("10.2,20.7,-5.3", n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0, -5.0], dtype=np.float32)
        )

    def test_process_string_normal_case_n2(self):
        obs = self.preprocessor.process("10.2,20.7,-5.3", n=2)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0], dtype=np.float32)
        )

    def test_process_string_fewer_elements_than_n(self):
        obs = self.preprocessor.process("10.2", n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_process_string_more_elements_than_n_parsed(self):
        # Current implementation parses only up to n elements from string
        obs = self.preprocessor.process("10.2,20.7,-5.3,30.0", n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0, -5.0], dtype=np.float32)
        )

    def test_process_string_non_numeric_first(self):
        obs = self.preprocessor.process("abc,20.7,-5.3", n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_process_string_non_numeric_middle(self):
        obs = self.preprocessor.process("10.2,abc,-5.3", n=3)
        # The updated logic parses parts then converts. If "abc" is part of selected_parts[:n]
        # and float("abc") fails, it defaults all to 0.0 for that specific parsing attempt.
        np.testing.assert_array_almost_equal(
            obs, np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_process_string_empty(self):
        obs = self.preprocessor.process("", n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_process_string_empty_n0(self):
        obs = self.preprocessor.process("", n=0)
        np.testing.assert_array_almost_equal(obs, np.array([], dtype=np.float32))

    def test_process_string_just_commas(self):
        obs = self.preprocessor.process(",,,", n=3)
        # Expects parts like '', '', '' which will cause ValueError on float conversion
        np.testing.assert_array_almost_equal(
            obs, np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_process_list_input(self):
        obs = self.preprocessor.process([10.2, 20.7, -5.3], n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0, -5.0], dtype=np.float32)
        )

    def test_process_list_input_n_is_kwarg_only(self):
        obs = self.preprocessor.process(
            [10.2, 20.7, -5.3, 99.9], n=2
        )  # n=2 should be ignored for list input
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0, -5.0, 100.0], dtype=np.float32)
        )

    def test_process_numpy_array_input(self):
        obs = self.preprocessor.process(np.array([10.2, 20.7, -5.3]), n=3)
        np.testing.assert_array_almost_equal(
            obs, np.array([10.0, 21.0, -5.0], dtype=np.float32)
        )

    def test_process_unsupported_type(self):
        obs = self.preprocessor.process(12345, n=3)  # Integer input
        np.testing.assert_array_almost_equal(
            obs, np.array([0.0, 0.0, 0.0], dtype=np.float32)
        )

    def test_quantization_and_thresholding(self):
        self.preprocessor_custom = BasicDataPreprocessor(quantum=0.5, min_threshold=0.1)
        obs = self.preprocessor_custom.process(
            "0.3,0.7,0.05", n=3
        )  # 0.05 should be zeroed
        np.testing.assert_array_almost_equal(
            obs, np.array([0.5, 0.5, 0.0], dtype=np.float32)
        )

        obs_near_zero = self.preprocessor_custom.process(
            "0.09,-0.09", n=2
        )  # Should be zeroed by min_threshold
        np.testing.assert_array_almost_equal(
            obs_near_zero, np.array([0.0, 0.0], dtype=np.float32)
        )


if __name__ == "__main__":
    unittest.main()
