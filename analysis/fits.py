#!/usr/bin/env python3

import sympy as sp
import numpy as np
from scipy import spatial
from scipy.optimize import curve_fit

def lorentz_model(num_terms):
    '''
    The Lorentz lineshape.

    A * 2 / π / w / (1 + 4/w^2 * (x-d)^2)

    Parameters
    ----------
    num_terms (int)

    Returns
    -------
    fitfun (func): a function of (3*num_terms + 1) parameters, where
    the first one is taken as the independent variable and the other
    ones the model parameters organized as: 
    (all num_terms amplitudes, all center positions, all widths).
    '''
    x = sp.Symbol('x')
    thef = [(sp.Symbol('A_%d' % i) * 2 / sp.pi / sp.Symbol('w_%d' % i) 
            / (1 + 4 / sp.Symbol('w_%d' % i)**2 * (x-sp.Symbol('d_%d' % i))**2)) for i in range(num_terms)]
    Avars = tuple([sp.Symbol('A_%d' % i) for i in range(num_terms)])
    dvars = tuple([sp.Symbol('d_%d' % i) for i in range(num_terms)])
    wvars = tuple([sp.Symbol('w_%d' % i) for i in range(num_terms)])
    allvars = (x,) + Avars + dvars + wvars
    fitfun = np.sum(thef)
    fitfun = sp.lambdify(allvars, fitfun, 'numpy')
    return fitfun

def gaussian_model(num_terms):
    '''
    A classic for all ages.

    A / sqrt(2π) / w * exp(-(x-d)^2 / 2 / w^2)

    Parameters
    ----------
    num_terms (int)

    Returns
    -------
    fitfun (func): a function of (3*num_terms + 1) parameters, where
    the first one is taken as the independent variable and the other
    ones the model parameters organized as: 
    (all num_terms amplitudes, all center positions, all widths).   
    '''
    x = sp.Symbol('x')
    thef = [sp.Symbol('A_%d' % i) / sp.sqrt(2*sp.pi) / sp.Symbol('w_%d' % i) * sp.exp(-1/2/sp.Symbol('w_%d' % i)**2*(x-sp.Symbol('d_%d' % i))**2) for i in range(num_terms)]
    Avars = tuple([sp.Symbol('A_%d' % i) for i in range(num_terms)])
    dvars = tuple([sp.Symbol('d_%d' % i) for i in range(num_terms)])
    wvars = tuple([sp.Symbol('w_%d' % i) for i in range(num_terms)])
    allvars = (x,) + Avars + dvars + wvars
    fitfun = np.sum(thef)
    fitfun = sp.lambdify(allvars, fitfun, 'numpy')
    return fitfun

def pseudo_voigt_model(num_terms):
    '''
    An   approximation   to  the  convolution  of  Gaussian  and
    Lorentzian lineshapes.
    
    A * (η * L(x, γL)
        + (η-1) * G(x, γG))
    
    where
    L(x, γL) = 1 / π / γL / (1+(x-d)**2/γL**2)
    G(x, γL) = 1 / sqrt(π) / γG * exp( -(x-d)**2 / γG**2)

    Parameters
    ----------
    num_terms (int)

    Returns
    -------
    fitfun  (func):  a function of (4*num_terms + 1) parameters,
    where the first one is taken as the independent variable and
    the other ones the model parameters organized as:
    (all   num_terms   amplitudes,  all  center  positions,  all
    Gaussian widths, all Lorentzian widths).

    Reference
    ---------
    Ida,  Ando,  and Toraya, “Extended Pseudo-Voigt Function for
    Approximating the Voigt Profile.” 
    '''
    x = sp.Symbol('x')
    γG = sp.Symbol('γG')
    γL = sp.Symbol('γL')
    γT = (γG**5 + 2.69269 * γG**4 * γL + 2.42843 * γG**3 * γL**2 
         + 4.47163 * γG**2 * γL**3 + 0.074842 * γG * γL**4 + γL**5)**(1/5)
    proto_η = 1.36603 * γL / γT - 0.47719 * (γL / γT)**2 + 0.11116 * (γL / γT)**3

    Avars = tuple([sp.Symbol('A_%d' % i) for i in range(num_terms)])
    dvars = tuple([sp.Symbol('d_%d' % i) for i in range(num_terms)])
    γGvars = tuple([sp.Symbol('γG_%d' % i) for i in range(num_terms)])
    γLvars = tuple([sp.Symbol('γL_%d' % i) for i in range(num_terms)])
    allvars = (x,) + Avars + dvars + γGvars + γLvars

    def single_term(i):
        A = sp.Symbol('A_%d' % i)
        η = proto_η.subs({γL: sp.Symbol('γL_%d' % i), γG: sp.Symbol('γG_%d' % i)})
        γLi = sp.Symbol('γL_%d' % i)
        γGi = sp.Symbol('γG_%d' % i)
        d = sp.Symbol('d_%d' % i )
        single_voigt = η*1/sp.pi/γLi/((x-d)**2/γLi**2+1) + (1-η)*1/γGi/sp.sqrt(sp.pi)*sp.exp(-(x-d)**2/γGi**2)
        single_voigt = A * single_voigt
        return single_voigt

    thefun = [single_term(i) for i in range(num_terms)]
    fitfun = np.sum(thefun)
    fitfun = sp.lambdify(allvars, fitfun, 'numpy')
    return fitfun

def spectrum_4param_fit(x, y, lineshape_fun, max_peaks,
    wiggle=10, maxfev=100000, de= 100, wiggle_jiggle=200, verbose=False):
    '''
    Given a three parameter (amplitude, center, width) lineshape function this function
    fits the given data (x,y) for superpositions of several (up to max_peaks) of these
    lineshapes.

    Fitting progresses by the solver adding one term at a time, seeding the solver with
    a starting center position at the largest discrepancy in y - fity.

    Parameters
    ----------
    x (array-like 1-D): 
    y (array-like 1-D): 
    lineshape_fun (function): a function that receives one parameter (how many terms) and which returns
    a function of (1 + 3*num_term) parameters, the first one being the independent variable.
    wiggle (float): starting width of a lineshape.
    maxfev (int):   how many function evaluations are fed into curve_fit.
    de (float): limits the upper and lower bound on the center positions.
    wiggle_jiggle (float): upper bound for the widths of the fitted line-shapes.
    verbose (bool): whether to print information as the fitting proceeds.

    Returns
    -------
    fit_history (np.array): a list of fitted parameters as the fitting increases the number of terms.
    cosine_sims (np.array): cosine similarity between y and the fitted y as the fitting increases the number of terms.
    rms_errors  (np.array): RMS errors 
    
    '''
    fit_params = []
    fity = np.zeros(y.shape)
    residual = y - fity
    cosine_sims = []
    rms_errors = []
    fit_history = []
    for num_peaks in range(1,max_peaks+1):
        start_amplitudes = fit_params[:(num_peaks-1)] + [np.max(residual)]
        start_positions = fit_params[(num_peaks-1):2*(num_peaks-1)] + [x[np.argmax(residual)]]
        start_widthsG = fit_params[2*(num_peaks-1):3*(num_peaks-1)] + [wiggle]
        start_widthsL = fit_params[3*(num_peaks-1):] + [wiggle]
        start_params = start_amplitudes + start_positions + start_widthsG + start_widthsL

        lower_bounds = [0]*len(start_amplitudes) + [s - de for s in start_positions] + [0 for _ in start_widthsG] + [0 for _ in start_widthsL]
        upper_bounds = [np.inf]*len(start_amplitudes) + [s + de for s in start_positions] + [wiggle_jiggle for _ in start_widthsG] + [wiggle_jiggle for _ in start_widthsL]
        bounds = (lower_bounds, upper_bounds)

        fitfun = lineshape_fun(num_peaks)
        fparams, fcov = curve_fit(fitfun, x, y, start_params, maxfev=maxfev, bounds=bounds)
        fit_params = list(fparams)
        fit_history.append(fit_params)

        fity = fitfun(x, *fparams)
        cosine_sim = 1 - spatial.distance.cosine(y, fity)
        cosine_sims.append(cosine_sim)
        rms_errors.append(np.sqrt(sum(np.abs(y-fity)**2)/len(y)))
        
        if verbose:
            print("#"*10)
            print(num_peaks, cosine_sim)
        residual = y - fity
    cosine_sims = np.array(cosine_sims)
    rms_errors = np.array(rms_errors)
    return fit_history, cosine_sims, rms_errors

def spectrum_3param_fit(x, y, lineshape_fun, max_peaks, 
    wiggle=10, maxfev=100000, de= 100, wiggle_jiggle=200, verbose=False):
    '''
    Given  a  four parameter (amplitude, center, width1, width2) lineshape
    function this function fits the given data (x,y) for superpositions of
    several (up to max_peaks) of these lineshapes.

    Fitting  progresses  by  the solver adding one term at a time, seeding
    the  solver with a starting center position at the largest discrepancy
    in y - fity.

    Parameters
    ----------
    x (array-like 1-D): 
    y (array-like 1-D): 
    lineshape_fun  (function): a function that receives one parameter (how
    many  terms)  and  which  returns  a  function  of  (1  +  3*num_term)
    parameters,  the  first  one  being  the  independent variable. wiggle
    (float): starting width of a lineshape.
    maxfev (int):   how many function evaluations are fed into curve_fit.
    de (float): limits the upper and lower bound on the center positions.
    wiggle_jiggle  (float): upper bound for the widths of the fitted line-
    shapes.  verbose  (bool):  whether to print information as the fitting
    proceeds.

    Returns
    -------
    fit_history  (np.array):  a  list  of fitted parameters as the fitting
    increases the number of terms.
    cosine_sims  (np.array):  cosine similarity between y and the fitted y
    as the fitting increases the number of terms.
    rms_errors  (np.array): RMS errors 
    
    '''
    fit_params = []
    fity = np.zeros(y.shape)
    residual = y - fity
    cosine_sims = []
    rms_errors = []
    fit_history = []
    for num_peaks in range(1,max_peaks+1):
        start_amplitudes = fit_params[:(num_peaks-1)] + [np.max(residual)]
        start_positions = fit_params[(num_peaks-1):2*(num_peaks-1)] + [x[np.argmax(residual)]]
        start_widths = fit_params[2*(num_peaks-1):] + [wiggle]
        start_params = start_amplitudes + start_positions + start_widths

        lower_bounds = [0]*len(start_amplitudes) + [s - de for s in start_positions] + [0 for _ in start_widths]
        upper_bounds = [np.inf]*len(start_amplitudes) + [s + de for s in start_positions] + [wiggle_jiggle for _ in start_widths]
        bounds = (lower_bounds, upper_bounds)

        fitfun = lineshape_fun(num_peaks)
        fparams, fcov = curve_fit(fitfun, x, y, start_params, maxfev=maxfev, bounds=bounds)
        fit_params = list(fparams)
        fit_history.append(fit_params)

        fity = fitfun(x, *fparams)
        cosine_sim = 1 - spatial.distance.cosine(y, fity)
        cosine_sims.append(cosine_sim)
        rms_errors.append(np.sqrt(sum(np.abs(y-fity)**2)/len(y)))
        
        if verbose:
            print("#"*10)
            print(num_peaks, cosine_sim)
        residual = y - fity
    cosine_sims = np.array(cosine_sims)
    rms_errors = np.array(rms_errors)
    return fit_history, cosine_sims, rms_errors