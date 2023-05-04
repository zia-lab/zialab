#                                                                            
#   ┌───────────────────────────────────────────────────────────────────────┐
#   │***********************************************************************│
#   │************@&&&&&@&@@&&@&&&@&&@&&@@&&@&&&&&%&&&&@&&/#(((#&************│
#   │***********@&&&&&@&&&&&@&&&&&&&&@&@&@&@@&&&&&&&&@&&&%/(/(%&&***********│
#   │***********@&&&&&@&@&&&@&&&@&&@&&&&@&&@&@&@&@&&@@&&%%**#&&&&***********│
#   │***********&&@&&&&@&@@&@&&&&@@&&&&@@&&@&&%&@@&&@&@&%%/%&&&&&***********│
#   │***********@&&&&&@&┌─────────────────────────────────┐%&&&&@***********│
#   │***********&&&&&&@&│           Generalized           │%&&&&@***********│
#   │************@&&&&&@│         Metalenses with         │@&&&@************│
#   │***********@&&&&&&&│           S4 and MEEP           │#@&&@@***********│
#   │***********&&&@&&&&│   --- Juan David Lizarazo ---   │#@@@&@***********│
#   │***********@&&@&&&&│           Mar 31 2020           │#@&&&&***********│
#   │***********@&&@&&&&│            version 3            │(&&&&@***********│
#   │************@&@&&&&└─────────────────────────────────┘&&&@@************│
#   │***********&&&&&@&&&&&&&&%&&&&&&&&&&%%##%##%#%####%(#%#%&&&@***********│
#   │***********@&@&&@&@&&&&&&&&&&&&&&&%#%##%#%%%%##%%#%##%#%&&&&***********│
#   │***********@&&&&@&&@&&&&&&&&&&&&%%%%%%%#%%#%%%%%&%%#%###&&&@***********│
#   │***********@&&&&@&&@&&&&&&%&%&&%#%#%%##%%%%%%#%%%%%#%%##&&&@***********│
#   │***********@&&&&&&&&&@&&&&&&%%%%%#%%#%%%%%%%#%%#%%%#%%##&%&&***********│
#   │***********&&@&&&@&&%@&&&&&%#%%%%%%#%%%%%%%%&%&%%&%#%%%%%%&@***********│
#   │*************@&&&&&&&&&&&&%%%%%%#%&%#%%%%%&%%%%&%%%%%#%%&@*************│
#   │*************&&&&&&&&&&&&%%%%%%#&%#%%%%%%&%#%#%%#%%%%#%%&@*************│
#   │*************@&&&@%&&&&%%&%%%%%%%%%%%%%%%#%&%%%&%%%%%%%%&@*************│
#   │************&@&&@@%%%%%%%#%%%%%%%%%%%%%%%%&%&&%%%%%%%%%%&%@************│
#   │************&@&&&&%&%%%%%%#%%%%%%%&%&&%%%%%%%%&%%%%%%%%%%%@************│
#   │************&&&&%%&%%%%%#%%%%%%%%%&%&%%%%%%%&&%&%%%%%%%%&%@************│
#   │***********&&%%%%%&&%%%%%%%%&%%%%%&&%%%%&&&&%%&%%%%%%%%%%&%&***********│
#   │***********%&%&%&%&&&&&&&&&&&&&&&&&%&%%%&&%%%&%&%&&%%%%&&%&%***********│
#   │***********************************************************************│
#   └───────────────────────────────────────────────────────────────────────┘
#             ┌───────────────────────────────────────────────────┐          
#             │   S4 scripts are run by creating lua scripts and  │          
#             │ running them in terminal using the lua executable │          
#             │ for S4. MEEP can be easily installed on a mac by  │          
#             │         using the conda package manager.          │          
#             └───────────────────────────────────────────────────┘          
#             ┌───────────────────────────────────────────────────┐          
#             │  With the help of RCWA simulations run with S4,   │          
#             │   metasurfaces are designed to image points to    │          
#             │  surfaces, and their performance is estimated by  │          
#             │        running FDTD simulations with MEEP.        │          
#             └───────────────────────────────────────────────────┘          

# This variant is used to simulate 2D metalenses with a significantly
# reduced simulation volume given that here an extended source is used
# closer to the metalens that emulates the emission from a point source.
# In addition to the previous version, now the simulation volume is also
# reduced by querying the field right after the metalens and propagating
# this to the far-field.
# It also offers a tool to run a given metalens using several CPU cores
# in parallel.

import numpy as np
import os
import subprocess
import sys
import uuid
import meep as mp
import time
import datetime
import pickle
from textwrap import dedent
from tabulate import tabulate
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap, Normalize

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# setup directories

home_folder = os.path.expanduser('~')
s4dir = os.path.join(home_folder,'Google Drive/Zia Lab/CEM/S4')
s4dir = '/Users/juan/ZiaLab/CEM/S4'

##### log dirs #####
if sys.platform == 'win32':
    sys.path.insert(0,'%s:/Google Drive/Zia Lab/Python/' % drive_letter)
    logdir='%s:/Google Drive/Zia Lab/Log/' % drive_letter
if sys.platform == 'darwin':
    sys.path.insert(0,'/Users/juan/Google Drive/Zia Lab/Python/')
    logdir='/Users/juan/Google Drive/Zia Lab/Log/'
datadir = logdir + 'Data/'
graphdir = logdir + 'Graph/'
##### log dirs #####

###############################################################
################# Convenient Optics functions #################

def focal_length(na, aperture):
    '''
    Given NA and aperture, determine the focal length.
    '''
    return aperture/2 * np.sqrt(1/na**2-1)

def imaging_phase_profile(H, d, w, R, x, wavelength, n, eta, **kwargs):
    '''
    Given the depth H of a point emitter, 
    the distance d from the metalens surface to the detector plane,
    the radius of the detector,
    and the radius R of the metalens,
    compute the phase required at a position x in the plane
    of the metasurface. 
    '''
    return ((2 * np.pi / wavelength) * n * (H - np.sqrt(x**2 + H**2)) -
     (2 * np.pi / wavelength) * (d - np.sqrt(eta**2 * x**2 + d**2)) / eta)

################# Convenient Optics functions #################
###############################################################

###############################################################
################### Convenient S4 functions ###################

def expand_sim_params(sim_params):
    '''
    Compute additional parameters for the S4 simulations.
    '''
    sim_params['field_height'] = sim_params['post_height']
    sim_params['half_cell_width'] = sim_params['cell_width'] / 2.
    sim_params['half_post_width'] = sim_params['post_width'] / 2.
    sim_params['excitation_frequency'] = 1. / sim_params['wavelength']
    
    return sim_params

def post_phase(sim_params):
    '''
    Given the S4-simulation parameters, returns the electric field
    array(Exr, Eyr, Ezr, Exi, Eyi, Ezi) at (x_coord, y_coord, field_height)
    by executing an S4 lua script.
    '''

    lua = '''
    S = S4.NewSimulation()
    -- specifying all lengths in microns.
    S:SetLattice({{{cell_width},0}}, {{0,{cell_width}}})
    S:SetNumG({num_G})

    S:AddMaterial('vacuum', {{1,0}})
    S:AddMaterial('substrate', {{{epsilon}, 0}})


    S:AddLayer(
        'bottom',    -- name
        0,           -- thickness
        'vacuum') -- background material (semi-infinite)

    S:AddLayer(
       'forest',       -- name of the layer
       {post_height}, -- height of the layer
       'vacuum')       -- material of the layer

    S:AddLayer(
        'top',    -- new layer name
        0,        -- thickness
        'substrate') -- background material (semi-infinite)


    S:SetLayerPatternRectangle(
        'forest', -- layer to pattern
        'substrate',  -- material of the posts
        {{0,0}},  -- center of rectangle
        0, -- angle
        {{{half_post_width},{half_cell_width}}}) -- halfwidths

    S:SetExcitationPlanewave(
        {{0,0}},  -- incidence angles (sph coords: phi [0,180], theta [0,360])
        {{{s_amp},0}},  -- s-polarization amplitude and phase (in degrees)
        {{{p_amp},0}})  -- p-polarization amplitude and phase

    S:SetFrequency({excitation_frequency})

    print(S:GetEField({{{x_coord},{y_coord},{field_height}}}))
        '''.format(**sim_params)
    script_loc = (s4dir+'luascript-%s.lua') % str(uuid.uuid4())
    s4command = '"'+s4dir+'/S4-1.1.1-osx" "%s"' % (script_loc)
    lua_file = open(script_loc,'w')
    lua_file.write(lua)
    lua_file.close()
    result = subprocess.check_output(s4command,shell=True)
    os.system('rm "%s"' % script_loc)
    return np.array([float(x) for x in result.decode().split('\t')])

def post_transmission(sim_params):
    '''
    Given the S4-simulation parameters, returns the electric field
    array(Exr, Eyr, Ezr, Exi, Eyi, Ezi) at (x_coord, y_coord, field_height)
    by executing an S4 lua script.
    '''

    lua = '''
    S = S4.NewSimulation()
    -- specifying all lengths in microns.
    S:SetLattice({{{cell_width},0}}, {{0,{cell_width}}})
    S:SetNumG({num_G})

    S:AddMaterial('vacuum', {{1,0}})
    S:AddMaterial('substrate', {{{epsilon}, 0}})

    S:AddLayer(
        'bottom',    -- name
        0,           -- thickness
        'vacuum') -- background material (semi-infinite)

    S:AddLayer(
       'forest',       -- name of the layer
       {post_height}, -- height of the layer
       'vacuum')       -- material of the layer

    S:AddLayer(
        'top',    -- new layer name
        0,        -- thickness
        'substrate') -- background material (semi-infinite)

    S:SetLayerPatternRectangle(
        'forest', -- layer to pattern
        'substrate',  -- material of the posts
        {{0,0}},  -- center of rectangle
        0, -- angle
        {{{half_post_width},{half_cell_width}}}) -- halfwidths

    S:SetExcitationPlanewave(
        {{0,0}}, -- incidence angles (sph coords: phi [0,180], theta [0,360])
        {{{s_amp},0}},  -- s-polarization amplitude and phase (in degrees)
        {{{p_amp},0}})  -- p-polarization amplitude and phase

    S:SetFrequency({excitation_frequency})

    print(S:GetPowerFlux('top'))
        '''.format(**sim_params)
    script_loc = (s4dir+'luascript-%s.lua') % str(uuid.uuid4())
    s4command = '"'+s4dir+'/S4-1.1.1-osx" "%s"' % (script_loc)
    lua_file = open(script_loc,'w')
    lua_file.write(lua)
    lua_file.close()
    result = subprocess.check_output(s4command,shell=True)
    os.system('rm "%s"' % script_loc)
    return np.array([float(x) for x in result.decode().split('\t')])

################### Convenient S4 functions ###################
###############################################################

###############################################################
######################### MISC funtions #######################

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    # https://goshippo.com/blog/measure-real-size-any-python-object/
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def function_topper(x,y):
    '''
    This function flattens out a set of points {x,y(x)}
    so that their interpolation would be a one-to-one function.
    x is assumed to be monotonically increasing.
    '''
    clean_x = []
    clean_y = []
    # first determine if the top function will be increasing or decreasing
    if y[1] > y[0]:
        sign = 1
    elif y[1] < y[0]:
        sign = -1
    else:
        print('undetermined sign')
    yp_current = y[0]
    clean_x = [x[0]]
    clean_y = [y[0]]
    for index in range(len(x)-1):
        xp = x[index]
        yp = y[index]
        next_xp = x[index+1]
        next_yp = y[index+1]
        if sign == 1:
            if (next_yp > yp) and next_yp > max(clean_y):
                clean_x.append(xp)
                clean_y.append(yp)
        if sign == -1:
            if (next_yp < yp) and next_yp < min(clean_y):
                clean_x.append(xp)
                clean_y.append(yp)
    return np.array(clean_x), np.array(clean_y)

######################### MISC funtions #######################
###############################################################

###############################################################
######################## MEEP functions #######################

def aux_params(metalens):
    '''
    Compute additional parameters.
    '''
    if metalens['w'] == metalens['R']:
      metalens['w'] = metalens['w'] + 1e-3
    metalens['aperture'] = 2*metalens['R']
    metalens['num of unit cells'] = int(metalens['aperture'] 
                                       / metalens['unit cell size'])
    if metalens['num of unit cells'] % 2:
        pass
    else:
        metalens['num of unit cells'] += -1
    metalens['ws'] = metalens['R']
    metalens['fcen'] = 1./metalens['wavelength']
    metalens['n'] = np.sqrt(metalens['epsilon'])
    metalens['normal_incidence_transmission'] = (1-((1-metalens['n'])/(1+metalens['n']))**2)
    metalens['TIR_onset_coordinate'] = (np.tan(np.arcsin(1/metalens['n']))
                                        * metalens['H'])
    metalens['wavelength_rgb'] = wave_to_rgb(metalens['wavelength'])
    metalens['beta'] = 2*np.arctan(metalens['R']/metalens['H'])
    metalens['k'] = metalens['n']*2.*np.pi/metalens['wavelength'] # inside dia
    metalens['cmap'] = ListedColormap(np.array([
                [i/255*metalens['wavelength_rgb'][0],
                i/255*metalens['wavelength_rgb'][1],
                i/255*metalens['wavelength_rgb'][2],
                1] for i in range(256)]))
    metalens['k_0'] = 2.*np.pi/metalens['wavelength'] # in air
    metalens['eta'] = metalens['w']/metalens['R'] - 1
    metalens['NA_c'] = (metalens['n'] * metalens['R'] 
                        / np.sqrt(metalens['R']**2+metalens['H']**2))
    metalens['source_width'] = 2./metalens['fcen']
    metalens['cell_width'] =  metalens['simulation_parameters']['cell_width']
    metalens['top_plus'] = metalens['d']*0.1
    
    # determine size of simulation area
    metalens['sim_cell_width'] = (2*max(metalens['R'],metalens['w'])
                                  + 2*metalens['pml_width']
                                  + 2*metalens['gap_h'])
    if metalens['w'] >= metalens['R']:
        metalens['sim_cell_width']+= 2*metalens['gap_h']
    metalens['sim_cell_height'] = (metalens['s']
         + 2 * metalens['pml_width'] + metalens['post_height']
         + metalens['b'] + 2 * metalens['gap_v'])
    
    # determine locations of different features
    metalens['source_coordinate'] = (-metalens['sim_cell_height']/2.
                    + metalens['pml_width'] + metalens['gap_v'])
    metalens['interface_coordinate'] = (-metalens['sim_cell_height']/2.
                                        + metalens['pml_width']
                                        + metalens['s']
                                        + metalens['gap_v'])
    metalens['top_of_posts_coordinate'] = (metalens['interface_coordinate']
                                          + metalens['post_height'])
    metalens['detector_plane_coordinate'] = (metalens['interface_coordinate']
                                             + metalens['d'])
    
    metalens['simulation_time'] = (metalens['source_width']
                                   + (metalens['n'] 
                                      * metalens['s']
                                      / metalens['wavelength'])
                                   + ((np.sqrt(metalens['b']**2
                                       + metalens['R']**2)) 
                                     / metalens['wavelength']))
    
    metalens['extent'] = [-metalens['sim_cell_width']/2,
                          metalens['sim_cell_width']/2,
                          -metalens['sim_cell_height']/2,
                          metalens['sim_cell_height']/2]
    metalens['full_extent'] = [-metalens['sim_cell_width']/2,
                          metalens['sim_cell_width']/2,
                          -metalens['sim_cell_height']/2,
                          (metalens['detector_plane_coordinate']
                          + metalens['top_plus'])]
    metalens['nearfield_coordinate'] = (metalens['interface_coordinate']
                                        + metalens['post_height']
                                        + metalens['b'])
    return metalens


def make_metalens_geometry(metalens):
    '''
    Given metalens parameters, determine the required phases, and using
    these and the known width to phase relationship, determine the
    required widths for the posts.
    '''
    # first design the mask based on the given widths and corresponding phases
    widths = metalens['widths']
    phases = metalens['phases']
    wavelength = metalens['wavelength']
    good_widths = (widths >= metalens['min_width'])
    widths = widths[good_widths]
    phases = phases[good_widths]
    aperture = 2*metalens['R']
    # compute the required phases based on the wavelength, 
    # focal length and number of unit cells
    if (max(phases)-min(phases)) < 2*np.pi:
        print((max(phases)-min(phases)))
        print("not a full phase coverage")
        return "not a full phase coverage"
    x, y = function_topper(widths, phases)
    axis_positions = np.linspace((-metalens['unit cell size']*
                              (metalens['num of unit cells']-1)/2),
                              (metalens['unit cell size']*
                              (metalens['num of unit cells']-1)/2),
                              metalens['num of unit cells'])
    required_phases = np.array([imaging_phase_profile(**metalens, x=xs) 
                                for xs in axis_positions])
    required_phases = required_phases - min(required_phases)
    required_phases = required_phases % (2*np.pi)
    required_widths = np.interp(required_phases, y, x)
    # create the posts
    the_posts = [mp.Block(size=mp.Vector3(w, metalens['post_height']),
                  center = mp.Vector3(position,
                                      (metalens['interface_coordinate']
                                       + metalens['post_height']/2)
                                     ),
                  material = mp.Medium(epsilon = metalens['epsilon'])) 
                for w, position in zip(required_widths, axis_positions)]
    # create the substrate
    metalens['substrate_height'] = (metalens['pml_width']
                                    + metalens['gap_v']
                                    + metalens['s'])
    substrate = [mp.Block(size = mp.Vector3(metalens['sim_cell_width'],
                                            metalens['substrate_height']),
                        center = mp.Vector3(0,
                              (-metalens['sim_cell_height']/2
                              + metalens['substrate_height']/2)),
                        material = mp.Medium(epsilon = metalens['epsilon']))]
    flux_substrate = [mp.Block(size = mp.Vector3(metalens['sim_cell_width'],
                                            metalens['sim_cell_height']),
                        center = mp.Vector3(0,0),
                        material = mp.Medium(epsilon = metalens['epsilon']))]
    metalens['required_phases'] = required_phases
    metalens['required_widths'] = required_widths
    metalens['axis_positions'] = axis_positions
    metalens['geometry'] = substrate + the_posts
    metalens['flux_geometry'] = flux_substrate
    # compute the contour of the metalens
    track = [[-metalens['R'], metalens['interface_coordinate']]]
    post_h = metalens['post_height']
    for ax_position, pwidth in zip(metalens['axis_positions'],
                                  metalens['required_widths']):
        this_post = [
          [ax_position-pwidth/2, metalens['interface_coordinate']],
          [ax_position-pwidth/2, metalens['interface_coordinate'] + post_h],
          [ax_position+pwidth/2, metalens['interface_coordinate'] + post_h],
          [ax_position+pwidth/2, metalens['interface_coordinate']]
                    ]
        track.extend(this_post)
    track.append([metalens['R'], metalens['interface_coordinate']])
    track = np.array(track)
    metalens['contour'] = track
    return metalens

def plot_phase_profile(metalens):
    plt.rcParams.update({'font.size': 18})
    plt.figure(figsize=(13,3))
    plt.plot(metalens['axis_positions'],metalens['required_widths'])
    plt.plot(metalens['axis_positions'],metalens['required_widths'],
            'ko',ms=2)
    plt.xlabel('x/$\mu$m')
    plt.ylabel('post width / $\mu$m')
    plt.xlim(-metalens['R'],metalens['R'])
    plt.show()

def print_params(metalens):
    print_out_lines = []
    non_printable = [list, np.ndarray, dict]
    for k in metalens:
        thing = metalens[k]
        thing_type = type(thing)
        if thing_type in non_printable:
            continue
        if thing_type in [int, np.int64]:
            thing_parsed = "%d" % thing
        if thing_type == bool:
            thing_parsed = "%s" % thing
        if thing_type in [float, np.float64]:
            thing_parsed = "%.2f" % thing
        if thing_type == str:
            thing_parsed = thing
        print_out_lines.append([k, thing_parsed])
    print(tabulate(print_out_lines))

#def far_ez_source_amp_func(metalens):
#    '''
#    returns the required amplitude
#    function necessary to simulate
#    an isotropic point source
#    '''
#    def far_ez(mpvec):
#        '''
#        remember that the vectors
#        that MEEP will provide here
#        are relative to the center of the source
#        '''
#        r = np.sqrt(mpvec.x**2 + (metalens['H'] - metalens['s'])**2)
#        ph = np.exp(1j * metalens['k'] * r)
#        am = 1./(r)**1.5
#        return am * ph
#    return far_ez

def out_of_plane_dip_amp_func_Ez(metalens):
    '''
    returns the required amplitude
    function necessary to simulate
    an isotropic point source
    '''
    def far_JEz(mpvec):
        '''
        remember that the vectors
        that MEEP will provide here
        are relative to the center of the source
        '''
        x = mpvec.x
        H, k, n = (metalens['H'] - metalens['s']), metalens['k'], metalens['n']
        return -H*k*n*(2*k*np.sqrt(H**2 + x**2) + 1j)*np.exp(1j*k*np.sqrt(H**2 + x**2))/(2*(k*np.sqrt(H**2 + x**2))**(5/2))
    return far_JEz

def out_of_plane_dip_amp_func_Hx(metalens):
    '''
    returns the required amplitude
    function necessary to simulate
    an isotropic point source
    '''
    def far_JEz(mpvec):
        '''
        remember that the vectors
        that MEEP will provide here
        are relative to the center of the source
        '''
        x = mpvec.x
        H, k, n = (metalens['H'] - metalens['s']), metalens['k'], metalens['n']
        return -np.exp(1j*k*np.sqrt(H**2 + x**2))/np.sqrt(k*np.sqrt(H**2 + x**2))
    return far_JEz

def plot_em_energy_density(metalens, normFunc = Normalize, saver=False):
    vmin = np.percentile(metalens['rho_em'].flatten(),10)
    vmax = np.percentile(metalens['rho_em'].flatten(),10)
    plt.rcParams.update({'font.size': 32})
    fig, ax = plt.subplots(1,figsize=(20,18))
    ims = ax.imshow(metalens['rho_em']+0.001, extent=metalens['extent'],
              cmap = metalens['cmap'],
              origin='lower',
              norm=normFunc(vmin=vmin,
                            vmax=vmax))
    ax.set_xlabel('x/$\mu$m')
    ax.set_ylabel('ya/$\mu$m')
    ax.plot([-metalens['w'],metalens['w']],
            [metalens['d'],metalens['d']],
            'w--')
    fig.colorbar(ims,ax=ax,label='$|E|^2$')
    plt.tight_layout()
    if saver:
        fig.dpi = metalens['rho_em'].shape[0]/fig.get_size_inches()[1]
        plt.savefig(saver+'.pdf', transparent=True)
        plt.close()
    else:
      plt.show()

def plot_density(metalens, quantity, extra='',
                 norm_fun=Normalize, saver=False,
                 pmin=5, pmax=95):
    vmin = np.percentile(metalens[quantity].flatten(),pmin)
    vmax = np.percentile(metalens[quantity].flatten(),pmax)
    pretty_labels = {'rho_em': r'$\rho_{EM}$'}
    plt.rcParams.update({'font.size': 32})
    fig, ax = plt.subplots(1,figsize=(20,18))
    ims = ax.imshow(metalens[quantity],extent=metalens['full_extent'],
              cmap=metalens['cmap'],
              origin='lower',
              norm=norm_fun(vmin=vmin, vmax=vmax))
    ax.set_xlabel('x/$\mu$m')
    ax.set_ylabel('y/$\mu$m')
    ax.plot([-metalens['w'],metalens['w']],
            [(metalens['detector_plane_coordinate'])]*2,
            'wo')
    fig.colorbar(ims, ax=ax, label=pretty_labels[quantity])
    plt.tight_layout()
    exec(extra)
    if saver:
        fig.dpi = metalens['rho_em'].shape[0]/fig.get_size_inches()[1]
        plt.savefig(saver+'.pdf', transparent=True)
        plt.close()
    else:
        plt.show()

def plot_simulation_cell(metalens):
    plt.rcParams.update({'font.size': 18})
    fig, ax = plt.subplots(figsize=(10,10))
    # simulation area boundary
    ax.plot([-metalens['sim_cell_width']/2,
             metalens['sim_cell_width']/2,
             metalens['sim_cell_width']/2,
             -metalens['sim_cell_width']/2,
             -metalens['sim_cell_width']/2],
            [-metalens['sim_cell_height']/2,
             -metalens['sim_cell_height']/2,
             metalens['sim_cell_height']/2,
             metalens['sim_cell_height']/2,
             -metalens['sim_cell_height']/2],
            label='border')
    # pml wedge
    ax.plot([-metalens['sim_cell_width']/2 + metalens['pml_width'],
             metalens['sim_cell_width']/2 - metalens['pml_width'],
             metalens['sim_cell_width']/2 - metalens['pml_width'],
             -metalens['sim_cell_width']/2 + metalens['pml_width'],
             -metalens['sim_cell_width']/2 + metalens['pml_width']],
            [-metalens['sim_cell_height']/2 + metalens['pml_width'],
             -metalens['sim_cell_height']/2 + metalens['pml_width'],
             metalens['sim_cell_height']/2 - metalens['pml_width'],
             metalens['sim_cell_height']/2 - metalens['pml_width'],
             -metalens['sim_cell_height']/2 + metalens['pml_width']],
            label='pml')
    # interface
    ax.plot([-metalens['sim_cell_width']/2,
            metalens['sim_cell_width']/2],
            [(-metalens['sim_cell_height']/2 + metalens['pml_width']
            + metalens['gap_v'] + metalens['s'])]*2,
            '--', ms=2, label='interface')
    # near-field plane
    ax.plot([-metalens['sim_cell_width']/2,
            metalens['sim_cell_width']/2],
            [(metalens['sim_cell_height']/2
            - metalens['gap_v'] - metalens['pml_width'])]*2,
            label='near-field plane')
    # source
    ax.plot([-metalens['R'],
    metalens['R']],
    [metalens['source_coordinate']]*2,
    '--',ms=2, label='source')
    # metalens box
    ax.add_patch(plt.Rectangle((-metalens['R'],
            (metalens['interface_coordinate'])),
            2*metalens['R'],
            metalens['post_height'],
            alpha=0.1))
    # substrate
    ax.add_patch(plt.Rectangle((-metalens['sim_cell_width']/2,
            (-metalens['sim_cell_height']/2)),
            metalens['sim_cell_width'],
            metalens['s'] + metalens['gap_v'] + metalens['pml_width'],
            fc=(0,0,1,0.2),
            hatch='/'))
    ax.set_aspect('equal')
    plt.xlabel('x/$\mu$m')
    plt.ylabel('y/$\mu$m')
    plt.title('Simulation Cell')
    plt.legend()
    plt.show()

def simulate_metalens(metalens):
    # Setup the MEEP objects
    cell = mp.Vector3(metalens['sim_cell_width'], metalens['sim_cell_height'])
    # All around the simulation cell
    pml_layers = [ mp.PML(metalens['pml_width']) ]
    # Set up the sources
    sources = [mp.Source(src=mp.ContinuousSource(
                         wavelength=metalens['wavelength'],
                         width=metalens['source_width']
                        ),
              component=mp.Ez,
              center=mp.Vector3(0, metalens['source_coordinate']),
              size=mp.Vector3(2 * metalens['ws'], 0),
              amp_func=out_of_plane_dip_amp_func_Ez(metalens)),
              mp.Source(src=mp.ContinuousSource(
                        wavelength=metalens['wavelength'],
                        width=metalens['source_width']
                      ),
              component=mp.Hx,
              center=mp.Vector3(0, metalens['source_coordinate']),
              size=mp.Vector3(2 * metalens['ws'], 0),
              amp_func=out_of_plane_dip_amp_func_Hx(metalens))
              ]
    # Set up the symmetries
    syms = []
    if metalens['x_mirror_symmetry']:
        syms.append(mp.Mirror(mp.X))
    sim = mp.Simulation(cell_size=cell,
                boundary_layers=pml_layers,
                geometry=metalens['geometry'],
                force_complex_fields=metalens['complex_fields'],
                symmetries=syms,
                sources=sources,
                resolution=metalens['resolution'])
    start_time = time.time()
    metalens['run_date'] = (datetime.
                            datetime.
                            now().
                            strftime("%b %d %Y at %H:%M:%S"))
    mp.quiet(metalens['quiet'])
    sim.init_sim()
    
    # Branch if saving for making an animation
    if metalens['save_output']:
      sim.run(mp.to_appended("ez-{sim_id}".format(**metalens),
              mp.at_every(metalens['simulation_time']/1000.,
              mp.output_efield_z)),
              until=metalens['simulation_time'])
    else:
      sim.run(until=metalens['simulation_time']) 
    
    # Compute the clock run time and grab the fields
    metalens['array_metadata'] = sim.get_array_metadata()
    metalens['run_time_in_s'] = time.time() - start_time
    metalens['fields'] = {'Ez': sim.get_array(component=mp.Ez).transpose(),
                          'Hx': sim.get_array(component=mp.Hx).transpose(),
                          'Hy': sim.get_array(component=mp.Hy).transpose()
                          }
    metalens['eps'] = sim.get_epsilon().transpose()
    # Dump the result to disk
    if metalens['log_to_pkl'][0]:
        if metalens['log_to_pkl'][1] == '':
            pkl_fname = '%smetalens-%s.pkl' % (datadir, metalens['sim_id'])
        else:
            pkl_fname = metalens['log_to_pkl'][1]
        print(pkl_fname)
        pickle.dump(metalens, open(pkl_fname,'wb'))
    return metalens

def get_flux_on_metalens(metalens):
    # Setup the MEEP objects
    cell = mp.Vector3(metalens['sim_cell_width'], metalens['sim_cell_height'])
    # All around the simulation cell
    pml_layers = [ mp.PML(metalens['pml_width']) ]
    # Set up the sources
    sources = [mp.Source(src=mp.ContinuousSource(
                     wavelength=metalens['wavelength'],
                     width=metalens['source_width']
                    ),
          component=mp.Ez,
          center=mp.Vector3(0, metalens['source_coordinate']),
          size=mp.Vector3(2 * metalens['ws'], 0),
          amp_func=out_of_plane_dip_amp_func_Ez(metalens)),
          mp.Source(src=mp.ContinuousSource(
                    wavelength=metalens['wavelength'],
                    width=metalens['source_width']
                  ),
          component=mp.Hx,
          center=mp.Vector3(0, metalens['source_coordinate']),
          size=mp.Vector3(2 * metalens['ws'], 0),
          amp_func=out_of_plane_dip_amp_func_Hx(metalens))
          ]
    # Set up the symmetries
    syms = []
    if metalens['x_mirror_symmetry']:
        syms.append(mp.Mirror(mp.X))
    sim = mp.Simulation(cell_size=cell,
                boundary_layers=pml_layers,
                geometry=metalens['flux_geometry'],
                force_complex_fields=metalens['complex_fields'],
                symmetries=syms,
                sources=sources,
                resolution=metalens['resolution'])
    mp.quiet(metalens['quiet'])
    sim.init_sim()
    sim.run(until=metalens['simulation_time']) 

    fields = {'Ez': sim.get_array(component=mp.Ez).transpose(),
              'Hx': sim.get_array(component=mp.Hx).transpose(),
              'Hy': sim.get_array(component=mp.Hy).transpose()}
    transverse_axis = (
      np.linspace(-metalens['sim_cell_width']/2,
      metalens['sim_cell_width']/2,
      fields['Ez'].shape[1]))
    optical_axis = np.linspace(-metalens['sim_cell_height']/2,
                  metalens['sim_cell_height']/2,
                  fields['Ez'].shape[0])
    interface_index = np.argmin(np.abs(optical_axis-metalens['interface_coordinate']))
    Sy = (np.real(np.conjugate(fields['Ez'])
              * fields['Hx'])[interface_index])[np.abs(transverse_axis)<=metalens['R']]
    return np.sum(Sy)


def para_metalens(metalens, num_cores):
  '''
  Run script in the parallel environment for MEEP.
  '''
  print("See progress in terminal.")
  # save the params to disk
  pickle.dump(metalens, open('metalens_temp.pkl','wb'))
  # compose the script to be run
  script = '''
          main_dir = '/Users/juan/Google Drive/Zia Lab/CEM/MEEP'
          import meep as mp
          import numpy as np
          from matplotlib import pyplot as plt
          import os
          os.chdir(main_dir)
          home_folder = os.path.expanduser('~')

          import uuid
          import subprocess
          import pickle
          import time
          import sys
          sys.path.append(os.getcwd())
          import datetime
          if sys.platform == 'darwin':
            sys.path.append(os.path.join(home_folder,
                    'Google Drive/Zia Lab/Codebase/zialab'))
          else:
            print("Make amends for Windows or your other OS.")

          from cem.metalenses_3 import *

          metalens = pickle.load(open('metalens_temp.pkl','rb'))
          metalens = simulate_metalens(metalens)
          # metalens = compute_post_simulation_params(metalens)
          pickle.dump(metalens, open(os.path.join(main_dir,'out.pkl'), 'wb'))
          print('done')
  '''
  script_fname = 'parameep-hack-%s.py' % str(uuid.uuid4())
  # save the python script to the playground dir
  with open(script_fname,'w') as f:
    f.write(dedent(script))
  command_sequence = ''.join(['source activate parameep; ',
        'mpirun -n %d python %s' % (num_cores, script_fname)])
  os.system(command_sequence)
  out = pickle.load(open('out.pkl','rb'))
  os.system('mv out.pkl parametalens-%s.pkl' % metalens['sim_id'])
  return out

def compute_post_simulation_params(metalens, verbose=True):
    '''From the result of a simulation, compute the following quantities:
      - rho_em : electromagnetic energy density
      - S_x, S_y : the x,y components of the time averaged Poynting vector
      - max_axial_field_in_image_space: the y_coordinate of the maximum
        energy density along the optical axis
      - reached_det_plane: the ratio of the integrated S_y at the
        detector plane to the integrated S_y right after the metalens.
      - hit_the_target: the ratio of the integrated S_y at the
        within the bounds of the detector to the integrated S_y right
        after the metalens.
    '''
    metalens['optical_axis'] = np.linspace(-metalens['sim_cell_height']/2,
                                            metalens['sim_cell_height']/2,
                                            metalens['fields']['Ez'].shape[0])
    metalens['transverse_axis'] = np.linspace(-metalens['sim_cell_width']/2,
                                            metalens['sim_cell_width']/2,
                                            metalens['fields']['Ez'].shape[1])
    metalens['optical_axis_index'] = np.argmin(
                                          np.abs(metalens['transverse_axis']))
    metalens['top_of_post_index'] = np.argmin(np.abs(metalens['optical_axis']
                                    - metalens['top_of_posts_coordinate']))
    # far-field propagation
    metalens['nearfield_index'] = np.argmin(np.abs(metalens['optical_axis']
                                    - metalens['nearfield_coordinate']))
    metalens['lr_copies'] = int(round((metalens['freq_multiplier']-1)/2))

    metalens['farfields'] = {}
    metalens['nearfields'] = {}
    propagator = None
    for field in metalens['fields']:
        if verbose:
            print("Computing the farfield for %s..." % field)
        metalens['nearfields'][field] = metalens['fields'][field][metalens['nearfield_index']]
        zeropad = np.zeros(len(metalens['nearfields'][field])*metalens['lr_copies'])
        metalens['nearfields'][field] = np.concatenate((zeropad,metalens['nearfields'][field],zeropad))
        metalens['nearfield_fft'] = np.fft.fft(metalens['nearfields'][field])
        metalens['kx_frequencies'] = 2*np.pi*np.fft.fftfreq(
                                len(metalens['nearfields'][field]),
                                d=1./metalens['resolution'])
        metalens['ky'] = np.sqrt(metalens['k_0']**2-metalens['kx_frequencies']**2+0j)
        metalens['optical_axis_for_farfield'] = np.linspace(
                    metalens['nearfield_coordinate'],
                    metalens['detector_plane_coordinate'] + metalens['top_plus'],
                    int(round((metalens['detector_plane_coordinate'] + metalens['top_plus']
                    - metalens['nearfield_coordinate'])
                    * metalens['resolution']))) - metalens['nearfield_coordinate']
        metalens['optical_axis_for_farfield'] = (metalens['optical_axis_for_farfield'].reshape((len(metalens['optical_axis_for_farfield']),1)))
        if propagator is None:
            propagator = np.exp(1j*metalens['ky'] * metalens['optical_axis_for_farfield'])
        metalens['field_ft'] = (metalens['nearfield_fft'] * propagator)
        metalens['farfields'][field] = (np.fft.ifft(metalens['field_ft']))
        del metalens['field_ft']
        del metalens['nearfield_fft']
    del propagator
    metalens['fields']['rho_em'] = 0.5*np.abs(metalens['fields']['Ez'])**2 # not fully correct
    metalens['farfields']['rho_em'] = 0.5*np.abs(metalens['farfields']['Ez'])**2 # not fully correct
    for field in metalens['farfields']:
        if verbose:
            print("Patching the entire field for %s..." % field)
        nearFieldChunk = metalens['fields'][field][:metalens['nearfield_index']]
        zeropad2 = np.zeros((nearFieldChunk.shape[0],nearFieldChunk.shape[1]*metalens['lr_copies']))
        paddedfield = np.concatenate((zeropad2,nearFieldChunk,zeropad2),axis=1)
        metalens['farfields'][field] = np.concatenate(
          (paddedfield,
          metalens['farfields'][field]))
    
    metalens['farfields']['Sx'] = np.real(-np.conjugate(metalens['farfields']['Ez'])
                            * metalens['farfields']['Hy'])
    metalens['farfields']['Sy'] = np.real(np.conjugate(metalens['farfields']['Ez'])
                          * metalens['farfields']['Hx'])
    metalens['full_extent'][0] = (-metalens['sim_cell_width']
                                 * metalens['freq_multiplier']/2)
    metalens['full_extent'][1] = (metalens['sim_cell_width']
                                 * metalens['freq_multiplier']/2)
    metalens['transverse_axis_extended'] = np.linspace(
                                      metalens['full_extent'][0],
                                      metalens['full_extent'][1],
                                      metalens['farfields']['Ez'].shape[1])
    metalens['optical_axis_index'] = np.argmin(
                                      np.abs(metalens['transverse_axis_extended']))
    metalens['optical_axis_extended'] = np.linspace(metalens['full_extent'][2],
                                              metalens['full_extent'][3],
                                              metalens['farfields']['Ez'].shape[0])
    metalens['detector_plane_index'] = np.argmin(np.abs(metalens['optical_axis_extended']-
                                        metalens['detector_plane_coordinate']))
    metalens['flux_through_target'] = np.sum(
      metalens['farfields']['Sy'][metalens['detector_plane_index']][np.abs(metalens['transverse_axis_extended']) <=
              metalens['w']])
    metalens['full_flux'] = metalens['incident_flux']*np.pi/metalens['beta']
    if 'incident_flux' in metalens.keys():
        metalens['tf/if'] = (metalens['flux_through_target']
                             / metalens['incident_flux'])
        metalens['tf/ff'] = (metalens['flux_through_target']
                             / metalens['full_flux'])
    return metalens

def wave_to_rgb(wavelength, gamma=0.8):
    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    
    REF: https://www.noah.org/wiki/wave_to_rgb_in_Python
    '''

    wavelength = 1000*float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
      attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
      R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
      G = 0.0
      B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
      R = 0.0
      G = ((wavelength - 440) / (490 - 440)) ** gamma
      B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
      R = 0.0
      G = 1.0
      B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
      R = ((wavelength - 510) / (580 - 510)) ** gamma
      G = 1.0
      B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
      R = 1.0
      G = (-(wavelength - 645) / (645 - 580)) ** gamma
      B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
      attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
      R = (1.0 * attenuation) ** gamma
      G = 0.0
      B = 0.0
    else:
      R = 1.0
      G = 1.0
      B = 1.0
    return (R, G, B)



######################## MEEP functions #######################
###############################################################
