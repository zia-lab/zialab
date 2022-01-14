import time
import numpy as np
from datetime import datetime, timedelta
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui

pg.setConfigOption('background', 'k')
pg.setConfigOption('foreground', 'w')
margin = 50

weather_csv = '/Users/juan/Downloads/Weather Lab - Lab.csv'
dates = list(map(lambda x: datetime.strptime(x, '%m/%d/%y %H:%M').timestamp(),
            np.genfromtxt(weather_csv, delimiter=',',
            skip_header=1, usecols=0, dtype=(str))))
# np.savetxt('/Users/juan/Desktop/weathertimes.csv',dates,delimiter=',')
temps = np.genfromtxt(weather_csv,
            delimiter=',',skip_header=1,usecols=1)
humes = np.genfromtxt(weather_csv,
            delimiter=',',skip_header=1,usecols=2)

app = QtGui.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle('Lab Weather')
win.setGeometry(80,80,1000,600)
label = pg.LabelItem(justify='center')
win.addItem(label)

humidity_plot = win.addPlot(row=1, col=0, title='Relative Humidity',
        axisItems = {'bottom': pg.DateAxisItem()})
humidity_plot.showGrid(x=True, y=True)
humidity_plot.setMouseEnabled(y=False,x=False)

humidity_plot.plot(dates, humes, pen='r')
range_ = humidity_plot.getViewBox().viewRange()
humidity_plot.getViewBox().setLimits(xMin=dates[0], xMax=dates[-1])

humidity_plot.setContentsMargins(*(margin,0,margin,0))
humidity_plot.setLabel(axis='left',text='RH/%')

temperature_plot = win.addPlot(row=2, col=0, title='Temperature',
        axisItems = {'bottom': pg.DateAxisItem()})
temperature_plot.showGrid(x=True, y=True)
temperature_plot.setMouseEnabled(y=False)

temperature_plot.plot(dates, temps, pen='g')
range_ = temperature_plot.getViewBox().viewRange()
temperature_plot.getViewBox().setLimits(xMin=dates[0], xMax=dates[-1])
temperature_plot.setContentsMargins(*(margin,0,margin,0))
temperature_plot.setLabel(axis='left',text='T/C')

selector_plot = win.addPlot(row=3, col=0, title='% RH',
        axisItems = {'bottom': pg.DateAxisItem()})
selector_plot.showGrid(x=True, y=True)
selector_plot.setMouseEnabled(y=False)

selector_plot.plot(dates, humes, pen='r')
range_ = selector_plot.getViewBox().viewRange()
selector_plot.getViewBox().setLimits(xMin=dates[0], xMax=dates[-1])
selector_plot.setContentsMargins(*(margin,0,margin,margin))
selector_plot.setLabel(axis='left',text='RH/%')

region = pg.LinearRegionItem()
region.setZValue(10)
selector_plot.addItem(region, ignoreBounds=True)

def update():
    region.setZValue(10)
    minX, maxX = region.getRegion()
    if maxX > dates[-1]:
        region.setRegion([minX, dates[-1]])
    minX, maxX = region.getRegion()
    if minX < dates[0]:
        region.setRegion([dates[0], maxX])
    minX, maxX = region.getRegion()
    for aplot in [temperature_plot, humidity_plot]:
        aplot.setXRange(minX, maxX, padding=0)
    left_timestamp = datetime.fromtimestamp(minX)
    right_timestamp = datetime.fromtimestamp(maxX)
    label_text = '%s -> %s' % (left_timestamp.strftime("%b %d, %Y"), right_timestamp.strftime("%b %d, %Y"))
    label.setText("<span style='font-size: 30pt'>%s<span style='color: red'>" % label_text)

region.sigRegionChanged.connect(update)
region.setRegion([dates[-1] - 7*24*3600,dates[-1]])

if __name__ == '__main__':
    app.exec_()
