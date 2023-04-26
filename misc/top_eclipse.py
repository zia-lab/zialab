#!/usr/bin/env python3

import numpy as np

niko = [(25,7),       (30,330),   (35,1400),
        (40,2480),   (45,5000),  (50,7300),
        (55,10000), (60,15400), (65,20000),
        (70,25400), (75,30500), (80,34800),
        (85,41500), (90,46600), (95,51000),
        (100,53100)]
niko      = np.array(niko).astype(float)
niko[:,1] = niko[:,1]/np.max(niko[:,1])

def nikoncalibrator(current_intensity, current_knob, target_intensity):
    '''
    Given  a current intensity and the current position of the knob in the
    top  illuminator  for  the  Nikon  Eclipse  microscope.  This function
    returns  the  position  at which the knob should be set to achieve the
    target  intensity. If the target intensity is outside the range of the
    current estimated range of the knob, an error is raised.

    This is based on data taken by Gabby and David circa 2023.

    Caveat emptor, these are just estimates.

    Parameters
    ----------
    current_intensity : float
        The current intensity of the light source.
    current_knob : float
        The current position of the knob in the top illuminator.
    target_intensity : float
        The target intensity of the light source.
    Returns
    -------
    target_knob : int
        The position of the knob for the top illuminator  to  achieve  the
        target intensity.
    '''
    scaler = np.interp(current_knob, niko[:,0], niko[:,1])
    scaled_niko = niko
    scaled_niko[:,1] = current_intensity / scaler * scaled_niko[:,1]
    max_scaled = int(np.max(scaled_niko[:,1]))
    min_scaled = int(np.min(scaled_niko[:,1]))
    target_knob = int(np.interp(target_intensity, 
                                scaled_niko[:,1], 
                                scaled_niko[:,0]))
    assert target_intensity >= min_scaled, f"Target intensity is too low, minimum is about {min_scaled}. Consider decreasing the overall brightness by other means"
    assert target_intensity <= max_scaled, f"Target intensity is too high, maximum is about {max_scaled}. Consider increasing the overall brightness by other means."
    return target_knob