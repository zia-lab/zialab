from ctypes import cdll, c_int, c_uint, c_double
import atexit # The atexit module defines functions to register and unregister cleanup functions
from time import sleep
import sys

# ╔═══════════════════════╗
# ║   __  __  ____ _      ║
# ║  |  \/  |/ ___| |     ║
# ║  | |\/| | |   | |     ║
# ║  | |  | | |___| |___  ║
# ║  |_|  |_|\____|_____| ║
# ║                       ║
# ║    mad city labs      ║
# ╚═══════════════════════╝

# Created by David on July 17 2019
# based on https://github.com/yurmor/mclpiezo/

global default_path_to_dll
global mcl_notes
default_path_to_dll = r'C:\Program Files\Mad City Labs\NanoDrive\Madlib.dll'
mcl_notes = '''
+ Big rangy goes 300 um on all axes.
+ Small rangy goes 100 um on all axes.
'''

class Madpiezo():
	def __init__(self):
        self.platform = sys.platform
        self.notes = mcl_notes
        print(self.notes)
        assert self.platform == 'win32', "Only runs on Windows."
		# provide valid path to Madlib.dll. Madlib.h and Madlib.lib should also be in the same folder
        print("path to dll: %s" % default_path_to_dll)
        path_to_dll = input("press enter to keep, type to change: ")
        if path_to_dll == '': path_to_dll = default_path_to_dll
        self.shortname = 'MCL stage'
        self.fullname = 'MCL - Nano-LP100'
        self.manual_fname = './zialab/Manuals/'+self.fullname + '.pdf'
		self.madlib = cdll.LoadLibrary(path_to_dll)
		self.handler = self.mcl_start()
		atexit.register(self.mcl_close)
    def manual(self):
        '''open the pdf manual'''
        platform_open_cmds = {'linux':'xdg-open','darwin':'open'}
        try:
            print("Opening the manual.")
            os.system('%s "%s"' % (platform_open_cmds[self.platform],self.manual_fname))
        except:
            print("wups, could not open")
	def mcl_start(self):
		"""
		Requests control of a single Mad City Labs Nano-Drive.
		Return Value:
			Returns a valid handle or returns 0 to indicate failure.
		"""
		mcl_init_handle = self.madlib['MCL_InitHandle']

		mcl_init_handle.restype = c_int
		handler = mcl_init_handle()
		if(handler==0):
			print("MCL init error")
			return -1
		return 	handler
	def mcl_read(self,axis_number):
		"""
		Read the current position of the specified axis.
		Parameters:
			axis [IN] Which axis to move. (X=1,Y=2,Z=3,AUX=4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns a position value or the appropriate error code.
		"""
		mcl_single_read_n = self.madlib['MCL_SingleReadN']
		mcl_single_read_n.restype = c_double
		return  mcl_single_read_n(c_uint(axis_number), c_int(self.handler))
	def mcl_write(self,position, axis_number):
		"""
		Commands the Nano-Drive to move the specified axis to a position.
		Parameters:
			position [IN] Commanded position in microns.
			axis [IN] Which axis to move. (X=1,Y=2,Z=3,AUX=4)
			handle [IN] Specifies which Nano-Drive to communicate with.
		Return Value:
			Returns MCL_SUCCESS or the appropriate error code.
		"""
		mcl_single_write_n = self.madlib['MCL_SingleWriteN']
		mcl_single_write_n.restype = c_int
		error_code = mcl_single_write_n(c_double(position), c_uint(axis_number), c_int(self.handler))

		if(error_code !=0):
			print("MCL write error = ", error_code)
		return error_code
	def goxy(self,x_position,y_position):
		self.mcl_write(x_position,1)
		self.mcl_write(y_position,2)
	def goz(self,z_position):
		self.mcl_write(z_position,3)
	def get_position(self):
		return self.mcl_read(1), self.mcl_read(2), self.mcl_read(3)
	def mcl_close(self):
		"""
		Releases control of all Nano-Drives controlled by this instance of the DLL.
		"""
		mcl_release_all = self.madlib['MCL_ReleaseAllHandles']
		mcl_release_all()
