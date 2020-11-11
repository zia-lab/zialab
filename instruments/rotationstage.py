#!/usr/bin/env python3

import ctypes

class PRM1Z8():

    '''
    For Thorlabs PRM1Z8 (Motorized Rotation Stage)

    Thorlabs APT Device Type Number:
    TDC001/KDC101 = 31	# 1 Ch DC servo driver T-Cube/K-Cube.

    Serial Number:
    SN 432258
    '''

    def __init__(self, type_num=31):
        '''
        APT type number for the KDC101 motor is 31.
        '''
        self.type_num = ctypes.c_long(type_num)
        self.apt = ctypes.windll.LoadLibrary("D:/Google Drive/Zia Lab/Codebase/zialab/instruments/DLLs/APT.dll")
        self.connected_units = ctypes.c_long(0)
        self.serial_num = ctypes.c_long()
        self.model, self.version, self.notes = ctypes.c_buffer(255), ctypes.c_buffer(255), ctypes.c_buffer(255)
        self.min_pos, self.max_pos, self.pitch = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
        self.min_vel, self.max_vel, self.acceleration = ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
        self.units = ctypes.c_long()
        self.position = ctypes.c_float()

    def open(self, device_id=ctypes.c_long(0), dialogue_flag=False):
        '''
        Initiate the polarizer and get harware information.
        '''
        print("Initiating APT device(s)...\n")
        if self.apt.APTInit() == 0:
            self.apt.EnableEventDlg(dialogue_flag)
            self.apt.GetNumHWUnitsEx(self.type_num, ctypes.pointer(self.connected_units))
            self.apt.GetHWSerialNumEx(self.type_num, device_id, ctypes.pointer(self.serial_num))
            print("{} APT unit(s) with serial number {} is(are) connected.\n".format(self.connected_units.value, self.serial_num.value))
            print("Initializing hardware...\n")
            self.apt.InitHWDevice(self.serial_num)
            self.apt.GetHWInfo(self.serial_num, self.model, 255, self.version, 255, self.notes, 255)
            print("Model: {} \nVersion: {}\nNotes: {}\n".format(self.model.value, self.version.value, self.notes.value))
            self.get_axis_info()
            self.get_velocity_info()
        else:
            raise Exception('No APT device connected.')

    def get_axis_info(self):
        self.apt.MOT_GetStageAxisInfo(self.serial_num, ctypes.pointer(self.min_pos), ctypes.pointer(self.max_pos), ctypes.pointer(self.units), ctypes.pointer(self.pitch))
        print("Minimum Position: {} \nMaximum Position: {}\nUnits: {}\nPitch: {}\n".format(self.min_pos.value, self.max_pos.value, self.units.value, self.pitch.value))

    def get_velocity_info(self):
        self.apt.MOT_GetVelParams(self.serial_num, ctypes.pointer(self.min_vel), ctypes.pointer(self.max_vel), ctypes.pointer(self.acceleration))
        print("Minimum Velocity: {} \nMaximum Velocity: {}\nAcceleration: {}\n".format(self.min_vel.value, self.max_vel.value, self.acceleration.value))

    def qPOS(self):
        self.apt.MOT_GetPosition(self.serial_num, ctypes.pointer(self.position))
        return self.position.value

    def set_vel(self, min_vel, acceleration, max_vel):
        self.apt.MOT_SetVelParams(self.serial_num, min_vel, acceleration, max_vel)

    def move(self, position, type_flag="absolute"):
        if type_flag == "absolute":
            self.apt.MOT_MoveAbsoluteEx(self.serial_num, ctypes.c_float(position), True)

    def home(self):
        self.apt.MOT_MoveHome(self.serial_num)

    def close(self):
        if self.apt.APTCleanUp() == 0:
            print("Device disconnected.")
