#!/usr/bin/env python3

import numpy as np
from time import sleep, time
import re
import sys
codebase_dir = 'D:/ZiaLab/Codebase/'
sys.path.append(codebase_dir)
from zialab.misc.sugar import send_message
from tenacity import retry, stop_after_attempt

AXES_RANGE = 40. # in mm

def navigation_matrix(n1,m1,n2,m2,x1,y1,x2,y2):
    return np.matrix([[-(-m2 * x1 + m1 * x2)/(m2*n1 - m1*n2),-(n2*x1 - n1*x2)/(m2*n1 - m1*n2)],
            [-(-m2*y1+m1*y2)/(m2*n1-m1*n2),-(-n2*y1 + n1*y2)/(-m2*n1+m1*n2)]])

def parse_num_coords(str_coord):
    letters = {c: idx for idx, c in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx')}
    letter = re.findall('(\D)',str_coord)[0]
    nums = ''.join(re.findall('(\d)',str_coord))
    return np.array([int(nums),letters[letter]])

def move_and_wait(stage, axis, position):
    '''
    Move to the commanded position and wait until it's reached.
    Parameters
    ----------
    axis  (str): 'x' or 'y'
    position (float): position in mm
    '''
    assert axis in ['x','y']
    axis = {'x':'1','y':'2'}[axis]
    assert type(position) in [int,float,np.float64, np.float32, np.int32, np.int64], "wacky position"
    assert abs(position) < AXES_RANGE, "position out of range"
    stage.MOV(axis,position)
    while not stage.qONT()[axis]:
        sleep(0.01)

def TRO(stage, tro_state):
    if tro_state.lower() == 'off':
        stage.GcsCommandset('TRO 1 0')
        stage.GcsCommandset('TRO 2 0')
    if tro_state.lower() == 'ON':
        stage.GcsCommandset('TRO 1 1')
        stage.GcsCommandset('TRO 2 1')

def setCTO(stage, StartThreshold, StopThreshold, velocity, TriggerStep, Axis='1', Polarity=1, TriggerMode=0):  # Configure the CTO
    stage.GcsCommandset('TRO 2 1')
    stage.GcsCommandset('CTO 2 1 ' + str(TriggerStep))
    stage.GcsCommandset('CTO 2 2 ' + Axis)
    stage.GcsCommandset('CTO 2 3 ' + str(TriggerMode))
    stage.GcsCommandset('CTO 2 8 ' + str(StartThreshold))
    stage.GcsCommandset('CTO 2 9 ' + str(StopThreshold))
    stage.GcsCommandset('CTO 2 10 ' + str(StartThreshold))
    stage.GcsCommandset('VEL x ' + str(velocity))
    stage.GcsCommandset('VEL y ' + str(velocity))

def parse_events(events):
    T3WRAPAROUND = 65536
    parsed_events = []
    oflcorrection = 0
    truensync = 0
    for event in events:
        record = '{0:0{1}b}'.format(event,32)
        channel = int(record[:4],base=2)
        dtime = int(record[4:16], base=2)
        nsync = int(record[16:], base=2)
        if channel == 0xF:
            if dtime == 0:
                oflcorrection += T3WRAPAROUND
            else:
                truensync = oflcorrection + nsync
        else:
            truensync = oflcorrection + nsync
        parsed_events.append([channel, dtime, nsync, truensync])
    return parsed_events

def parse_T2_events(events):
    parsed_events = []
    T2WRAPAROUND = 210698240
    oflcorrection=0
    truetime=0
    for event in events:
        record = '{0:0{1}b}'.format(event,32)
        channel = int(record[:4],base=2)
        time = int(record[4:],base=2)
        if channel == 15:
            marker = int(record[28:32], base=2)
            if marker == 0:
                oflcorrection += T2WRAPAROUND
            else:
                truetime = oflcorrection + time
                parsed_events.append([2,truetime])
        else:
            truetime = oflcorrection + time
            parsed_events.append([channel,truetime])
    parsed_events = np.array(parsed_events)
    return parsed_events

def snr_to_vel(scan):
    '''
    Using the current count rate, the trigger step,
    an assumed noise rate, and a target SNR, the required
    speed is returned. If the calculated speed is greater
    that the set maximum speed, then the maximum speed is
    returned.
    '''
    MAX_vel = 0.5 # in mm/s
    target_vel = (np.sqrt(scan['dx']) * (scan['cr'] - scan['nr'])/np.sqrt(scan['cr'] + scan['nr']) / scan['SNR'])**2
    if target_vel > MAX_vel:
        snr = np.sqrt(scan['dx']/MAX_vel) * (scan['cr']-scan['nr'])/np.sqrt(scan['cr']+scan['nr'])
        print("target_vel larger than max, SNR changed to %f" % snr)
        return MAX_vel
    else:
        return target_vel

def compute_runway(stage, vel, fast=False, tol=0.001):
    '''
    Parameters
    ----------
    stage   (zialab.instruments.stage)
    vel     (float): scan speed in mm/s
    fast    (bool): if True then previous values are used to estimate adequate runway.
    tol     (float): tolerance for error in trial motion
    Returns
    -------
    goodrunway (float): runway in mm
    '''
    if (not fast) or (vel < 0.00125) or (vel > 0.8):
        stage.DRT(0,1,'1')
        d = 0.1 # move 100 um
        current_x = stage.qPOS()['1']
        original_vel = stage.qVEL()['1']
        stage.VEL('1',vel)
        move_and_wait(stage, 'x', current_x+d)
        # read the data tables
        stage.qDRR()
        while not stage.bufstate:
            sleep(0.1)
            pass
        stage.VEL('1',original_vel)
        times = np.array(stage.bufdata[0])
        times = times-times[0]
        commanded = np.array(stage.bufdata[1])
        actual = np.array(stage.bufdata[2])
        err = np.abs(np.abs(commanded-actual))
        maxerrarg = np.argmax(err)
        err = err[maxerrarg:]
        errtimes = times[maxerrarg:]
        erractual = actual[maxerrarg:]
        for idx, oneerr in enumerate(err):
            if oneerr < tol:
                break
        goodtimearg = idx
        goodrunway = np.abs(erractual[goodtimearg] - current_x)
        stage.DRT(0,1,'0')
        return goodrunway
    else:
        # interpolate using precomputed values
        vels = np.array([0.0125, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8])
        runways = np.array([0.00230,0.00370,0.00600,
                            0.00940,0.01570,0.02740,0.05860])
        return np.interp(vel,vels,runways)

def linescanner(stage, pharp, linescan, verbose=False):
    linescan['reads'] = [] # in this list the events will be collected
    linescan['xf'] = (linescan['xi'] 
            + np.ceil((linescan['xf']-linescan['xi'])
                      /linescan['dx'])*linescan['dx'])
    linescan['N'] = int(round(((linescan['xf']-linescan['xi'])
                              /linescan['dx']))+1)
    linescan['ts'] = ((linescan['xf']-linescan['xi']+2*linescan['e'])
                      /linescan['velx'])
    linescan['dt'] = 0.25*linescan['ts'] # how often the buffer will be read
    linescan['tph'] = 1.2*linescan['ts'] # measurement time for picoharp
    linescan['start'] = linescan['xi'] - linescan['e']
    linescan['end'] = linescan['xf'] + linescan['e']
    linescan['dwell_time'] = linescan['dx'] / linescan['velx']
    if verbose:
        print('Scan will take about {ts} s.'.format(**linescan))

    # move to start at speed vsafe
    stage.VEL('1',linescan['vsafe'])
    stage.VEL('2',linescan['vsafe'])
    move_and_wait(stage, 'x', linescan['start'])
    move_and_wait(stage, 'y', linescan['y'])
    # configure CTO and set speed
    stage.VEL('1',linescan['velx'])
    setCTO(stage, **{'StartThreshold':linescan['xi'],
                    'StopThreshold':linescan['xf'],
                    'velocity':linescan['velx'],
                    'TriggerStep':linescan['dx']})
    # start measurement on picoharp
    pharp.start_measurement(linescan['tph'])
    # issue the motion command to the stage
    try:
        stage.MOV('1', linescan['end'])
    except:
        stage.MOV('1', linescan['end'])
    # read buffer in a loop and stop when stage arrives to end
    while True:
        sleep(linescan['dt'])
        buff = pharp.buffer_read()
        if buff != None:
            if verbose:
                print('adding events ...')
            linescan['reads'].extend(list(buff))
        if stage.qONT()['1']:
            break
    for idx in range(10):
        if verbose:
            print(idx)
        buff = pharp.buffer_read()
        if buff != None:
            if verbose:
                print('adding events ...')
            linescan['reads'].extend(list(buff))
    pharp.stop_measurement()
    linescan['events'] = np.array(parse_events(linescan['reads']))
    linescan['parsed_scan'] = np.diff(linescan['events'][linescan['events'][:,1] == 8][:,3])/linescan['dwell_time']/1000
    linescan['x_coords'] = np.linspace(linescan['xi'],linescan['xf'],len(linescan['parsed_scan']))
    TRO(stage, "off")
    return linescan

def scanner(stage, pharp, scan):
    '''
    Do a raster scan on a given region by performing a sequence of line scans.
    If cleaning_run is True then the scan begins by moving both axes 2mm
    in each direction, this helps greatly in improving the reliability of
    the resulting scan. This run is done at speed v_cleaning.
    
    If a scanning speed velx is given then this speed is used,
    if not then it is computed with the target SNR according to the
    count rate at the staring position. 
    
    When returning to the left margin after having scanned a row, the
    stage returns there moving at a speed v_safe.
    
    Every linescan begins has a runway length computed by the functtion
    compute_runway which is a function of the scan speed.
    '''
    # works consistently in a on scanning regions larger that about 20 um
    # scans every row left to right
    # and goes from bottom to top
    assert scan['yf'] > scan['yi'], "yf must be larger than yi"
    assert scan['xf'] > scan['xi'], "xf must be larger than xi"
    scan['yf'] = (scan['yi'] 
                  + np.ceil((scan['yf']-scan['yi'])/scan['dx'])*scan['dx'])
    scan['Ny'] = int(round((scan['yf']-scan['yi'])/scan['dx']))
    scan['ys'] = np.linspace(scan['yi'],scan['yf'],scan['Ny'])
    if scan['cleaning_run']:
        print("Running a cleaning run ...")
        stage.VEL('1',scan['v_cleaning'])
        stage.VEL('2',scan['v_cleaning'])
        move_and_wait(stage, 'y', scan['yi'])
        move_and_wait(stage, 'x', scan['xi'])
        move_and_wait(stage, 'x', scan['xi']-2)
        move_and_wait(stage, 'x', scan['xi']+2)
        move_and_wait(stage, 'y', scan['yi']-2)
        move_and_wait(stage, 'y', scan['yi']+2)
    move_and_wait(stage, 'y', scan['yi'])
    move_and_wait(stage, 'x', scan['xi'])
    scan['start_time'] = time()
    print("Reading the countrate in the starting position...")
    scan['cr'] = pharp.get_counts()[0]
    if 'velx' not in scan.keys():
        print("Computing speed from given target SNR...")
        scan['velx'] = snr_to_vel(scan)
    scan['SNR'] = (np.sqrt(scan['dx']/scan['velx']) 
                   * (scan['cr']-scan['nr'])/np.sqrt(scan['cr']+scan['nr']))
    stage.VEL('2',scan['velx'])
    if scan['fast_runway']:
        scan['e'] = compute_runway(stage, scan['velx'], fast=True)
    else:
        scan['e'] = compute_runway(stage, scan['velx'], fast=False)
    print("Doing linescans...")
    for idx, y in enumerate(scan['ys']):
        print('row %d of %d' % (idx+1, len(scan['ys'])))
        move_and_wait(stage, 'y',y)
        linescan = {'velx': scan['velx'],
               'e': scan['e'],
               'xi': scan['xi'],
               'xf': scan['xf'],
               'dx': scan['dx'], # trigger step
               'vsafe': scan['vsafe'],
               'y': y,
               'nr': scan['nr'],
               'SNR': scan['SNR']}
        linescan = linescanner(linescan)
        scan['linescans'].append(linescan)
        elapsed_time = time() - scan['start_time']
        rem_time = (scan['Ny']-idx+1)*elapsed_time/(idx+1)/60.
        print('Time remaining: %.1f min' % rem_time)
    
    print("Computing final scan result...")
    rows = [onescan['parsed_scan'] for onescan in scan['linescans']]
    expectedcols = [(s['N']) for s in scan['linescans']]
    colsizes = list(map(len,rows))
    if min(colsizes) != max(colsizes): # if all is good leave as is
        # if not then do some interpolation to put everything in shape
        print("Probable jitter motion detected, using heuristic parsing...")
        colsize = np.median(colsizes)
        x_coords = np.linspace(scan['xi'],scan['xf'],int(colsize))
        interprows = [np.interp(x_coords,
                                np.linspace(scan['xi'],scan['xf'],len(row)),
                                row) for row in rows]
        scan['final_map'] = np.array(interprows)
    else:
        print("All rows good...")
        scan['final_map'] = np.array(rows)
    
    print("Tidying things up...")
    scan['xf'] = linescan['xf'] # propagate the adjusted xf to scan
    scan['time_taken'] = time() - scan['start_time']
    scan['mins_taken'] = scan['time_taken']/60.
    scan['dx_in_um'] = scan['dx']*1000
    scan['info_title'] = '{sample_name}\nv = {velx:.2f} mm/s | SNR -> {SNR:.1f} | {mins_taken:.2f} min | dx = {dx_in_um} um'.format(**scan)
    return scan 

def linescan_retry_alert(retry_state):
    alert_msg = 'Failure detected in linescan, retrying...'
    send_message(alert_msg)

@retry(stop=stop_after_attempt(3),
      after=linescan_retry_alert)
def T2linescanner(stage, pharp, linescan, verbose=False):
    linescan['reads'] = [] # in this list the events will be collected
    linescan['xf'] = (linescan['xi'] 
            + np.ceil((linescan['xf_original']-linescan['xi'])
                      /linescan['dx'])*linescan['dx'])
    linescan['N'] = int(round(((linescan['xf']-linescan['xi'])
                              /linescan['dx']))+1)
    linescan['ts'] = ((linescan['xf']-linescan['xi']+2*linescan['e'])
                      /linescan['velx'])
    linescan['dt'] = 0.25*linescan['ts'] # how often the buffer will be read
    linescan['tph'] = 1.2*linescan['ts'] # measurement time for picoharp
    linescan['start'] = linescan['xi'] - linescan['e']
    linescan['end'] = linescan['xf'] + linescan['e']
    linescan['dwell_time'] = linescan['dx'] / linescan['velx']
    if verbose:
        print('Scan will take about {ts} s.'.format(**linescan))

    # move to start at speed vsafe
    stage.VEL('1',linescan['vsafe'])
    stage.VEL('2',linescan['vsafe'])
    move_and_wait(stage, 'x',linescan['start'])
    move_and_wait(stage, 'y',linescan['y'])
    # configure CTO and set speed
    stage.VEL('1',linescan['velx'])
    setCTO(stage, **{'StartThreshold':linescan['xi'],
                    'StopThreshold':linescan['xf'],
                    'velocity':linescan['velx'],
                    'TriggerStep':linescan['dx']})
    # start measurement on picoharp
    pharp.start_measurement(linescan['tph'])
    # enable data recorder on the stage
    try:
        stage.DRT(0,1,'1')
    except:
        stage.DRT(0,1,'1')
    # issue the motion command to the stage
    try:
        stage.MOV('1', linescan['end'])
    except:
        stage.MOV('1', linescan['end'])
    # read buffer in a loop and stop when stage arrives to end
    while True:
        sleep(linescan['dt'])
        buff = pharp.buffer_read()
        if buff != None:
            if verbose:
                print('adding events ...')
            linescan['reads'].extend(list(buff))
        if stage.qONT()['1']:
            break
    for idx in range(10):
        if verbose:
            print(idx)
        buff = pharp.buffer_read()
        if buff != None:
            if verbose:
                print('adding events ...')
            linescan['reads'].extend(list(buff))
    pharp.stop_measurement()
    # read the data tables on the stage
    stage.qDRR()
    while not stage.bufstate:
        sleep(0.1)
        pass
    trajectory = {}
    trajectory['times'] = np.array(stage.bufdata[0])
    trajectory['times'] = trajectory['times'] - trajectory['times'][0]
    trajectory['commanded_positions'] = np.array(stage.bufdata[1])
    trajectory['actual_positions'] = np.array(stage.bufdata[2])
    linescan['trajectory'] = trajectory
    stage.DRT(0,1,'0')
    linescan['events'] = np.array(parse_T2_events(linescan['reads']))
    linescan['numsteps'] = int((linescan['xf']-linescan['xi']+2*linescan['e'])/linescan['dx'])
    linescan['bintimes'] = linescan['events'][linescan['events'][:,0] == 2][:,1]
    linescan['events'] = linescan['events'][linescan['events'][:,0] != 2][:,1]
    linescan['parsed_scan'], _, = np.histogram(linescan['events'], bins=linescan['bintimes'])
    linescan['x_coords'] = np.linspace(linescan['xi']-linescan['e'],linescan['xf']+linescan['e'],len(linescan['parsed_scan']))
    TRO(stage, "off")
    return linescan

def T2scanner_retry_alert(stage, retry_state):
    alert_msg = 'Failure detected in T2scanner, retrying...'
    send_message(alert_msg)

@retry(stop=stop_after_attempt(3),
      after=T2scanner_retry_alert)
def T2scanner(stage, pharp, scan):
    '''
    Do a raster scan on a given region by performing a sequence of line scans.
    If cleaning_run is True then the scan begins by moving both axes 2mm
    in each direction, this helps greatly in improving the reliability of
    the resulting scan. This run is done at speed v_cleaning.
    
    If a scanning speed velx is given then this speed is used,
    if not then it is computed with the target SNR according to the
    count rate at the staring position. 
    
    When returning to the left margin after having scanned a row, the
    stage returns there moving at a speed v_safe.
    
    Every linescan begins has a runway length computed by the function
    compute_runway which is a function of the scan speed.
    '''
    # works consistently in a on scanning regions larger that about 20 um
    # scans every row left to right
    # and goes from bottom to top
    assert scan['yf'] > scan['yi'], "yf must be larger than yi"
    assert scan['xf'] > scan['xi'], "xf must be larger than xi"
    scan['yf'] = (scan['yi'] 
                  + np.ceil((scan['yf']-scan['yi'])/scan['dx'])*scan['dx'])
    scan['Ny'] = int(round((scan['yf']-scan['yi'])/scan['dx']))
    scan['ys'] = np.linspace(scan['yi'],scan['yf'],scan['Ny'])
    if scan['cleaning_run']:
        print("Running a cleaning run ...")
        stage.VEL('1',scan['v_cleaning'])
        stage.VEL('2',scan['v_cleaning'])
        move_and_wait(stage, 'y', scan['yi'])
        move_and_wait(stage, 'x', scan['xi'])
        move_and_wait(stage, 'x', scan['xi']-2)
        move_and_wait(stage, 'x', scan['xi']+2)
        move_and_wait(stage, 'y', scan['yi']-2)
        move_and_wait(stage, 'y', scan['yi']+2)
    move_and_wait(stage, 'y', scan['yi'])
    move_and_wait(stage, 'x', scan['xi'])
    scan['start_time'] = time()
    print("Reading the countrate in the starting position...")
    scan['cr'] = pharp.get_counts()[0]
    if 'velx' not in scan.keys():
        print("Computing speed from given target SNR...")
        scan['velx'] = snr_to_vel(scan)
    scan['SNR'] = (np.sqrt(scan['dx']/scan['velx']) 
                   * (scan['cr']-scan['nr'])/np.sqrt(scan['cr']+scan['nr']))
    stage.VEL('2',scan['velx'])
    if scan['fast_runway']:
        scan['e'] = compute_runway(stage, scan['velx'], fast=True)
    else:
        scan['e'] = compute_runway(stage, scan['velx'], fast=False)
    print("Doing linescans...")
    scan['linescans'] = []
    for idx, y in enumerate(scan['ys']):
        print('row %d of %d' % (idx+1, len(scan['ys'])))
        move_and_wait(stage, 'y', y)
        linescan = {'velx': scan['velx'],
               'e': scan['e'],
               'xi': scan['xi'],
               'xf': scan['xf'],
               'xf_original': scan['xf'],    
               'dx': scan['dx'], # trigger step
               'vsafe': scan['vsafe'],
               'y': y,
               'nr': scan['nr'],
               'SNR': scan['SNR']}
        linescan = T2linescanner(stage, pharp, linescan)
        scan['linescans'].append(linescan)
        elapsed_time = time() - scan['start_time']
        rem_time = (scan['Ny']-idx+1)*elapsed_time/(idx+1)/60.
        print('Time remaining: %.1f min' % rem_time)
    
    print("Computing final scan result with simple parsing...")
    rows = [onescan['parsed_scan'] for onescan in scan['linescans']]
    expectedcols = [(s['N']) for s in scan['linescans']]
    colsizes = list(map(len,rows))
    if min(colsizes) != max(colsizes): # if all is good leave as is
        # if not then do some interpolation to put everything in shape
        print("Probable jitter motion detected, using heuristic parsing...")
        colsize = np.median(colsizes)
        x_coords = np.linspace(scan['xi'],scan['xf'],int(colsize))
        interprows = [np.interp(x_coords,
                                np.linspace(scan['xi'],scan['xf'],len(row)),
                                row) for row in rows]
        scan['final_map_simple'] = np.flip(np.array(interprows),axis=1)
    else:
        print("All rows good...")
        scan['final_map_simple'] = np.flip(np.array(rows), axis=1)
    
    print("Computing final scan result with improved parsing...")
    all_better_counts = []
    all_dwell_times = []
    for linescan in scan['linescans']:
        clicks = (linescan['events'])*4./1e9
        position_marks = (linescan['bintimes'])*4/1e9
        position_marks = position_marks - position_marks[0]
        stage_times =  (linescan['trajectory']['times'])
        stage_dt = stage_times[1]-stage_times[0] # in ms
        stage_positions = (linescan['trajectory']['actual_positions'])
        for stage_time_pivot in stage_positions:
            if stage_time_pivot >= linescan['xi']:
                break
        stage_times = stage_times - stage_time_pivot
        interpol_clicks = np.interp(clicks, stage_times, stage_positions)
        linescan_marks = np.arange(linescan['xi'], linescan['xf'], linescan['dx'])
        better_counts, _ = np.histogram(interpol_clicks, linescan_marks)
        dwell_times, _ = np.histogram(stage_positions, bins= linescan_marks)
        all_dwell_times.append(stage_dt*dwell_times)
        all_better_counts.append(better_counts)
    all_better_counts = np.flip(np.array(all_better_counts), axis=1)
    all_dwell_times = np.flip(np.array(all_dwell_times), axis=1)
    scan['final_map'] = all_better_counts/all_dwell_times
    
    print("Tidying things up...")
    scan['xf'] = linescan['xf'] # propagate the adjusted xf to scan
    scan['time_taken'] = time() - scan['start_time']
    scan['mins_taken'] = scan['time_taken']/60.
    scan['dx_in_um'] = scan['dx']*1000
    scan['info_title'] = '{sample_name}\nv = {velx:.2f} mm/s | SNR -> {SNR:.1f} | {mins_taken:.2f} min | dx = {dx_in_um} um'.format(**scan)
    return scan 

