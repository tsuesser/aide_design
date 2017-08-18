# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 15:31:16 2017

@author: eak244
"""
import math
from scipy import constants, interpolate
import numpy as np

from AIDE import physchem as pc
from AIDE import pipedatabase as pipe
from AIDE.units import unit_registry as u
from AIDE import utility as ut

#The following constants need to go into a constants file.

# pipe schedule for trunks
SDR_TRUNK = 26
FLOW = 1.8*u.L/u.s
ratio_VC_orifice= 0.62
HEIGHT_FILTER_LAYER_LOW = 0.2*u.m
VELOCITY_BACKWASH = 0.011 *u.m/u.s

# determine the pipe size for the filter body
def filter_body_size(bw_velocity, flow, sdr):
    id=flow/bw_velocity
    return pipe.ND_SDR_available(id, sdr)