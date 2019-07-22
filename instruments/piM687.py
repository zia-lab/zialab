# Coded by Yang Wang circa 2019
# Yet to be made compatible with python3.

import pyPICommands as gcs
import time

class M687():
    pi = gcs.pyPICommands("PI_GCS2_DLL_x64.dll", "PI_")

    def __init__(self):
        pass

    # write any of the allowed gcs commands to the controller.
    def gcs_cmd(self, cmd):
        self.pi.GcsCommandset(cmd)

    # establish connection to the stage by connecting through a virtual serial port(usb masked as RS232) with specific baunt rate.
    #       it also performs a maintanence run(moving both x and y for 10mm) to spread out the lubricant and achieve optimal performance.
    def open(self):
        if self.pi.ConnectRS232(13, 115200) == True:
            print('M687:\nStage is CONNECTED.')
            # print('Checking servo states and reference modes...')
            self.gcs_cmd('SVO x 1')
            time.sleep(0.1)
            self.gcs_cmd('SVO y 1')
            # print('servo states: ON.')
            self.gcs_cmd('RON x 1')
            time.sleep(0.1)
            self.gcs_cmd('RON y 1')
            time.sleep(0.1)
            print('reference mode: REFERENCED.')
            # self.gcs_cmd('VEL x 1')
            # time.sleep(0.1)
            # self.gcs_cmd('VEL y 1')
            time.sleep(0.1)
            print('Stage is performing a maintenance run....')
            self.move_x(5)
            time.sleep(1)
            self.move_x(-5)
            time.sleep(1)
            self.move_x(0)
            time.sleep(1)
            self.move_y(5)
            time.sleep(1)
            self.move_y(-5)
            time.sleep(1)
            self.move_y(0)
            print('Maintanence run finished. Stage is now READY.\n')
        else:
            raise TypeError('Stage was not found.')

    # close the connection with the stage.
    def close(self):
        self.pi.CloseConnection()
        print('M687:\nStage is DISCONNECTED.\n')

    # get the answer string of any gcs command that were sent to the stage. (e.g. returns the velocity if one used a command to query the velocity)
    def gcs_answer(self):
        answer = ''
        answer_size = self.pi.GcsGetAnswerSize()
        while answer_size != '':
            answer += self.pi.GcsGetAnswer()
            answer_size = self.pi.GcsGetAnswerSize()
        return answer

    # determines whether either of the axes have reached target position for at least a pre-set amount of the settling time.
    def is_on_target(self, axis):
        self.pi.GcsCommandset('ONT? ' + axis)
        if self.pi.GcsGetAnswer()[2] == '1':
            return True
        else:
            return False

    # query both x and y positions of the stage.
    def qPOS(self):
        self.pi.GcsCommandset(chr(5))
        while self.pi.GcsGetAnswer() == '1':
            pass
        position = self.pi.qPOS('x y')
        return [position['x'], position['y']]

    # move the stage in the x-axis.
    def move_x(self, x):
        t0_x = time.time()
        self.pi.GcsCommandset('MOV x ' + str(x))
        while not (self.is_on_target('x')) and (time.time() - t0_x < 10):
            pass

    # move the stage in the y-axis.
    def move_y(self, y):
        t0_y = time.time()
        self.pi.GcsCommandset('MOV y ' + str(y))
        while not self.is_on_target('y') and (time.time() - t0_y < 10):
            pass

    # configure the CTO setting so that the stage sends out trigger signals with a specific trigger step size, range, velocity etc.)
    def setCTO(self, StartThreshold, StopThreshold, velocity, TriggerStep, Axis='x', Polarity=1,
               TriggerMode=0):  # Configure the CTO
        self.gcs_cmd('TRO 2 1')
        self.gcs_cmd('CTO 2 1 ' + str(TriggerStep))
        self.gcs_cmd('CTO 2 2 ' + Axis)
        self.gcs_cmd('CTO 2 3 ' + str(TriggerMode))
        self.gcs_cmd('CTO 2 8 ' + str(StartThreshold))
        self.gcs_cmd('CTO 2 9 ' + str(StopThreshold))
        self.gcs_cmd('CTO 2 10 ' + str(StartThreshold))
        self.gcs_cmd('VEL x ' + str(velocity))
        self.gcs_cmd('VEL y ' + str(velocity))

    # turn on the TRO trigger output channel 2 on the controller.
    def TRO_ON(self):
        self.gcs_cmd('TRO 2 1')

    # turn off the TRO trigger output channel 2 on the controller.
    def TRO_OFF(self):
        self.gcs_cmd('TRO 2 0')

    # set the velocity of the stage.
    def setvel(self, v_x, v_y):  # Set the velocity of the stage
        self.gcs_cmd('VEL x ' + str(v_x))
        self.gcs_cmd('VEL y ' + str(v_y))
