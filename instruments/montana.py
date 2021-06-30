#!/usr/bin/env python3
import socket
import sys
import time
from time import sleep
from decimal import Decimal

class Montana:

    def __init__(self, ip, port):
        self.target_platform_stability = 0.04
        self.temperature_stepup_size = 5.00
        self.maximum_platform_stepup_target_temperature = 100.00
        # Time limit for reaching the cooldown platform temperature (seconds):
        self.cooldown_timeout = 18000
        # Time limit for reaching platform stability for cooldown and step-up (seconds)
        self.stability_timeout = 1800
        self.ip = ip
        self.port = port
        self.cryo_conn = CryoComm(ip=ip, port=port)

    def reconnect(self):
        self.cryo_conn = CryoComm(ip=self.ip, port=self.port)

    def set_target_platform_temperature(self, set_point, timeout = 10):
        "Set the target platform temperature."

        print("Set target platform temperature {0}".format(set_point))

        timeout = time.time() + timeout  # Determine timeout

        target_temperature = self.send_target_platform_temperature(set_point)
        print('Target temp:', target_temperature)
        while round(target_temperature, 2) != round(set_point, 2):
            if timeout > 0:
                if time.time() > timeout:  # If we pass the timeout, give up.
                    return False
            sleep(1)
            target_temperature = self.send_target_platform_temperature(self.cryo_conn, set_point)

        return True


    def send_target_platform_temperature(self, set_point):
        "Send the target platform temperature to the Cryostation.  Read it back to verify the set operation"

        print("Send target platform temperature {0}".format(set_point))

        target_temperature_decimal = 0.0
        target_temperature_string = ''

        try:
            if self.cryo_conn.send_command_get_response("STSP" + str(set_point)).startswith("OK"):
                target_temperature_string = self.cryo_conn.send_command_get_response("GTSP")
        except Exception as err:
            print("Failed to send target platform temperature")
            exit(1)
        try:
            target_temperature_decimal = Decimal(target_temperature_string)
        except Exception as err:
            target_temperature_decimal = 0.0
        return target_temperature_decimal

    def initiate_cooldown(self, target_cooldown_temp):
        '''Set the target platform temperature and initiate cooldown.'''
        self.target_cooldown_temp = target_cooldown_temp
        print("Setting the cooldown temperature to %.1f K..." % target_cooldown_temp)
        if not self.set_target_platform_temperature(target_cooldown_temp):
            print("Timed out setting cooldown target platform temperature")
        print("Initiating cooldown...")
        try:
            if self.cryo_conn.send_command_get_response("SCD") != "OK":
                print("Cooldown did not initiate...")
        except Exception as err:
            print("Failed to initiate cooldown...")

    def initiate_warmup(self):
        try:
            if self.cryo_conn.send_command_get_response("SWU") != "OK":
                print("Warmup did not initiate...")
            else:
                print("Initiating warmup...")
        except Exception as err:
            print("Failed to initiate warmup...")

    def get_platform_temperature(self):
        try:
            temp = float(self.cryo_conn.send_command_get_response("GPT"))
        except:
            return False
        self.platform_temp = temp
        return temp

    def get_sample_temperature(self):
        try:
            temp = float(self.cryo_conn.send_command_get_response("GST"))
        except:
            return False
        self.sample_temp = temp
        return temp

    def get_cryoptic_temperature(self):
        try:
            temp = float(self.cryo_conn.send_command_get_response("GUT"))
        except:
            return False
        self.cryoptic_temp = temp
        return temp

    def get_alarm_state(self):
        try:
            alarm_state = (self.cryo_conn.send_command_get_response("GAS"))
        except:
            print("Error found in acquiring alarm state.")
            return False
        self.alarm_state = alarm_state
        return alarm_state

    def get_pressure(self):
        '''
        pressure returned in Pa
        '''
        try:
            pressure = 0.133322*float(self.cryo_conn.send_command_get_response("GCP"))
        except:
            return False
        self.pressure = pressure
        return pressure

    def close(self):
        self.cryo_conn.__del__()

    def get_full_state(self):
        '''
        returns pressure/Pa, platform_temp/K, sample_temp/K, cryoptic_temp/K
        '''
        try:
            self.get_pressure()
            self.get_platform_temperature()
            self.get_sample_temperature()
            self.get_cryoptic_temperature()
            return self.pressure, self.platform_temp, self.sample_temp, self.cryoptic_temp
        except:
            print("Error getting pressure and temperatures...")
            return False

    def wait_for_cooldown_and_stability(self):
        "Wait for the Cryostation system to cooldown and stabilize."

        print("Wait for cooldown temperature")
        if self.cooldown_timeout > 0:  # If cooldown timeout enabled
            cooldown_max_time = time.time() + self.cooldown_timeout  # Determine cooldown timeout
        while True:
            sleep(3)
            if self.cooldown_timeout > 0:
                if time.time() > cooldown_max_time:  # If we pass the cooldown timeout, give up.
                    print("Timed out waiting for cooldown temperature")
                    return False
            try:
                current_temperature = float(self.cryo_conn.send_command_get_response("GPT"))
            except Exception as err:
                current_temperature = 0.0
            # Wait until platform temperature reaches target
            if current_temperature <= self.target_cooldown_temp and current_temperature > 0:
                break

        print("Wait for cooldown stability")
        if self.stability_timeout > 0:  # If stability timeout enabled
            stability_max_time = time.time() + self.stability_timeout  # Determine stability timeout
        while True:
            sleep(3)
            if self.stability_timeout > 0:
                if time.time() > stability_max_time:  # If we pass the stability timeout, give up.
                    print("Timed out waiting for cooldown stability")
                    return False
            try:
                current_stability = float(self.cryo_conn.send_command_get_response("GPS"))
            except Exception as err:
                current_stability = 0.0
            if current_stability <= self.target_platform_stability and current_stability > 0:  # Wait until platform stability reaches target
                return True

class CryoComm:
    "Class to provide python communication with a Cryostation"


    def __init__(self, ip='localhost', port=7773):
        "CryoComm - Constructor"

        self.ip = ip
        self.port = port
        self.socket = None

		# Connect to the Cryostation
        try:
            self.socket = socket.create_connection((ip, port), timeout=10)
        except Exception as err:
            print("CryoComm:Connection error - {}".format(err))
            raise err

        self.socket.settimeout(5)


    def __send(self, message):
        "CryoComm - Send a message to the Cryostation"

        total_sent = 0

        # Prepend the message length to the message.
        message = str(len(message)).zfill(2) + message

		# Send the message
        while total_sent < len(message):
            try:
                sent = self.socket.send(message[total_sent:].encode())
            except Exception as err:
                print("CryoComm:Send communication error - {}".format(err))
                raise err

            # If sent is zero, there is a communication issue
            if sent == 0:
                raise RuntimeError("CryoComm:Cryostation connection lost on send")
            total_sent = total_sent + sent


    def __receive(self):
        "CryoComm - Receive a message from the Cryostation"

        chunks = []
        received = 0

		# Read the message length
        try:
            message_length = int(self.socket.recv(2).decode('UTF8'))
        except Exception as err:
            print("CryoComm:Receive message length communication error - {}".format(err))
            raise err

        # Read the message
        while received < message_length:
            try:
                chunk = self.socket.recv(message_length - received)
            except Exception as err:
                print("CryoComm:Receive communication error - {}".format(err))
                raise err

            # If an empty chunk is read, there is a communication issue
            if chunk == '':
                raise RuntimeError("CryoComm:Cryostation connection lost on receive")
            chunks.append(chunk)
            received += len(chunk)

        return ''.join([x.decode('UTF8') for x in chunks])


    def send_command_get_response(self, message):
        "CryoComm - Send a message to the Cryostation and receive a response"

        self.__send(message)
        return self.__receive()


    def __del__(self):
        "CryoComm - Destructor"

        if self.socket:
            self.socket.shutdown(1)
            self.socket.close()
