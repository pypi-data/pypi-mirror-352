#!/usr/bin/env python

import unittest

from tests.script_runner import ScriptRunner
from tests import test_module


class ArrayTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()
        self._output = test_module.replace_print()
        self._runner = ScriptRunner(self)

    def test_minimal(self):
        script = """
            declare a[10]
            assign a[5] 100
            print a[5]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 100)

    def test_2d(self):
        script = """
            declare b[100]
            assign b[20] 30
            print b[20]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 30)

    def test_nested(self):
        script = """
            declare outer[10]
            declare inner[5]

            repeat with i from 0 to 9
                assign outer[i] {i* 20}
            assign inner[3] 5
            assign inner[0] 3
            print outer[inner[inner[0]]]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 100)

    def test_as_param(self):
        script = """
            define f with array[] index begin
                return array[index]
            end

            declare v[10]
            repeat with i from 0 to 9
                assign v[i] {i* 50}
            print [f v 5]
        """
        self._runner.run_script(script)
        self.assertEqual(self._output.get_object(), 250)

    def test_partial_deref(self):
        script = """
            define f with a[] i begin
                return a[i]
            end

            declare y[10][20]
            assign y[5][10] 200

            println [f y[5] 10]
        """
        self._runner.run_script(script)
        # self.assertEqual(self._output.get_object(), 200)


if __name__ == '__main__':
    unittest.main()
