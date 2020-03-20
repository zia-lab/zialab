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

# setup directories

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

s4dir = '/Users/juan/Google Drive/Zia Lab/CEM/S4/'

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
    return 2
    return ((np.pi / wavelength) * n * (H - np.sqrt(x**2 + H**2)) -
     (np.pi / wavelength) * (d - np.sqrt(eta**2 * x**2 + d**2)) / eta)

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
    sim_params['eta'] = sim_params['w']/sim_params['R'] - 1
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

def make_metalens_geometry(metalens_params):
    '''
    Given metalens parameters, determine the required phases, and using
    these and the known width to phase relationship, determine the
    required widths for the posts.
    '''
    # first design the mask based on the given widths and corresponding phases
    widths = metalens_params['widths']
    phases = metalens_params['phases']
    wavelength = metalens_params['wavelength']
    good_widths = (widths >= metalens_params['min_width'])
    widths = widths[good_widths]
    phases = phases[good_widths]
    aperture = metalens_params['aperture']
    f = metalens_params['f']
    # compute the required phases based on the wavelength, 
    # focal length and number of unit cells
    if (max(phases)-min(phases)) < 2*np.pi:
        print((max(phases)-min(phases)))
        return "not a full phase coverage"
    x, y = function_topper(widths, phases)
    axis_positions = np.linspace((-metalens_params['unit cell size']*
                              (metalens_params['num of unit cells']-1)/2),
                              (metalens_params['unit cell size']*
                              (metalens_params['num of unit cells']-1)/2),
                              metalens_params['num of unit cells'])
    required_phases = -2*np.pi/wavelength*(np.sqrt((axis_positions-metalens_params['axial_offset'])**2+f**2)-f)
    required_phases = required_phases - min(required_phases)
    required_phases = required_phases % (2*np.pi)
    required_widths = np.interp(required_phases, y, x)
    # create the posts
    hairline = [mp.Block(size=mp.Vector3(w, metalens_params['post_height']),
                    center = mp.Vector3(position,(-metalens_params['H']/2
                                                  +metalens_params['sub_thickness']
                                                  +metalens_params['post_height']/2)),
                    material = mp.Medium(epsilon = metalens_params['epsilon'])) for w, position in zip(required_widths, axis_positions)]
    # create the substrate
    substrate = [mp.Block(size = mp.Vector3(aperture,metalens_params['sub_thickness']),
                        center = mp.Vector3(0,-metalens_params['H']/2+metalens_params['sub_thickness']/2),
                        material = mp.Medium(epsilon = metalens_params['epsilon']))]
    metalens_params['required_phases'] = required_phases
    metalens_params['required_widths'] = required_widths
    metalens_params['axis_positions'] = axis_positions
    return metalens_params, substrate + hairline

def aux_params(metalens_params):
    '''
    Compute a few additional parameters.
    '''
    metalens_params['num of unit cells'] = int(metalens_params['aperture'] / metalens_params['unit cell size'])
    if metalens_params['num of unit cells'] % 2:
        pass
    else:
        metalens_params['num of unit cells'] += -1

    metalens_params['f'] = focal_length(metalens_params['NA'],metalens_params['aperture'])
    metalens_params['fcen'] = 1/metalens_params['wavelength']
    metalens_params['n'] = np.sqrt(metalens_params['epsilon'])

    metalens_params['H'] = metalens_params['sub_thickness'] + metalens_params['post_height'] + metalens_params['air_space'] # height of the simulation cell
    metalens_params['top_of_posts_coordinate'] = (-metalens_params['H']/2
                                        + metalens_params['sub_thickness']
                                        + metalens_params['post_height'])

    metalens_params['source_offset'] = (-metalens_params['H']/2
                                        + metalens_params['sub_thickness']
                                        - 3*metalens_params['wavelength'])
    metalens_params['near2far_offset'] = (-metalens_params['H']/2
                                          + metalens_params['sub_thickness']
                                          + metalens_params['post_height']
                                          + 3*metalens_params['wavelength'])

    metalens_params['f#'] = metalens_params['f'] / metalens_params['aperture']
    metalens_params['source width'] = 2. / metalens_params['fcen']
    metalens_params['simulation time'] = (metalens_params['source width']
                                          + metalens_params['n'] * metalens_params['sub_thickness'] / metalens_params['wavelength']
                                          + (metalens_params['H'] - metalens_params['sub_thickness']) / metalens_params['wavelength'])
    metalens_params['f#'] = metalens_params['aperture']/metalens_params['f']

    return metalens_params

def run_checks(metalens_params):
    '''
    Kind of outdated.
    '''
    for geometrical_feature in ['source_offset', 'near2far_offset']:
        if metalens_params[geometrical_feature] > metalens_params['H']/2 - metalens_params['pml width']:
            print(geometrical_feature," is out of bounds.")
        if metalens_params[geometrical_feature] < -metalens_params['H']/2 + metalens_params['pml width']:
            print(geometrical_feature," is out of bounds.")
    else:
        print("All checks passed.")

def metalens(metalens_params):
    '''
    Run a single threaded Meep simulation for the given simulation
    parameters.
    '''
    metalens_params = aux_params(metalens_params)
    metalens_params, geometry = make_metalens_geometry(metalens_params)
    # Setup the MEEP objects
    cell = mp.Vector3(metalens_params['aperture'],
                      metalens_params['H'])
    # All around the simulation cell
    pml_layers = [mp.PML(metalens_params['pml width'])]

    # Let sources be continuous
    sources = [mp.Source(src=mp.ContinuousSource(wavelength=metalens_params['wavelength'],
                                                 width = metalens_params['source width']),
                        component=mp.Ez,
                        center=mp.Vector3(0,metalens_params['source_offset']),
                        size=mp.Vector3(metalens_params['aperture'] - 2*metalens_params['pml width'],0))]

    sim = mp.Simulation(cell_size=cell,
                       boundary_layers=pml_layers,
                       geometry=geometry,
                       force_complex_fields = metalens_params['complex_fields'],
                       sources=sources,
                       resolution=metalens_params['resolution'])
    start_time = time.time()
    metalens_params['run_date'] = datetime.datetime.now().strftime("%b %d %Y at %H:%M:%S")

    sim.init_sim()
    sim.run(until=1*metalens_params['simulation time'])

    eps = sim.get_array(component=mp.Dielectric).transpose()
    ez = sim.get_array(component=mp.Ez).transpose()

    metalens_params['run_time_in_s'] = time.time() - start_time
    metalens_params['fields'] = {'Ez': ez}
    pickle.dump(metalens_params, open('%smetalens-%s.pkl' % (datadir, metalens_params['sim_id']),'wb'))
    return metalens_params

def para_metalens(metalens_params, num_cores):
    '''
    Run script in the parallel environment for MEEP.
    '''
    print("See progress in terminal.")
    # save the params to disk
    pickle.dump(metalens_params, open('metalens_params_temp.pkl','wb'))
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

metalens_params = pickle.load(open('metalens_params_temp.pkl','rb'))
metalens_params = aux_params(metalens_params)
metalens_params = metalens(metalens_params)
pickle.dump(metalens_params, open(os.path.join(main_dir,'out.pkl'), 'wb'))
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
    os.system('mv out.pkl metalens-%s.pkl' % metalens_params['sim_id'])
    return out

######################## MEEP functions #######################
###############################################################
