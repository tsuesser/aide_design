# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 13:57:23 2017

@author: cc2467
"""
import math

from scipy import constants, interpolate

#see numpy cheat sheet https://www.dataquest.io/blog/images/cheat-sheets/numpy-cheat-sheet.pdf
#The numpy import is needed because it is renamed here as np.
import numpy as np

import pandas as pd

import matplotlib.pyplot as plt

import sys, os

myGitHubdir=os.path.expanduser('~\\Documents\\GitHub')
if myGitHubdir not in sys.path:
    sys.path.append(myGitHubdir)

from AguaClara_design import physchem as pc

from AguaClara_design import pipedatabase as pipe

from AguaClara_design.units import unit_registry as u 

from AguaClara_design import utility as ut

from AguaClara_design import expert_inputs as exp

#==============================================================================
# Functions for Coagulant Viscosities and Selecting Available Tube Diameters
#==============================================================================

def _DiamTubeAvail(en_tube_series = True):
    if en_tube_series:    
        return 1*u.mm
    else:
        return (1/16)*u.inch

NU_WATER = 1*(u.mm**2/u.s)

def _nu_alum(conc_alum):
    nu = (1 + (4.255 * 10**-6) * conc_alum**2.289) * NU_WATER
    return nu.to(u.mm**2/u.s)
    
def _nu_pacl(conc_pacl):
    nu = (1 + (2.383 * 10**-5) * conc_pacl**1.893) * NU_WATER
    return nu.to(u.mm**2/u.s)
    
def _nu_chem(conc_chem, en_chem):
    if en_chem == 0:
        return _nu_alum(conc_chem)
    elif en_chem == 1:
        return _nu_pacl(conc_chem)
    else:
        return NU_WATER

  
    
#==============================================================================
# Flow rate Constraints for Laminar Tube Flow, Deviation from Linear Head Loss
# Behavior, and Lowest Possible Flow 
#==============================================================================

# Maximum flow that can be put through a tube of a given diameter without 
# exceeding the allowable deviation from linear head loss behavior
def _flow_available(Diam, HeadlossCDC):
    flow = math.pi * Diam**2 / 4 * (((
                2 * exp.RATIO_LINEAR_CDC_ERROR * HeadlossCDC * pc.gravity)/
                    exp.K_MINOR_CDC_TUBE)**1/2)
    return flow




#==============================================================================
# Length of Tubing Required Given Head Loss, Max Flow, and Diameter 
#==============================================================================

# Length of tube required to get desired head loss at maximum flow based on 
# the Hagen-Poiseuille equation.    

def _len_tube(flow, Diam, headloss, nu, k_minor):
    len = (((headloss*pc.gravity*math.pi*(Diam**4)/flow
             )-(k_minor*8*flow/math.pi
                ))/(128*nu))
    return len



#==============================================================================
# Helper Functions     
#==============================================================================

def _n_tube_array(FlowPlant, ConcDoseMax, ConcStock, 
                  DiamTubeAvail, HeadlossCDC): 
    
    math.ceil((FlowPlant * ConcDoseMax
               )/ ConcStock*_flow_available(DiamTubeAvail, HeadlossCDC)) 


def _flow_chem_stock(FlowPlant, ConcDoseMax, ConcStock):
    FlowPlant * ConcDoseMax / ConcStock 
    

def _flow_cdc_tube(FlowPlant, ConcDoseMax, ConcStock, 
                   DiamTubeAvail, HeadlossCDC):
    
    (_flow_chem_stock(FlowPlant, ConcDoseMax, ConcStock)
     ) / (_n_tube_array(FlowPlant, ConcDoseMax, ConcStock, 
                        DiamTubeAvail, HeadlossCDC)
          )
    
    
# Calculate the length of each diameter tube given the corresponding flow rate
# and coagulant 
# Choose the tube that is shorter than the maximum length tube.
def _length_cdc_tube_array(FlowPlant, ConcDoseMax, ConcStock, 
                           DiamTubeAvail, HeadlossCDC, ENCoag, MinorLossCDCTube):
    
    _len_tube(_flow_cdc_tube(FlowPlant, ConcDoseMax, ConcStock, 
                             DiamTubeAvail, HeadlossCDC
                             ) , DiamTubeAvail, HeadlossCDC, _nu_chem(ConcStock, ENCoag
                                                                      ), MinorLossCDCTube)

# Find the index of that tube
def i_cdc(FlowPlant, ConcDoseMax, ConcStock, 
          DiamTubeAvail, HeadlossCDC, LenCDCTubeMax, 
          ENCoag, MinorLossCDCTube):
    
    tube_array = _length_cdc_tube_array(FlowPlant, ConcDoseMax, ConcStock, 
                                        DiamTubeAvail, HeadlossCDC, ENCoag, 
                                        MinorLossCDCTube)
    if tube_array[0] < LenCDCTubeMax:
        if LenCDCTubeMax < 
    