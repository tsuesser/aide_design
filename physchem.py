"""
Created on Thu Jun 15 14:07:28 2017

@author: Karan Newatia

Last modified: Mon Jul 10 2017 
By: Sage Weber-Shirk


This file contains unit process functions pertaining to the design of 
physical/chemical unit processes for AguaClara water treatment plants.
"""

######################### Imports #########################
import numpy as np
import scipy

try:
    from AguaClara_design.units import unit_registry as u
except:
      from units import unit_registry as u

gravity = 9.80665 * u.m/u.s**2
"""Define the gravitational constant, in m/s²."""

#######################Simple geometry#######################
"""A few equations for useful geometry.
Is there a geometry package that we should be using?"""

def area_circle(DiamCircle):
    """Return the area of a circle."""
    if DiamCircle <= 0:
        raise ValueError("Diameter must be greater than zero.")
    return np.pi / 4 * DiamCircle**2


@u.wraps(u.m, u.m**2, False)
def diam_circle(AreaCircle):
    """Return the diameter of a circle."""
    if AreaCircle <= 0:
        raise ValueError("Area must be greater than zero.")
    return np.sqrt(4 * AreaCircle / np.pi)

######################### Hydraulics ######################### 
RATIO_VC_ORIFICE = 0.62

RE_TRANSITION_PIPE = 2100



WATER_DENSITY_TABLE = [(273.15, 278.15, 283.15, 293.15, 303.15, 313.15, 
                        323.15, 333.15, 343.15, 353.15, 363.15, 373.15
                        ), (999.9, 1000, 999.7, 998.2, 995.7, 992.2, 
                            988.1, 983.2, 977.8, 971.8, 965.3, 958.4
                            )
                       ]
"""Table of temperatures and the corresponding water density.

Index[0] is a list of water temperatures, in Kelvin.
Index[1] is the corresponding densities, in kg/m³.
"""


@u.wraps(u.kg/(u.m*u.s), [u.degK], False)
def viscosity_dynamic(T):
    """Return the dynamic viscosity of water at a given temperature.
    
    If given units, the function will automatically convert to Kelvin.
    If not given units, the function will assume Kelvin.
    """
    return 2.414 * (10**-5) * 10**((247.8)/(T-140))


@u.wraps(u.kg/u.m**3, [u.degK], False)
def density_water(temp):
    """Return the density of water at a given temperature.
    
    If given units, the function will automatically convert to Kelvin.
    If not given units, the function will assume Kelvin.
    """
    rhointerpolated = scipy.interpolate.CubicSpline(WATER_DENSITY_TABLE[0], 
                                                    WATER_DENSITY_TABLE[1])
    return rhointerpolated(temp)


@u.wraps(u.m**2/u.s, [u.degK], False)
def viscosity_kinematic(T):
    """Return the kinematic viscosity of water at a given temperature.
    
    If given units, the function will automatically convert to Kelvin.
    If not given units, the function will assume Kelvin.
    """
    return (viscosity_dynamic(T).magnitude 
            / density_water(T).magnitude)


@u.wraps(None, [u.m**3/u.s, u.m, u.m**2/u.s], False)
def re_pipe(FlowRate, Diam, Nu):
    """Return the Reynolds Number for a pipe."""         
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
        
    return (4 * FlowRate) / (np.pi * Diam * Nu)


@u.wraps(u.m, [u.m, u.m, None], False)
def radius_hydraulic(Width, DistCenter, openchannel):
    """Return the hydraulic radius."""  
    if not (Width and DistCenter) > 0:
        raise ValueError("Width and distance must be greater than 0.")
        
    if openchannel:
        h = (Width*DistCenter) / (Width + 2*DistCenter)
        # if openchannel is True, the channel is open. Otherwise, the channel 
        # is assumed to have a top. 
    else:
        h = (Width*DistCenter) / (2 * (Width+DistCenter))
    return h


@u.wraps(u.m, [u.m**2, u.m], False)
def radius_hydraulic_general(Area, WP):
    """Return the general hydraulic radius."""
    if not (Area and WP) > 0:
        raise ValueError("Area and wetted perimeter must be greater than 0.")
    return Area / WP 


@u.wraps(None, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, None], False)
def re_rect(FlowRate, Width, DistCenter, Nu, openchannel):
    """Return the Reynolds Number for a rectangular channel."""
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if FlowRate <= 0:
        raise ValueError("Flow rate must be greater than 0.")
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
        
    return (4 * FlowRate 
            * radius_hydraulic(Width, DistCenter, openchannel).magnitude
            / (Width * DistCenter * Nu))
    #Reynolds Number for rectangular channel; open = False if all sides
    #are wetted; l = Diam and Diam = 4*R.h     
    

@u.wraps(None, [u.m/u.s, u.m**2, u.m, u.m**2/u.s], False)
def re_general(Vel, Area, WP, Nu):
    """Return the Reynolds Number for a general cross section."""
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if Vel <= 0:
        raise ValueError("Velocity must be greater than 0.")
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
        
    return 4 * radius_hydraulic_general(Area, WP).magnitude * Vel / Nu
        

@u.wraps(None, [u.m**3/u.s, u.m, u.m**2/u.s, u.m], False)
def fric(FlowRate, Diam, Nu, PipeRough):
    """Return the friction factor for pipe flow.
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
        
    if re_pipe(FlowRate, Diam, Nu) >= RE_TRANSITION_PIPE:
        #Swamee-Jain friction factor for turbulent flow; best for 
        #Re>3000 and ε/Diam < 0.02        
        f = (0.25 / (np.log10(PipeRough/(3.7*Diam) + 5.74 
                                / re_pipe(FlowRate, Diam, Nu)**0.9
                                )
                     ) ** 2
             )
    else:
        f = 64 / re_pipe(FlowRate, Diam, Nu)
    return f


@u.wraps(None, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m, None], False)
def fric_rect(FlowRate, Width, DistCenter, Nu, PipeRough, openchannel):
    """Return the friction factor for a rectangular channel."""
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if not 0 < PipeRough < 1:
        raise ValueError("Pipe roughness should be between 0 and 1.")
        
    if re_rect(FlowRate,Width,DistCenter,Nu,openchannel) >= RE_TRANSITION_PIPE:
        #Swamee-Jain friction factor adapted for rectangular channel.
        #Diam = 4*R_h in this case.         
        f = (0.25 
             / (np.log10(PipeRough 
                           / ((3.7 * 4 
                               * radius_hydraulic(Width, DistCenter, openchannel)
                               ) + 5.74
                              ) 
                           / re_rect(FlowRate, Width, DistCenter, Nu,
                                     openchannel) ** 0.9
                           )
                ) ** 2
             )
    else:
        f = 64 / re_rect(FlowRate, Width, DistCenter, Nu, openchannel)
    return f
 

@u.wraps(None, [u.m**2, u.m, u.m/u.s, u.m**2/u.s, u.m], False)
def fric_general(Area, PerimWetted, Vel, Nu, PipeRough):
    """Return the friction factor for a general channel."""
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if not 0 < PipeRough < 1:
        raise ValueError("Pipe roughness should be between 0 and 1.")
        
    if re_general(Vel, Area, PerimWetted, Nu) >= RE_TRANSITION_PIPE:
        #Swamee-Jain friction factor adapted for any cross-section.
        #Diam = 4*R*h 
        f= (0.25 /
            (np.log10(PipeRough
                      / (3.7 * 4 * radius_hydraulic_general(Area, PerimWetted))
                      + 5.74
                      / re_general(Vel, Area, PerimWetted, Nu) ** 0.9
                      )
             ) ** 2
            )
    else:
        f = 64 / re_general(Vel, Area, PerimWetted, Nu)
    return f      
         

@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m], False)
def headloss_fric(FlowRate, Diam, Length, Nu, PipeRough):
    """Return the major head loss (due to wall shear) in a pipe.
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if Length <= 0:
        raise ValueError("Length must be greater than 0.")
    return (fric(FlowRate, Diam, Nu, PipeRough)
            * 8 / (gravity.magnitude * np.pi**2) 
            * (Length * FlowRate**2) / Diam**5
            )


@u.wraps(u.m, [u.m**3/u.s, u.m, None], False)
def headloss_exp(FlowRate, Diam, KMinor):
    """Return the minor head loss (due to expansions) in a pipe. 
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity
    if not (FlowRate and Diam) > 0:
        raise ValueError("Inputs must be greater than 0.")
    if KMinor < 0:
        raise ValueError("Minor loss must not be negative.")
        
    return KMinor * 8 / (gravity.magnitude * np.pi**2) * FlowRate**2 / Diam**4


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m, None], False)
def headloss(FlowRate, Diam, Length, Nu, PipeRough, KMinor):
    """Return the total head loss from major and minor losses in a pipe.
    
    This equation applies to bh laminar and turbulent flows.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls
    para = [FlowRate, Diam, Length, Nu, PipeRough, KMinor]
    for i in range(6):
        if isinstance(para[i],list):
            index = i
            para[i] = np.array(para[i])
    size = len(para[index])
    hl = []
    for i in range(size): 
        temp = [0,0,0,0,0,0]
        for j in range(6):
            temp[j]=para[j]
            if j==index:
                temp[index]=para[index][i]
    
        headloss = ((headloss_fric(temp[0], temp[1], temp[2], temp[3], temp[4]).magnitude)
        + (headloss_exp(temp[0], temp[1], temp[5]).magnitude))
        hl.append(headloss)
      

    return hl


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m, u.m**2/u.s, u.m, None], False)
def headloss_fric_rect(FlowRate, Width, DistCenter, Length, Nu, PipeRough, openchannel):
    """Return the major head loss due to wall shear in a rectangular channel.
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if Length <= 0:
        raise ValueError("Length must be greater than 0")
        
    return (fric_rect(FlowRate, Width, DistCenter, Nu, 
                      PipeRough, openchannel).magnitude 
            * Length 
            / (4 * radius_hydraulic(Width, DistCenter, openchannel)) 
            * FlowRate**2 
            / (2 * gravity.magnitude * (Width*DistCenter)**2)
            )


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, None], False)
def headloss_exp_rect(FlowRate, Width, DistCenter, KMinor):
    """Return the minor head loss due to expansion in a rectangular channel.
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity
    if not (FlowRate and Width and DistCenter) > 0:
        raise ValueError("Flow rate, width, and distance must be greater than 0.")
    if KMinor < 0:
        raise ValueError("Headloss must not be negative.")
    
    return KMinor * FlowRate**2 / (2 * gravity.magnitude * (Width*DistCenter)**2) 
 

@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m, None, u.m**2/u.s, u.m, None], False)
def headloss_rect(FlowRate, Width, DistCenter, Length, 
                  KMinor, Nu, PipeRough, openchannel):
    """Return the total head loss in a rectangular channel. 
    
    Total head loss is a combination of the major and minor losses.
    This equation applies to both laminar and turbulent flows.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    return (headloss_exp_rect(FlowRate, Width, DistCenter, KMinor).magnitude
              + headloss_fric_rect(FlowRate, Width, DistCenter, Length, 
                                   Nu, PipeRough, openchannel).magnitude)
    

@u.wraps(u.m, [u.m**2, u.m, u.m/u.s, u.m, u.m**2/u.s, u.m], False)
def headloss_fric_general(Area, PerimWetted, Vel, Length, Nu, PipeRough):
    """Return the major head loss due to wall shear in the general case.
 
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if Length <= 0:
        raise ValueError("Length must be greater than 0.")
    
    return (fric_general(Area, PerimWetted, Vel, Nu, PipeRough) * Length 
            / (4 * radius_hydraulic_general(Area, PerimWetted).magnitude) 
            * Vel**2 / (2*gravity.magnitude)
            )
     

@u.wraps(u.m, [u.m/u.s, None], False)
def headloss_exp_general(Vel, KMinor):
    """Return the minor head loss due to expansion in the general case.
    
    This equation applies to both laminar and turbulent flows.
    """
    #Checking input validity
    if Vel <= 0:
        raise ValueError("Velocity must be greater than 0.")
    if KMinor < 0:
        raise ValueError("Minor loss must not be negative.")
    return KMinor * Vel**2 / (2*gravity.magnitude)


@u.wraps(u.m, [u.m**2, u.m/u.s, u.m, u.m, None, u.m**2/u.s, u.m], False)
def headloss_gen(Area, Vel, PerimWetted, Length, KMinor, Nu, PipeRough):
    """Return the total head lossin the general case.
 
    Total head loss is a combination of major and minor losses.
    This equation applies to both laminar and turbulent flows.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    return (headloss_exp_general(Vel, KMinor).magnitude 
            + headloss_fric_general(Area, PerimWetted, Vel,
                                     Length, Nu, PipeRough).magnitude)

 
@u.wraps(u.m, [u.m**2/u.s, u.m, u.m, None, u.m**2/u.s, u.m, None], False)  
def headloss_manifold(FlowRate, Diam, Length, KMinor, Nu, PipeRough, NumOutlets):
    """Return the total head loss through the manifold."""
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if NumOutlets <= 0:
        raise ValueError("There must be at least one outlet.")
    return (headloss(FlowRate, Diam, Length, Nu, PipeRough, KMinor).magnitude
            * (1/3 
               + 1 / (2*NumOutlets) 
               + 1 / ((6*NumOutlets)**2))
            )


@u.wraps(u.m**3/u.s, [u.m, u.m, None], False)
def flow_orifice(Diam, Height, RatioVCOrifice):
    """Return the flow rate of the orifice."""
    #Checking input validity
    if not 0 < RatioVCOrifice < 1:
        raise ValueError("RatioVCOrifice should be between 0 and 1.")   
    Height = np.array(Height)
    Height.tolist()
    FlowRate = []
    for i in range(len(Height)):
         if Height[i] > 0:
            FlowRate.append(RatioVCOrifice * area_circle(Diam) 
                * np.sqrt(2 * gravity.magnitude * Height[i]))
         else:
             FlowRate.append(0)
    return np.array(FlowRate)


@u.wraps(u.m**3/u.s, [u.m, u.m, None], False)
def flow_orifice_vert(Diam, Height, RatioVCOrifice):
    """Return the vertical flow rate of the orifice."""
    #Checking input validity
    if not 0 < RatioVCOrifice < 1:
        raise ValueError("RatioVCOrifice should be between 0 and 1.")
    Height = np.array(Height)
    Height.tolist()
    FlowRate = []
    for i in range(len(Height)):
        if Height[i] > -Diam / 2:
           flow_vert = scipy.integrate.quad(lambda z: (Diam 
           * np.sin(np.arccos(z/(Diam/2)))* np.sqrt(Height[i] - z)
           ), -Diam/2,min(Diam/2,Height[i]))
           FlowRate.append(RatioVCOrifice * np.sqrt(2 * gravity.magnitude) *flow_vert[0])
        else:
           FlowRate.append(0)
    return np.array(FlowRate)


@u.wraps(u.m, [u.m, None, u.m**3/u.s], False)
def head_orifice(Diam, RatioVCOrifice, FlowRate):
    """Return the head of the orifice."""
    #Checking input validity
    if not (FlowRate and Diam) > 0:
        raise ValueError("Flow rate and diameter must be greater than 0.")
    if not 0 < RatioVCOrifice < 1:
        raise ValueError("RatioVCOrifice should be between 0 and 1.")
    return ((FlowRate 
             / (RatioVCOrifice * area_circle(Diam))
             )**2 
            / (2*gravity.magnitude)
            )

 
@u.wraps(u.m**2, [u.m, None, u.m**3/u.s], False)
def area_orifice(Height, RatioVCOrifice, FlowRate):
    """Return the area of the orifice."""
    #Checking input validity
    if not (FlowRate and Height) > 0:
        raise ValueError("Height and flow rate must be greater than 0.")
    if not 0 < RatioVCOrifice < 1:
        raise ValueError("RatioVCOrifice should be between 0 and 1.")
        
    return FlowRate / (RatioVCOrifice * np.sqrt(2 * gravity.magnitude * Height))
    

@u.wraps(None, [u.m**3/u.s, None, u.m, u.m], False)
def num_orifices(FlowPlant, RatioVCOrifice, HeadLossOrifice, DiamOrifice):
    """Return the number of orifices."""
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    return np.ceil(area_orifice(HeadLossOrifice, RatioVCOrifice, 
                                 FlowPlant).magnitude
                    / area_circle(DiamOrifice)
                    )
 

@u.wraps(u.m, [None, u.m**3/u.s, u.m, u.m, None, None, u.m**2/u.s, u.m, None],
         False)
def diam_orifice_manifold(RatioFlowManifold, FlowTank, DiamPipe, Length, 
                          KMinorTotal, NumOrifices, Nu, PipeRough, 
                          RatioVCOrifice):
    """Return the diameter of the orifice in the manifold."""
    # Question: should RatioFlowManifold be constrained to between 0 and 1?
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if not (Length and NumOrifices) > 0:
        raise ValueError("Length and number of orifices must be greater than 0.")
    if KMinorTotal < 0:
        raise ValueError("Minor loss must not be negative.")
    if not 0 < RatioVCOrifice < 1:
        raise ValueError("RatioVCOrifice should be between 0 and 1.")
    return ((((1 - RatioFlowManifold)*DiamPipe) ** 4 
             / ((((KMinorTotal 
                   + (fric(FlowTank, DiamPipe, Nu, PipeRough) * Length/DiamPipe)
                   )
                  * (RatioFlowManifold)
                  ) 
                  - KMinorTotal 
                  - (fric(FlowTank,DiamPipe,Nu,PipeRough) 
                     * Length / DiamPipe
                     ) 
                  * RatioVCOrifice**2 
                  * NumOrifices**2
                  )
                )
             ) ** (1/4))
 
    
# Here we define functions that return the flow rate.
@u.wraps(u.m**3/u.s, [u.m, u.m**2/u.s], False)
def flow_transition(Diam, Nu):
    """Return the flow rate for the laminar/turbulent transition.
    
    This equation is used in some of the other equations for flow.
    """
    #Checking input validity
    if Diam <= 0:
        raise ValueError("Diameter must be greater than 0.")
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
    return np.pi * Diam * RE_TRANSITION_PIPE * Nu / 4


@u.wraps(u.m**3/u.s, [u.m, u.m, u.m, u.m**2/u.s], False)
def flow_hagen(Diam, HeadLossFric, Length, Nu):
    """Return the flow rate for laminar flow with only major losses."""
    #Checking input validity
    if not (Diam and Length) > 0:
        raise ValueError("Diameter and length must be greater than 0.")
    if HeadLossFric < 0:
        raise ValueError("Headloss due to friction must not be negative.")
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
    return (np.pi*Diam**4) / (128*Nu) * gravity.magnitude * HeadLossFric / Length


@u.wraps(u.m**3/u.s, [u.m, u.m, u.m, u.m**2/u.s, u.m], False)
def flow_swamee(Diam, HeadLossFric, Length, Nu, PipeRough):
    """Return the flow rate for turbulent flow with only major losses."""
    #Checking input validity
    if not (Diam and Length) > 0:
        raise ValueError("Diameter and length must be greater than 0.")
    if HeadLossFric < 0:
        raise ValueError("Headloss due to friction must not be negative.")
    if not 0 < (Nu and PipeRough) < 1:
        raise ValueError("Nu and pipe roughness should be between 0 and 1.")
        
    logterm = -np.log10(PipeRough / (3.7 * Diam) 
                        + 2.51 * Nu * np.sqrt(Length / (2 * gravity.magnitude
                                                          * HeadLossFric
                                                          * Diam**3)
                                              )
                        )
    return ((np.pi / np.sqrt(2)) * Diam**(5/2) 
            * np.sqrt(gravity.magnitude * HeadLossFric / Length) * logterm
            )


@u.wraps(u.m**3/u.s, [u.m, u.m, u.m, u.m**2/u.s, u.m], False)
def flow_pipemajor(Diam, HeadLossFric, Length, Nu, PipeRough):
    """Return the flow rate with only major losses.
    
    This function applies to both laminar and turbulent flows.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    FlowHagen = flow_hagen(Diam, HeadLossFric, Length, Nu).magnitude
    if FlowHagen < flow_transition(Diam, Nu).magnitude:
        return FlowHagen
    else:
        return flow_swamee(Diam, HeadLossFric, Length, Nu, PipeRough).magnitude


@u.wraps(u.m**3/u.s, [u.m, u.m, None], False)
def flow_pipeminor(Diam, HeadLossExpans, KMinor):
    """Return the flow rate with only minor losses.
    
    This function applies to both laminar and turbulent flows.
    """ 
    #Checking input validity - inputs not checked here are checked by
    #functions this function calls.
    if not (HeadLossExpans and KMinor) >= 0:
        raise ValueError("Headloss and minor loss must not be negative.")
    return (area_circle(Diam) * np.sqrt(2 * gravity.magnitude 
                                                  * HeadLossExpans 
                                                  / KMinor)
            )

# Now we put all of the flow equations together and calculate the flow in a 
# straight pipe that has both major and minor losses and might be either
# laminar or turbulent.
@u.wraps(u.m**3/u.s, [u.m, u.m, u.m, u.m**2/u.s, u.m, None], False)
def flow_pipe(Diam, HeadLoss, Length, Nu, PipeRough, KMinor):
    """Return the the flow in a straight pipe.
    
    This function works for both major and minor losses and 
    works whether the flow is laminar or turbulent.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    if KMinor == 0:
        FlowRate = flow_pipemajor(Diam, HeadLoss, Length, Nu, 
                                  PipeRough).magnitude
    else:
        FlowRatePrev = 0
        err = 1
        FlowRate = min(flow_pipemajor(Diam, HeadLoss, Length, 
                                      Nu, PipeRough).magnitude, 
                       flow_pipeminor(Diam, HeadLoss, KMinor).magnitude
                       )
        while err > 0.01:
            FlowRatePrev = FlowRate
            HLFricNew = (HeadLoss * headloss_fric(FlowRate, Diam, Length, 
                                                  Nu, PipeRough).magnitude 
                         / (headloss_fric(FlowRate, Diam, Length, 
                                          Nu, PipeRough).magnitude
                            + headloss_exp(FlowRate, Diam, KMinor).magnitude
                            )
                         )
            FlowRate = flow_pipemajor(Diam, HLFricNew, Length, 
                                      Nu, PipeRough).magnitude
            if FlowRate == 0:
                err = 0
            else:
                err = abs(FlowRate - FlowRatePrev) / (FlowRate + FlowRatePrev)
    return FlowRate	
 

@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s], False)
def diam_hagen(FlowRate, HeadLossFric, Length, Nu):
    #Checking input validity
    if not (FlowRate and Length) > 0:
        raise ValueError("Flow rate and length must be greater than 0.")
    if HeadLossFric < 0:
        raise ValueError("Headloss must not be negative.")
    if not 0 < Nu < 1:
        raise ValueError("Nu should be between 0 and 1.")
        
    return ((128 * Nu * FlowRate * Length) 
            / (gravity.magnitude * HeadLossFric * np.pi)
            ) ** (1/4)


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m], False)
def diam_swamee(FlowRate, HeadLossFric, Length, Nu, PipeRough):
    """Return the inner diameter of a pipe.
    
    The Swamee Jain equation is dimensionally correct and returns the 
    inner diameter of a pipe given the flow rate and the head loss due
    to shear on the pipe walls. The Swamee Jain equation does NOT take 
    minor losses into account. This equation ONLY applies to turbulent 
    flow.
    """
    #Checking input validity
    if not (FlowRate and Length) > 0:
        raise ValueError("Flow rate and length must be greater than 0.")
    if HeadLossFric < 0:
        raise ValueError("Headloss must not be negative.")
    if not 0 < (Nu and PipeRough) < 1:
        raise ValueError("Nu and pipe roughness should be between 0 and 1.")
    a = ((PipeRough**1.25) 
         * ((Length * FlowRate**2) 
            / (gravity.magnitude * HeadLossFric)
            )**4.75
         )
    b = (Nu * (FlowRate**9.4) * (Length / (gravity.magnitude*HeadLossFric))**5.2)
    return 0.66 * (a+b)**0.04


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m], False)
def diam_pipemajor(FlowRate, HeadLossFric, Length, Nu, PipeRough):
    """Return the pipe IDiam that would result in given major losses.
    
    This function applies to both laminar and turbulent flow.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    DiamLaminar = diam_hagen(FlowRate, HeadLossFric, Length, Nu).magnitude
    if re_pipe(FlowRate, DiamLaminar, Nu) <= RE_TRANSITION_PIPE:
        return DiamLaminar
    else:
        return diam_swamee(FlowRate, HeadLossFric, Length, 
                           Nu, PipeRough).magnitude


@u.wraps(u.m, [u.m**3/u.s, u.m, None], False)
def diam_pipeminor(FlowRate, HeadLossExpans, KMinor):
    """Return the pipe ID that would result in the given minor losses.
    
    This function applies to both laminar and turbulent flow.
    """
    #Checking input validity
    if FlowRate <= 0:
        raise ValueError("Flow rate must be greater than 0.")
    if not (HeadLossExpans and KMinor) >= 0:
        raise ValueError("Headloss and minor loss must not be negative.")
    return ((np.sqrt(4 * FlowRate / np.pi)) 
            * (KMinor / (2 * gravity.magnitude * HeadLossExpans)) ** (1/4)
            )


@u.wraps(u.m, [u.m**3/u.s, u.m, u.m, u.m**2/u.s, u.m, None], False)
def diam_pipe(FlowRate, HeadLoss, Length, Nu, PipeRough, KMinor):
    """Return the pipe ID that would result in the given total head loss.
    
    This function applies to both laminar and turbulent flow and
    incorporates both minor and major losses.
    """
    #Inputs do not need to be checked here because they are checked by
    #functions this function calls.
    if KMinor == 0:
        Diam = diam_pipemajor(FlowRate, HeadLoss, Length, Nu, PipeRough).magnitude
    else:
        Diam = max(diam_pipemajor(FlowRate, HeadLoss, Length, Nu, PipeRough), diam_pipeminor(FlowRate, HeadLoss, KMinor)).magnitude
        err = 1.00
        while err > 0.001:
            DiamPrev = Diam
            HLFricNew = (HeadLoss * headloss_fric(FlowRate, Diam, Length, 
                                              Nu, PipeRough
                                              ).magnitude 
                     / (headloss_fric(FlowRate, Diam, Length, 
                                      Nu, PipeRough
                                      ).magnitude 
                                      + headloss_exp(FlowRate, 
                                                     Diam, KMinor
                                                     ).magnitude
                        )
                     )
            Diam = diam_pipemajor(FlowRate, HLFricNew, Length, Nu, PipeRough
                              ).magnitude
            err = abs(Diam - DiamPrev) / ((Diam+DiamPrev)/2)
    return Diam

# Weir head loss equations
@u.wraps(u.m, [u.m**3/u.m, u.m], False)
def width_rect_weir(FlowRate, Height):
    """Return the width of a rectangular weir."""
    #Checking input validity
    if not (FlowRate and Height) > 0:
        raise ValueError("Flow rate and height must be greater than 0.")
    return ((3 / 2) * FlowRate 
            / (RATIO_VC_ORIFICE * (np.sqrt(2*gravity.magnitude) * Height**(3/2)))
            )


# For a pipe, Width is the circumference of the pipe.
# Head loss for a weir is the difference in height between the water
# upstream of the weir and the top of the weir.
@u.wraps(u.m, [u.m**3/u.s, u.m], False)
def headloss_weir(FlowRate, Width):
    """Return the headloss of a weir."""
    #Checking input validity
    if not (FlowRate and Width) > 0:
        raise ValueError("Flow rate and width must be greater than 0.")
    return (((3/2) * FlowRate 
             / (RATIO_VC_ORIFICE * (np.sqrt(2*gravity.magnitude)*Width))
             ) ** 3)


@u.wraps(u.m, [u.m, u.m], False)
def flow_rect_weir(Height, Width):
    """Return the flow of a rectangular weir."""
    #Checking input validity
    if not (Height and Width) > 0:
        raise ValueError("Height and width must be greater than 0.")
    return ((2/3) * RATIO_VC_ORIFICE 
            * (np.sqrt(2*gravity.magnitude) * Height**(3/2)) 
            * Width)


@u.wraps(u.m, [u.m**3/u.s, u.m], False)
def height_water_critical(FlowRate, Width):
    """Return the critical local water depth."""
    #Checking input validity
    if not (FlowRate and Width) > 0:
        raise ValueError("Flow rate and width must be greater than 0.")
    return (FlowRate / (Width * gravity.magnitude)) ** (2/3)


@u.wraps(u.m/u.s, u.m, False)
def vel_horizontal(HeightWaterCritical):
    """Return the horizontal velocity."""
    #Checking input validity
    if HeightWaterCritical <= 0:
        raise ValueError("Critical height of water must be greater than 0.")
    return np.sqrt(gravity.magnitude * HeightWaterCritical)

K_KOZENY=5

@u.wraps(u.m, [u.m, u.m, u.m, u.m**2/u.s], False)
def headloss_kozeny(Length, Diam, Vel, PipeRough, Nu):
    """Return the Carmen Kozeny Sand Bed head loss."""
    #Checking input validity
    if not (Length and Diam and Vel) > 0:
        raise ValueError("Length, diameter, and velocity must be greater than 0.")
    if not 0 < (Nu and PipeRough) < 1:
        raise ValueError("Nu and pipe roughnesss should be between 0 and 1.")
        
    return (K_KOZENY * Length * Nu 
            / gravity.magnitude * (1-PipeRough) ** 2 
            / PipeRough**3 * 36 * Vel 
            / Diam ** 2)
