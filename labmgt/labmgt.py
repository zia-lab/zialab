import time
import pickle
import os

logdirs = ['/Users/juan/Google Drive/Zia Lab/Log/']
for i in range(len(logdirs)):
	print(str(i)+'. '+logdirs[i])
print(str(len(logdirs))+'. '+'other')
choicedir = int(input('Choose: '))
if choicedir == len(logdirs):
    while True:
        logdir = input('Enter path:')
        if os.path.isdir(logdir):
            break
        print('Directory does not exist in this computer. Please enter a valid one.')
else:
	logdir = logdirs[choicedir]
if not(os.path.isdir(logdir)):
    print('Directory does not exist in this computer')
	
def loggraph():
	"""Save a graph to the log in Google Drive in both png and pdf formats."""
	timestamp = int(time.time())
	pngfigname = logdir+'graphs/plot'+str(timestamp)+'.png'
	pdffigname = logdir+'graphs/plot'+str(timestamp)+'.pdf'
	print(pngfigname)
	print(pdffigname)
	plt.savefig(pngfigname, dpi=300)
	plt.savefig(pdffigname)
def logdata(description, data):
	"""Save data to a pickle located in the Google Drive log."""
	timestamp = int(time.time())
	picklename = logdir+'data/data'+str(timestamp)+'.pickle'
	pickle.dump([description, data], open(picklename,'wb'))
	print('File saved succesfully to '+picklename+'.')
