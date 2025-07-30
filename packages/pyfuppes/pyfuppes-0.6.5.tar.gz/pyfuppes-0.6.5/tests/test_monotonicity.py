# SPDX-FileCopyrightText: 2025 Florian Obersteiner / KIT
# SPDX-FileContributor: Florian Obersteiner <f.obersteiner@kit.edu>
#
# SPDX-License-Identifier: LGPL-3.0-or-later

import unittest

import numpy as np

from pyfuppes import monotonicity


class TestMonotonicity(unittest.TestCase):
    def test_strictly_increasing(self):
        self.assertTrue(monotonicity.strictly_increasing([1, 2, 3]))
        self.assertFalse(monotonicity.strictly_increasing([1, 2, 2]))
        self.assertFalse(monotonicity.strictly_increasing([1, 1, 3]))

    def test_strictly_decreasing(self):
        self.assertTrue(monotonicity.strictly_decreasing([3, 2, 1]))
        self.assertFalse(monotonicity.strictly_decreasing([3, 2, 2]))
        self.assertFalse(monotonicity.strictly_decreasing([3, 3, 1]))

    def test_non_increasing(self):
        self.assertTrue(monotonicity.non_increasing([1, 1, 1]))
        self.assertTrue(monotonicity.non_increasing([1, 1, -2]))
        self.assertFalse(monotonicity.non_increasing([1, 1, 3]))

    def test_non_decreasing(self):
        self.assertTrue(monotonicity.non_decreasing([1, 2, 3]))
        self.assertTrue(monotonicity.non_decreasing([1, 2, 2]))
        self.assertTrue(monotonicity.non_decreasing([2, 2, 2]))
        self.assertFalse(monotonicity.non_decreasing([1, 1, -3]))

    def test_strictly_inc_np(self):
        self.assertTrue(monotonicity.strict_inc_np(np.array([1, 2, 3])))
        self.assertFalse(monotonicity.strict_inc_np(np.array([1, 2, 2])))
        self.assertFalse(monotonicity.strict_inc_np(np.array([1, 1, 3])))

    def test_strictly_dec_np(self):
        self.assertTrue(monotonicity.strict_dec_np(np.array([3, 2, 1])))
        self.assertFalse(monotonicity.strict_dec_np(np.array([3, 2, 2])))
        self.assertFalse(monotonicity.strict_dec_np(np.array([3, 3, 1])))

    def test_non_inc_np(self):
        self.assertTrue(monotonicity.non_inc_np(np.array([2, 2, 2])))
        self.assertFalse(monotonicity.non_inc_np(np.array([1, 2, 2])))
        self.assertFalse(monotonicity.non_inc_np(np.array([1, 1, 3])))

    def test_non_dec_np(self):
        self.assertTrue(monotonicity.non_dec_np(np.array([1, 2, 3])))
        self.assertTrue(monotonicity.non_dec_np(np.array([2, 2, 2])))
        self.assertFalse(monotonicity.non_dec_np(np.array([1, -2, 2])))
        self.assertFalse(monotonicity.non_dec_np(np.array([1, 1, -3])))


if __name__ == "__main__":
    unittest.main()
