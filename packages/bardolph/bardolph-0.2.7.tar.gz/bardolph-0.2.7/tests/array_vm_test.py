#!/usr/bin/env python

import unittest

from bardolph.vm.array import Array


class ArrayVmTest(unittest.TestCase):
    def test_vector(self):
        array = Array(25)
        array.deref(5)
        array.set_value(100)
        array.deref(6)
        array.deref(5)
        self.assertEqual(100, array.get_value())

    def test_matrix2(self):
        # 5 x 10
        array = Array(5)
        array.add_dimension(10)

        # assign 100 to the element at [1][2]
        array.deref(1)
        array.index(2)
        array.set_value(100)

        # assign 200 to the element at [4][7]
        array.deref(4)
        array.index(7)
        array.set_value(200)

        array.deref(4)
        array.index(7)
        self.assertEqual(200, array.get_value())

        array.deref(1)
        array.index(2)
        self.assertEqual(100, array.get_value())

    def test_none_deref(self):
        array = Array(10)
        array.deref()
        array.index(6)
        array.set_value(100)
        array.deref(7)
        array.deref(6)
        self.assertEqual(100, array.get_value())

    def test_none_deref_2d(self):
        # 10 x 20
        array = Array(10)
        array.add_dimension(20)
        array.deref()
        array.index(5)
        array.index(9)
        array.set_value(500)
        array.deref(5)
        array.index(9)
        self.assertEqual(500, array.get_value())


if __name__ == '__main__':
    unittest.main()
