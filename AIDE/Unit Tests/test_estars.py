# -*- coding: utf-8 -*-
"""
Created on Thu Aug  17 11:51:51 2017

@author: Ethan Keller

Last modified: Thu Aug 17 2017
By: Ethan Keller
"""

#Note: All answer values in this file should be checked against MathCad
#before this file is released to the Master branch!

import unittest

import sys, os
from AIDE.units import unit_registry as u
from AIDE import physchem as pc
from AIDE.unit_process_design.prefab import estars

class EstarsTest(unittest.TestCase):
    def test_filter_body_size(self):
        '''These filter flow rates should result in these filter body sizes'''
        checks


if __name__ == "__main__":
    unittest.main()
