"""
Plot of lakeshore data
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import sqlite3 as sl
import time
from datetime import datetime
import sys
import os
sys.path.append("..")
from instruments import lakeshore

# for this to work the lakeshore_server.py script must be running.

lake = lakeshore.LS335()

def get_data():
    return [[d[idx] for d in data] for idx in [0,1,2]]

dbase = 'C:/Users/lab_pc_cryo/Desktop/lakedbase.db'
generate = False
if not os.path.exists(dbase):
    generate = True
con = sl.connect(dbase)

if generate:
    con.execute("""
        CREATE TABLE LAKESHORE (
            time REAL,
            realTemp REAL,
            setTemp REAL
        );
    """)

sql = 'INSERT INTO LAKESHORE (time, realTemp, setTemp) values(?, ?, ?)'

data = con.execute("SELECT * FROM LAKESHORE WHERE time > 0").fetchall()

if len(data) == 0:
    data = [[time.time(), lake.getTemp(), lake.getSP()]]

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')
pg.setConfigOption('antialias', True)

app = QtGui.QApplication([])

# # Set up UI widgets
# win2 = pg.QtGui.QWidget()
# win2.setWindowTitle('LakeShores')
# layout2 = pg.QtGui.QGridLayout()
# win2.setLayout(layout2)
# layout2.setContentsMargins(0, 0, 0, 0)
# depthLabel = pg.QtGui.QLabel('Max Hours:')
# layout2.addWidget(depthLabel, 0, 0)
# depthSpin = pg.SpinBox(value=0, step=1, bounds=[0, 10], delay=0, int=True)
# # depthSpin.resize(100, 20)
# layout2.addWidget(depthSpin, 0, 1)
# w2 = pg.GraphicsLayoutWidget()
# layout2.addWidget(w2, 1, 0, 1, 2)
# win2.show()

#generate layout

win0 = pg.QtGui.QWidget()
win0.setWindowTitle('Lakesore')
win0.setGeometry(80,80,1520,890)
layout = pg.QtGui.QGridLayout()
layout.setContentsMargins(0, 0, 0, 0)
depthLabel = pg.QtGui.QLabel('Max Hours:')
layout.addWidget(depthLabel, 0, 0)
depthSpin = pg.SpinBox(value=0, step=1, bounds=[0, 10], delay=0, int=True)
layout.addWidget(depthSpin, 0, 1)

glwin = pg.GraphicsLayoutWidget()
layout.addWidget(glwin, 1, 1, 1, 2)
label = pg.LabelItem(justify='center')
glwin.addItem(label)

win = glwin.addViewBox()

# rangeLabel = pg.QtGui.QLabel('Max Hours')
# win.addWidget(rangeLabel, 0, 0)
sample_temp = win.addPlot(row=1, col=0, title='Thermometer, Set Point / K')
selector = win.addPlot(row=2, col=0, title='Termometer / K')

region = pg.LinearRegionItem()
region.setZValue(10)
# Add the LinearRegionItem to the ViewBox, but tell the ViewBox to exclude this
# item when doing auto-range calculations.
selector.addItem(region, ignoreBounds=True)
sample_temp.setAutoVisible(y=True)

times, sample_temps, set_temps = get_data()
times = (np.array(times) - time.time())/3600

plot_sample_temp = sample_temp.plot(times, sample_temps, pen="y")
plot_set_temp = sample_temp.plot(times, set_temps, pen="g")
plot_selector = selector.plot(times, sample_temps, pen="y")

selector.setLabel(axis='bottom',text='t/hour')
if len(times) > 1:
    selector.setXRange(times[0],times[-1], padding=0)
    sample_temp.setXRange(times[0],times[-1], padding=0)
    sample_temp.setYRange(min(sample_temps), max(sample_temps), padding=0)
else:
    selector.setXRange(times[0],-0.1, padding=0)
    sample_temp.setXRange(times[0],-0.1, padding=0)
    sample_temp.setYRange(min(sample_temps), max(sample_temps), padding=0)

widgets = [sample_temp]
plot_widgets = [plot_sample_temp, plot_set_temp]
widget_labels = ['sample']

marge = 50
sample_temp.setContentsMargins(*(marge,0,marge,0))
selector.setContentsMargins(*(marge,0,marge,marge))

def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()
    maxX = min(maxX,0)
    for aplot in [sample_temp]:
        aplot.setXRange(minX, maxX, padding=0)

def updateData():
    global data
    new_temp = lake.getTemp()
    new_SP = lake.getSP()
    new_time = time.time()
    state = (new_time, new_temp, new_SP)
    con.execute(sql, state)
    con.commit()
    last_time = data[-1][0]
    data.extend(con.execute("SELECT * FROM LAKESHORE WHERE time > %d" % last_time).fetchall())
    times, sample_temps, set_temps = get_data()
    datas = [sample_temps, set_temps]
    now = time.time()
    times = (np.array(times) - now)/3600
    format_strings = 'Sample : %.2f K'.split(',')
    for widgy, f_string, datum in zip(widgets, format_strings, datas):
        widgy.setTitle(f_string % datum[-1])
        widgy.setAutoVisible(y=True)
        widgy.enableAutoRange(axis='y')
    plot_selector.setData(y=sample_temps, x=times)
    # selector.enableAutoRange(axis='x')
    if depthSpin.value() == 0:
        selector.setXRange(min(times),max(times), padding=0)
    else:
        selector.setXRange(-depthSpin.value(),max(times), padding=0)
    selector.enableAutoRange(axis='y')
    for widgy, datum in zip(plot_widgets, datas):
        widgy.setData(y=datum, x=times)
    timestamp = datetime.fromtimestamp(now)
    timestamp_s = timestamp.strftime("%H:%M:%S")
    label.setText("<span style='font-size: 30pt'>%s<span style='color: red'>" % (timestamp_s))


t = QtCore.QTimer()
t.timeout.connect(updateData)
t.start(1000)

region.sigRegionChanged.connect(update)

def updateRegion(window, viewRange):
    rgn = viewRange[0]
    region.setRegion(rgn)

sample_temp.sigRangeChanged.connect(updateRegion)
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
            vLines[widgylabel].setPos(mousePoint.x())
            hLines[widgylabel].setPos(mousePoint.y())

proxy = pg.SignalProxy(sample_temp.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
    con.close()
