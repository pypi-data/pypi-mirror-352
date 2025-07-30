import time
import math
from typing import Union, List
from deprecated import deprecated

import serial

from surveytools import *

from geocom import TCException, AtmosphericCorrectionData
from geocom.enums import LeicaReturnCode, EDMMeasurementMode, OnOffType, TMCMeasurementMode, \
    TMCInclinationSensorMeasurementProgram, PositionMode, ATRMode, FineAdjustPositionMode, FaceDef

RHO = 200 / math.pi

class TotalStation(object):

    def __init__(self, serialPortCOM, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, timeout=1, stopbits=1):
        self.last_return_code = LeicaReturnCode.GRC_OK
        self.waiting_instrument = 0
        self.serialPort = serial.Serial(port=serialPortCOM, baudrate=baudrate,
                                        bytesize=bytesize, parity=parity,
                                        timeout=timeout, stopbits=stopbits)

    def read_data_from_port(self) -> List[Union[LeicaReturnCode, str]]:
        time_wait = 0.5
        time_count = 0

        while True:
            time_count += time_wait
            if self.serialPort.inWaiting() > 0:
                out = self.serialPort.readline()
                print("read_data_from_port: " + str(out))
                out = out.decode("utf-8").rstrip()
                test = out[0:4]
                if out[0:4] == "%R1P":
                    out = out.split(":")
                    # out[0] protocol header
                    # out[1] following parameters
                    param = out[1].split(",")

                    # Set Enum vor Leica Return
                    param[0] = LeicaReturnCode(int(param[0]))
                    self.last_return_code = param[0]
                    self.waiting_instrument = 0
                    return param
            if time_count > 30:
                self.waiting_instrument = 0
                raise TCException(LeicaReturnCode.GRC_AUT_TIMEOUT)
            time.sleep(time_wait)

    def request(self, command: str) -> List[Union[LeicaReturnCode, str]]:
        send_commad = (command + "\r\n").encode()

        if self.waiting_instrument == 1:
            print("Wait... ")
            time.sleep(10)

        print("Send: " + str(send_commad))
        self.waiting_instrument = 1

        self.serialPort.write(send_commad)
        time_wait = 0.5
        time_count = 0

        return self.read_data_from_port()

    def get_edm_mode(self) -> EDMMeasurementMode:
        response = self.request("%R1Q,2021:")
        return EDMMeasurementMode(int(response[1]))

    def set_edm_mode(self, edm: EDMMeasurementMode) -> LeicaReturnCode:
        response = self.request('%R1Q,2020:{0}'.format(edm.value))
        return response[0]

    def get_atm_correction(self) -> 'AtmosphericCorrectionData':
        response = self.request("%R1Q,2029:")
        return AtmosphericCorrectionData(float(response[1]), float(response[2]), float(response[3]), float(response[4]))

    def set_atm_correction(self, atm: 'AtmosphericCorrectionData') -> LeicaReturnCode:
        response = self.request("%R1Q,2028:" + str(atm))
        return response[0]

    def get_incline_switch(self):
        response = self.request("%R1Q,2007:")
        return OnOffType(int(response[1]))

    def set_incline_switch(self, state: OnOffType):
        response = self.request('%R1Q,2006:{0}'.format(state.value))
        return response[0]

    def edm_laserpointer(self, state: OnOffType):
        response = self.request('%R1Q,1004:{0}'.format(state.value))
        return response[0]

    def get_prism_constant(self) -> float:
        response = self.request("%R1Q,2023:")
        return float(response[1])

    def wake_up(self):
        self.serialPort.write(b'%R1Q,18006:\r\n')
        time.sleep(30)
        self.serialPort.flushInput()

    def turn_off(self):
        response = self.request("%R1Q,112:0")
        return response[0]

    def get_instrument_name(self) -> str:
        response = self.request("%R1Q,5004:")
        return response[1]

    def get_software_version(self):
        response = self.request("%R1Q,5034:")
        return SWVersion(int(response[1]), int(response[2]), int(response[3]))

    def get_instrument_number(self) -> int:
        response = self.request("%R1Q,5003:")
        return int(response[1])

    def do_measure(self, command: TMCMeasurementMode, mode: TMCInclinationSensorMeasurementProgram) -> LeicaReturnCode:
        response = self.request("%R1Q,2008:{0},{1}".format(command.value, mode.value))
        return response[0]

    def get_simple_measurement(self, wait_time: int, mode: TMCInclinationSensorMeasurementProgram,
                               target_nr: str, atmospheric_data, measure_time) -> 'Measurement':

        response = self.request("%R1Q,2108:{0},{1}".format(wait_time, mode.value))

        if response[0] == LeicaReturnCode.GRC_OK:
            return Measurement(target_nr, Angle(float(response[1])), Angle(float(response[2])), float(response[3]), atmospheric_data, measure_time)
        else:
            return Measurement(target_nr, Angle(0), Angle(0), 0, atmospheric_data, measure_time)

    def search_target(self) -> LeicaReturnCode:
        response = self.request("%R1Q,17020:0")
        return response[0]

    def get_internal_temperature(self) -> int:
        response = self.request("%R1Q,5011:")
        return int(response[1])

    def set_user_atr_state(self, state: OnOffType) -> LeicaReturnCode:
        response = self.request("%R1Q,18005:{0}".format(state.value))
        return response[0]

    def set_telescope_position(self, direction: Angle, zenith: Angle, pos_mode: PositionMode, atr_mode: ATRMode) -> LeicaReturnCode:
        response = self.request("%R1Q,9027:{0},{1},{2},{3},0".format(direction.value_rad, zenith.value_rad, pos_mode.value, atr_mode.value))
        return response[0]

    def set_telescope_to_second_face(self, pos_mode: PositionMode, atr_mode: ATRMode) -> LeicaReturnCode:
        response = self.request("%R1Q,9028:{0},{1},0".format(pos_mode.value, atr_mode.value))
        return response[0]

    def fine_adjust(self, hz_area: Angle, v_area: Angle):
        response = self.request("%R1Q,9037:{0},{1},0".format(hz_area.value_rad, v_area.value_rad))
        return response[0]

    def get_fine_adjust_mode(self) -> FineAdjustPositionMode:
        response = self.request("%R1Q,9030:")
        return FineAdjustPositionMode(int(response[1]))

    def set_fine_adjust_mode(self, adj_mode: FineAdjustPositionMode) -> LeicaReturnCode:
        response = self.request("%R1Q,9031:{0}".format(adj_mode.value))
        return response[0]

    @deprecated(reason="Use get_angle1() instead.")
    def get_angle_complete(self, mode: TMCInclinationSensorMeasurementProgram) -> FullAngleMeasurement:
        return self.get_angle1(mode)

    def get_angle1(self, mode: TMCInclinationSensorMeasurementProgram) -> FullAngleMeasurement:
        response = self.request("%R1Q,2003:{0}".format(mode.value))
        a = FullAngleMeasurement()

        a.hz = Angle(float(response[1]))
        a.v = Angle(float(response[2]))
        a.angle_accuracy = Angle(float(response[3]))
        a.angle_time = int(response[4])
        a.cross_incline = Angle(float(response[5]))
        a.length_incline = Angle(float(response[6]))
        a.accuracy_incline = Angle(float(response[7]))
        a.incline_time = int(response[8])
        a.face_def = FaceDef(int(response[9]))

        return a

    def measure(self, target_nr: str, atmo, measure_time):
        self.do_measure(TMCMeasurementMode.TMC_DEF_DIST, TMCInclinationSensorMeasurementProgram.TMC_AUTO_INC)

        for _ in range(1, 8):
            time.sleep(1)
            m = self.get_simple_measurement(30, TMCInclinationSensorMeasurementProgram.TMC_AUTO_INC, target_nr, atmo, measure_time)
            if m.slope_distances > 0:
                return m

        self.do_measure(TMCMeasurementMode.TMC_DEF_DIST, TMCInclinationSensorMeasurementProgram.TMC_AUTO_INC)
        time.sleep(20)
        return self.get_simple_measurement(30, TMCInclinationSensorMeasurementProgram.TMC_AUTO_INC, target_nr, atmo, measure_time)

