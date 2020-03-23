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
#   │***********@&&@&&&&│           Mar 20 2020           │#@&&&&***********│
#   │***********@&&@&&&&│                                 │(&&&&@***********│
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


import numpy as np
import os
import subprocess
import sys
import uuid
import meep as mp
import time
import datetime
import pickle
from tabulate import tabulate
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.colors import ListedColormap

# setup directories

home_folder = os.path.expanduser('~')
s4dir = os.path.join(home_folder,'Google Drive/Zia Lab/CEM/S4')

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
        {{0,0}},  -- incidence angles (spherical coordinates: phi in [0,180], theta in [0,360])
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
        {{0,0}},  -- incidence angles (spherical coordinates: phi in [0,180], theta in [0,360])
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

# def post_phase_ppol(sim_params):
#     '''
#     Given the simulation parameters, returns the electric field
#     array(Exr, Eyr, Ezr, Exi, Eyi, Ezi) at (x_coord, y_coord, field_height)
#     by executing an S4 lua script.
#     '''
#
#     lua = '''
#     S = S4.NewSimulation()
#     -- specifying all lengths in microns.
#     S:SetLattice({{{cell_width},0}}, {{0,{cell_width}}})
#     S:SetNumG({num_G})
#
#     S:AddMaterial('vacuum', {{1,0}})
#     S:AddMaterial('substrate', {{{epsilon}, 0}})
#
#
#     S:AddLayer(
#         'bottom',    -- name
#         0,           -- thickness
#         'substrate') -- background material (semi-infinite)
#
#     S:AddLayer(
#        'forest',       -- name of the layer
#        {post_height}, -- height of the layer
#        'vacuum')       -- material of the layer
#
#     S:AddLayer(
#         'top',    -- new layer name
#         0,        -- thickness
#         'vacuum') -- background material (semi-infinite)
#
#
#     S:SetLayerPatternRectangle(
#         'forest', -- layer to pattern
#         'substrate',  -- material of the posts
#         {{0,0}},  -- center of rectangle
#         0, -- angle
#         {{{half_post_width},{half_cell_width}}}) -- halfwidths
#
#     S:SetExcitationPlanewave(
#         {{0,0}},  -- incidence angles (spherical coordinates: phi in [0,180], theta in [0,360])
#         {{0,0}},  -- s-polarization amplitude and phase (in degrees)
#         {{1,0}})  -- p-polarization amplitude and phase
#
#     S:SetFrequency({excitation_frequency})
#
#     print(S:GetEField({{{x_coord},{y_coord},{field_height}}}))
#         '''.format(**sim_params)
#     script_loc = (s4dir+'luascript-%s.lua') % str(uuid.uuid4())
#     s4command = '"'+s4dir+'/S4-1.1.1-osx" "%s"' % (script_loc)
#     lua_file = open(script_loc,'w')
#     lua_file.write(lua)
#     lua_file.close()
#     result = subprocess.check_output(s4command,shell=True)
#     os.system('rm "%s"' % script_loc)
#     return np.array([float(x) for x in result.decode().split('\t')])
#
# def post_phase_spol(sim_params):
#
#     '''Given the simulation parameters,
#     returns the electric field array(Exr, Eyr, Ezr, Exi, Eyi, Ezi) at (x_coord, y_coord, field_height)'''
#
#     lua = '''
#     S = S4.NewSimulation()
#     -- specifying all lengths in microns.
#     S:SetLattice({{{cell_width},0}}, {{0,{cell_width}}})
#     S:SetNumG({num_G})
#
#     S:AddMaterial('vacuum', {{1,0}})
#     S:AddMaterial('substrate', {{{epsilon}, 0}})
#
#
#     S:AddLayer(
#         'bottom',    -- name
#         0,           -- thickness
#         'substrate') -- background material (semi-infinite)
#
#     S:AddLayer(
#        'forest',       -- name of the layer
#        {post_height}, -- height of the layer
#        'vacuum')       -- material of the layer
#
#     S:AddLayer(
#         'top',    -- new layer name
#         0,        -- thickness
#         'vacuum') -- background material (semi-infinite)
#
#
#     S:SetLayerPatternRectangle(
#         'forest', -- layer to pattern
#         'substrate',  -- material of the posts
#         {{0,0}},  -- center of rectangle
#         0, -- angle
#         {{{half_post_width},{half_cell_width}}}) -- halfwidths
#
#     S:SetExcitationPlanewave(
#         {{0,0}},  -- incidence angles (spherical coordinates: phi in [0,180], theta in [0,360])
#         {{1,0}},  -- s-polarization amplitude and phase (in degrees)
#         {{0,0}})  -- p-polarization amplitude and phase
#
#     S:SetFrequency({excitation_frequency})
#
#     print(S:GetEField({{{x_coord},{y_coord},{field_height}}}))
#         '''.format(**sim_params)
#     script_loc = (s4dir+'luascript-%s.lua') % str(uuid.uuid4())
#     s4command = '"'+s4dir+'/S4-1.1.1-osx" "%s"' % (script_loc)
#     lua_file = open(script_loc,'w')
#     lua_file.write(lua)
#     lua_file.close()
#     result = subprocess.check_output(s4command,shell=True)
#     os.system('rm "%s"' % script_loc)
#     return np.array([float(x) for x in result.decode().split('\t')])

################### Convenient S4 functions ###################
###############################################################

###############################################################
######################### MISC funtions #######################

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
        return "not a full phase coverage"
    x, y = function_topper(widths, phases)
    axis_positions = np.linspace((-metalens['unit cell size']*
                              (metalens['num of unit cells']-1)/2),
                              (metalens['unit cell size']*
                              (metalens['num of unit cells']-1)/2),
                              metalens['num of unit cells'])
    #required_phases = -2*np.pi/wavelength*(np.sqrt((axis_positions-metalens['axial_offset'])**2+f**2)-f)
    required_phases = np.array([imaging_phase_profile(**metalens, x=xs) for xs in axis_positions])
    required_phases = required_phases - min(required_phases)
    required_phases = required_phases % (2*np.pi)
    required_widths = np.interp(required_phases, y, x)
    # create the posts
    hairline = [mp.Block(size=mp.Vector3(w, metalens['post_height']),
                    center = mp.Vector3(position,(-metalens['sim_cell_height']/2
                                                  +metalens['H']
                                                  +metalens['gap']
                                                  +metalens['pml_width']
                                                  +metalens['post_height']/2)),
                    material = mp.Medium(epsilon = metalens['epsilon'])) for w, position in zip(required_widths, axis_positions)]
    # create the substrate
    substrate = [mp.Block(size = mp.Vector3(metalens['sim_cell_width'],
                                            metalens['H']),
                        center = mp.Vector3(0,
                              (-metalens['sim_cell_height']/2
                              +metalens['H']/2)
                              +metalens['gap']
                              +metalens['pml_width']),
                        material = mp.Medium(epsilon = metalens['epsilon']))]
    metalens['required_phases'] = required_phases
    metalens['required_widths'] = required_widths
    metalens['axis_positions'] = axis_positions
    metalens['geometry'] = substrate + hairline
    return metalens

def plot_phase_profile(metalens):
    plt.figure(figsize=(10,3))
    plt.plot(metalens['axis_positions'],metalens['required_widths'])
    plt.plot(metalens['axis_positions'],metalens['required_widths'],'ko')
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

def plot_em_energy_density(metalens):
    plt.rcParams.update({'font.size': 32})
    plt.figure(figsize=(20,18))
    plt.imshow(metalens['e2']+0.001,extent=metalens['extent'],
              cmap = metalens['cmap'],
              origin='lower',
              norm=LogNorm(vmin=0.001))
    plt.xlabel('x/$\mu$m')
    plt.ylabel('z/$\mu$m')
    plt.plot([-metalens['w'],metalens['w']],
            [metalens['d'],metalens['d']],
            'w--')
    plt.colorbar(label='$|E|^2$')
    plt.tight_layout()
    plt.show()

def plot_simulation_cell(metalens):
    fig, ax = plt.subplots(figsize=(10,10))
    ax.plot([-metalens['sim_cell_width']/2, metalens['sim_cell_width']/2,
              metalens['sim_cell_width']/2, -metalens['sim_cell_width']/2,
              -metalens['sim_cell_width']/2],
            [-metalens['sim_cell_height']/2, -metalens['sim_cell_height']/2,
            metalens['sim_cell_height']/2, metalens['sim_cell_height']/2,
            -metalens['sim_cell_height']/2],
            label='border')
    ax.plot([-metalens['sim_cell_width']/2+metalens['pml_width'],
              metalens['sim_cell_width']/2-metalens['pml_width'],
              metalens['sim_cell_width']/2-metalens['pml_width'],
              -metalens['sim_cell_width']/2+metalens['pml_width'],
              -metalens['sim_cell_width']/2+metalens['pml_width']],
            [-metalens['sim_cell_height']/2+metalens['pml_width'],
            -metalens['sim_cell_height']/2+metalens['pml_width'],
            metalens['sim_cell_height']/2-metalens['pml_width'],
            metalens['sim_cell_height']/2-metalens['pml_width'],
            -metalens['sim_cell_height']/2+metalens['pml_width']],
            label='pml')
    ax.plot([0],[(-metalens['sim_cell_height']/2
                +metalens['pml_width']
                  +metalens['gap'])],
            'o',ms=2)
    ax.plot([-metalens['sim_cell_width']/2,
            metalens['sim_cell_width']/2],
            [(-metalens['sim_cell_height']/2
                +metalens['pml_width']
                  +metalens['gap']
              +metalens['H'])]*2,
            '--',ms=2)
    ax.plot([-metalens['w'],
            metalens['w']],
            [(metalens['sim_cell_height']/2
            -metalens['gap']
            -metalens['pml_width'])]*2,
            label='target')
    ax.add_patch(plt.Rectangle((-metalens['R'],
            (-metalens['sim_cell_height']/2
                +metalens['pml_width']
                  +metalens['gap']
              +metalens['H'])),
            2*metalens['R'],
            metalens['post_height'],
                                alpha=0.1))
    ax.add_patch(plt.Rectangle((-metalens['R'],
            (-metalens['sim_cell_height']/2
                +metalens['pml_width']
                  +metalens['gap']
              +metalens['H'])),
            2*metalens['R'],
            metalens['post_height'],
                  fc=(0,0,1,0.2)))
    ax.add_patch(plt.Rectangle((-metalens['sim_cell_width']/2,
            (-metalens['sim_cell_height']/2)),
            metalens['sim_cell_width'],
            metalens['H']+metalens['gap']+metalens['pml_width'],
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
    cell = mp.Vector3(metalens['sim_cell_width'],
              metalens['sim_cell_height'])
    # All around the simulation cell
    pml_layers = [mp.PML(metalens['pml_width'])]

    # Let sources be continuous
    sources = [mp.Source(src=mp.ContinuousSource(wavelength=metalens['wavelength'],
                            width = metalens['source_width']),
              component=mp.Ez,
              center=mp.Vector3(0,metalens['source_coordinate']),
              size=mp.Vector3(0,0))]

    sim = mp.Simulation(cell_size=cell,
                boundary_layers=pml_layers,
                geometry=metalens['geometry'],
                force_complex_fields = metalens['complex_fields'],
                sources=sources,
                resolution=metalens['resolution'])
    start_time = time.time()
    metalens['run_date'] = datetime.datetime.now().strftime("%b %d %Y at %H:%M:%S")

    sim.init_sim()
    if metalens['save_output']:
      sim.run(mp.to_appended("ez-{sim_id}".format(**metalens),
                  mp.at_every(metalens['simulation time']/1000.,
                      mp.output_efield_z)),
            until=1*metalens['simulation time'])
    else:
      sim.run(until=1*metalens['simulation time']) 

    eps = sim.get_array(component=mp.Dielectric).transpose()
    ez = sim.get_array(component=mp.Ez).transpose()

    metalens['run_time_in_s'] = time.time() - start_time
    metalens['fields'] = {'Ez': ez}
    pickle.dump(metalens, open('%smetalens-%s.pkl' % (datadir, metalens['sim_id']),'wb'))
    return metalens

def compute_post_simulation_params(metalens):
    metalens['extent'] = [-metalens['sim_cell_width']/2,metalens['sim_cell_width']/2,
              -metalens['sim_cell_height']/2,metalens['sim_cell_height']/2]
    metalens['e2'] = 1/2* np.abs(metalens['fields']['Ez'])**2
    metalens['optical_axis'] = np.linspace(-metalens['sim_cell_height']/2,
                       metalens['sim_cell_height']/2,
                       metalens['fields']['Ez'].shape[0])
    metalens['transverse_axis'] = np.linspace(-metalens['sim_cell_width']/2,
                       metalens['sim_cell_width']/2,
                       metalens['fields']['Ez'].shape[1])
    metalens['detector_plane_index'] = np.argmin(np.abs(metalens['optical_axis']
                                                -metalens['d']))
    metalens['optical_axis_index'] = np.argmin(np.abs(metalens['transverse_axis']))
    metalens['top_of_post_index'] = np.argmin(np.abs(metalens['optical_axis']
                                        -metalens['top_of_posts_coordinate']))
    metalens['max_axial_field_in_image_space'] = np.argsort(-metalens['e2'][:,metalens['optical_axis_index']])
    metalens['max_axial_field_in_image_space'] = (metalens['max_axial_field_in_image_space'][metalens['max_axial_field_in_image_space']>metalens['top_of_post_index']])[0]
    return metalens

def wavelength_to_rgb(wavelength, gamma=0.8):
    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    
    REF: https://www.noah.org/wiki/Wavelength_to_RGB_in_Python
    '''

    wavelength = float(wavelength)
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

def aux_params(metalens):
    '''
    Compute a few additional parameters.
    '''
    metalens['aperture'] = 2*metalens['R']
    metalens['num of unit cells'] = int(metalens['aperture'] / metalens['unit cell size'])
    if metalens['num of unit cells'] % 2:
        pass
    else:
        metalens['num of unit cells'] += -1

    metalens['fcen'] = 1/metalens['wavelength']
    metalens['n'] = np.sqrt(metalens['epsilon'])
    metalens['wavelength_rgb'] = wavelength_to_rgb(metalens['wavelength']*1000)
    metalens['cmap'] = ListedColormap(np.array([[i/255*metalens['wavelength_rgb'][0],i/255*metalens['wavelength_rgb'][1],i/255*metalens['wavelength_rgb'][2],1] for i in range(256)]))

    metalens['sim_cell_width'] = (2*max(metalens['R'],metalens['w']) + 
                  2*metalens['pml_width']+2*metalens['gap']) # height of the simulation cell
    if metalens['w'] >= metalens['R']:
        metalens['sim_cell_width']+= 2*metalens['gap']
    
    metalens['sim_cell_height'] = (metalens['H']+
         metalens['d'] + 2*metalens['pml_width'] +
         2*metalens['gap'])
    
    metalens['top_of_posts_coordinate'] = (-metalens['sim_cell_height']/2
                                        + metalens['H']
                                        + metalens['gap']
                                        + metalens['pml_width']
                                        + metalens['post_height'])
    metalens['source_coordinate'] = -metalens['H']
    
    metalens['eta'] = metalens['w']/metalens['R'] - 1

    metalens['near2far_offset'] = (-metalens['sim_cell_height']/2
                                          + metalens['H']
                                          + metalens['post_height']
                                          + 3*metalens['wavelength'])

#    metalens['f#'] = metalens['f'] / metalens['aperture']
    metalens['source_width'] = 2. / metalens['fcen']
    metalens['simulation time'] = (metalens['source_width']
                                          + metalens['n'] * np.sqrt(metalens['H']**2 + metalens['R']**2) / metalens['wavelength']
                                          + (np.sqrt(metalens['d']**2+metalens['R']**2)) / metalens['wavelength'])

    return metalens

def run_checks(metalens):
    '''
    Kind of outdated.
    '''
    for geometrical_feature in ['source_offset', 'near2far_offset']:
        if metalens[geometrical_feature] > metalens['H']/2 - metalens['pml_width']:
            print(geometrical_feature," is out of bounds.")
        if metalens[geometrical_feature] < -metalens['H']/2 + metalens['pml_width']:
            print(geometrical_feature," is out of bounds.")
    else:
        print("All checks passed.")

#def metalens_old(metalens):
#    '''
#    Run a single threaded Meep simulation for the given simulation
#    parameters.
#    '''
#    metalens = aux_params(metalens)
#    metalens, geometry = make_metalens_geometry(metalens)
#    # Setup the MEEP objects
#    cell = mp.Vector3(metalens['aperture'],
#                      metalens['H'])
#    # All around the simulation cell
#    pml_layers = [mp.PML(metalens['pml_width'])]
#
#    # Let sources be continuous
#    sources = [mp.Source(src=mp.ContinuousSource(wavelength=metalens['wavelength'],
#                                                 width = metalens['source_width']),
#                        component=mp.Ez,
#                        center=mp.Vector3(0,metalens['source_offset']),
#                        size=mp.Vector3(metalens['aperture'] - 2*metalens['pml_width'],0))]
#
#    sim = mp.Simulation(cell_size=cell,
#                       boundary_layers=pml_layers,
#                       geometry=geometry,
#                       force_complex_fields = metalens['complex_fields'],
#                       sources=sources,
#                       resolution=metalens['resolution'])
#    start_time = time.time()
#    metalens['run_date'] = datetime.datetime.now().strftime("%b %d %Y at %H:%M:%S")
#
#    sim.init_sim()
#    sim.run(until=1*metalens['simulation time'])
#
#    eps = sim.get_array(component=mp.Dielectric).transpose()
#    ez = sim.get_array(component=mp.Ez).transpose()
#
#    metalens['run_time_in_s'] = time.time() - start_time
#    metalens['fields'] = {'Ez': ez}
#    pickle.dump(metalens, open('%smetalens-%s.pkl' % (datadir, metalens['sim_id']),'wb'))
#    return metalens

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

import uuid
import subprocess
import pickle
import time
import sys
sys.path.append(os.getcwd())
from metalens import *
import datetime

metalens = pickle.load(open('metalens_temp.pkl','rb'))
metalens = aux_params(metalens)
metalens = metalens(metalens)
pickle.dump(metalens, open(os.path.join(main_dir,'out.pkl'), 'wb'))
print('done')
    '''
    script_fname = 'pmeep-hack-%s.py' % str(uuid.uuid4())
    # save the python script to the playground dir
    with open(script_fname,'w') as f:
        f.write(script)
    command_sequence = ''.join(['source activate pmeep; ',
              'mpirun -n %d python %s' % (num_cores, script_fname)])
    print(command_sequence)
    os.system(command_sequence)
    out = pickle.load(open('out.pkl','rb'))
    os.system('mv out.pkl metalens-%s.pkl' % metalens['sim_id'])
    return out

######################## MEEP functions #######################
###############################################################
