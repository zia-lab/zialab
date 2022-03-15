"""
Plot of cryostat data
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import sqlite3 as sl
import time, sys
from datetime import datetime
import os
import http.client, urllib

sys.path.append("..")
from instruments import montana2

going_down = True

def send_message(message):
    conn = http.client.HTTPSConnection("api.pushover.net",443)
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "aqxvnvfq42adpf78g9pwmphse9c2un",
        "user": "uqhx6qfvn87dtfz5dhk71hf2xh1iwu",
        "message": message,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    return None

def send_count(count):
    conn = http.client.HTTPSConnection("api.pushover.net",443)
    conn.request("POST", "/1/glances.json",
      urllib.parse.urlencode({
        "token": "aqxvnvfq42adpf78g9pwmphse9c2un",
        "user": "uqhx6qfvn87dtfz5dhk71hf2xh1iwu",
        "count": count,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    return None

send_updates = True
last_sent_temp = 0
cryostation = montana2.Montana()
sql = 'INSERT INTO MONTANA (time, chamberPressure, platformTemp, sampleTemp, objTemp) values(?, ?, ?, ?, ?)'

milestone_keys = list(range(20,300,20)) + [290, 295]
milestones = dict(zip(milestone_keys, [False]*len(milestone_keys)))

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('antialias', True)

def get_data():
    return [[d[idx] for d in data] for idx in [0,1,2,3,4]]

dbase = 'C:/Users/lab_pc_cryo/Desktop/cryodbase.db'

generate = False
if not os.path.exists(dbase):
    generate = True

con = sl.connect(dbase)

if generate:
    con.execute("""
        CREATE TABLE MONTANA (
            time REAL,
            chamberPressure REAL,
            platformTemp REAL,
            sampleTemp REAL,
            objTemp Real
        );
    """)
data = con.execute("SELECT * FROM MONTANA WHERE time > 0").fetchall()

if len(data) == 0:
    new_state = cryostation.get_full_state()
    new_time = time.time()
    state = [new_time, *new_state]
    con.execute(sql, state)
    data = [state]

last_sample_temp = data[-1][-2]
for milestone in milestones:
    if not going_down:
        milestones[milestone] = (last_sample_temp >= milestone)
    else:
        milestones[milestone] = (last_sample_temp <= milestone)
print(milestones)

#generate layout
app = QtGui.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('Celatone')
win.setGeometry(80,80,1520,890)
label = pg.LabelItem(justify='center')
win.addItem(label)

sample_temp = win.addPlot(row=1, col=0, title='Sample / K')
platform_temp = win.addPlot(row=2, col=0, title='Platform Temp / K')
chamber_pressure = win.addPlot(row=3, col=0, title='Pressure / Pa')
obj_temp = win.addPlot(row=4, col=0, title='OBJ Temp / K')
selector = win.addPlot(row=5, col=0, title='Sample / K')

region = pg.LinearRegionItem()
region.setZValue(10)
# Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
# item when doing auto-range calculations.
selector.addItem(region, ignoreBounds=True)
sample_temp.setAutoVisible(y=True)
chamber_pressure.setAutoVisible(y=True)
obj_temp.setAutoVisible(y=True)

times, pressures, plat_temps, sample_temps, obj_temps = get_data()
times = (np.array(times) - time.time())/3600

plot_sample_temp = sample_temp.plot(times, sample_temps, pen="r")
plot_platform_temp = platform_temp.plot(times, plat_temps, pen="b")
plot_chamber_pressure = chamber_pressure.plot(times, pressures, pen="g")
plot_obj_temperature = obj_temp.plot(times, obj_temps, pen="y",)
plot_selector = selector.plot(times, sample_temps, pen="r")

selector.setLabel(axis='bottom',text='t/hour')
selector.setXRange(times[0],times[-1], padding=0)
sample_temp.setXRange(times[0],times[-1], padding=0)
sample_temp.setYRange(min(sample_temps), max(sample_temps), padding=0)

widgets = [sample_temp, chamber_pressure, obj_temp, platform_temp]
plot_widgets = [plot_sample_temp, plot_chamber_pressure, plot_obj_temperature, plot_platform_temp]
widget_labels = ['sample','pressure','obj','plat']
for widgy in widgets + [selector]:
    marge = 50
    widgy.setContentsMargins(*(marge,0,marge,0))
sample_temp.setContentsMargins(*(marge,0,marge,0))
selector.setContentsMargins(*(marge,0,marge,marge))

def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()
    maxX = min(maxX,0)
    for aplot in [sample_temp, chamber_pressure, obj_temp, platform_temp]:
        aplot.setXRange(minX, maxX, padding=0)
    back_then = datetime.fromtimestamp(time.time() + minX*3600)
    back_then_str = back_then.strftime("%H:%M:%S")
    selector.setTitle('Sample/K | %s' % back_then_str)

def updateData():
    global data
    global last_sent_temp
    new_state = cryostation.get_full_state()
    new_time = time.time()
    state = (new_time, *new_state)
    last_temp = new_state[-2]
    for milestone in milestones:
        if not going_down:
            going_on = ((last_temp > milestone) and (not milestones[milestone]))
        else:
            going_on = ((last_temp < milestone) and (not milestones[milestone]))
        if going_on:
            # send message
            send_message('%d K reached' % milestone)
            # change to
            milestones[milestone] = True
            break
    if send_updates:
        if int(last_temp) % 5 == 0:
            if int(last_temp) != last_sent_temp:
                send_count(int(last_temp))
                print("update sent at %d K" %(int(last_temp)))
                last_sent_temp = int(last_temp)
    con.execute(sql, state)
    con.commit()
    last_time = data[-1][0]
    data.extend(con.execute("SELECT * FROM MONTANA WHERE time > %d" % last_time).fetchall())
    times, pressures, plat_temps, sample_temps, obj_temps = get_data()
    datas = [sample_temps, pressures, obj_temps, plat_temps]
    now = time.time()
    times = (np.array(times) - now)/3600
    format_strings = 'Sample : %.2f K,Pressure : %.2f Pa,Cryo-Optic : %.2f K,Platform : %.2f K'.split(',')
    for widgy, f_string, datum in zip(widgets, format_strings, datas):
        widgy.setTitle(f_string % datum[-1])
        widgy.setAutoVisible(y=True)
        widgy.enableAutoRange(axis='y')
    plot_selector.setData(y=sample_temps, x=times)
    selector.enableAutoRange(axis='y')
    # selector.enableAutoRange(axis='x')
    selector.setXRange(min(times),max(times), padding=0)
    for widgy, datum in zip(plot_widgets, datas):
        widgy.setData(y=datum, x=times)
    timestamp = datetime.fromtimestamp(now)
    timestamp_s = timestamp.strftime("%H:%M:%S")
    label.setText("<span style='font-size: 30pt'>%s<span style='color: red'>" % (timestamp_s))


t = QtCore.QTimer()
t.timeout.connect(updateData)
t.start(300)

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

# sample_temp.sigRangeChanged.connect(updateRegion)
region.setRegion([times[0] + (times[-1]-times[0])*0.1, times[-1]])

#cross hairs
vLines = {}
hLines = {}
vbs = {}
for widgy, widgylabel in zip(widgets, widget_labels):
    vLine = pg.InfiniteLine(angle=90, movable=False)
    hLine = pg.InfiniteLine(angle=0, movable=False)
    vLines[widgylabel] = vLine
    hLines[widgylabel] = hLine
    widgy.addItem(vLine, ignoreBounds=True)
    widgy.addItem(hLine, ignoreBounds=True)
    vbs[widgylabel] = widgy.vb

def mouseMoved(evt):
    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
    for widgy, widgylabel in zip(widgets, widget_labels):
        if widgy.sceneBoundingRect().contains(pos):
            mousePoint = vbs[widgylabel].mapSceneToView(pos)
            #label.setText("(%0.2f hours ago, %0.1f K)" % (mousePoint.x(), mousePoint.y()))
            # label.setText("%0.1f K" % (mousePoint.y()))
            # label.setPos(mousePoint.x(), mousePoint.y())
            vLines[widgylabel].setPos(mousePoint.x())
            hLines[widgylabel].setPos(mousePoint.y())

proxy = pg.SignalProxy(sample_temp.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    con.close()
