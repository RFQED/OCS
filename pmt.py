import math
import time
from constants import *
from config import *
import DRS4Wrapper
import sys
import serial


# OLD 
#time_PMT_settle     =  10.0    # settling time after HV change 

#TESTING
time_PMT_settle     =  10   # settling time after HV change 

def init_pmt():
    # try setting up comms to arduino
    # make this global so funcs below can see it
    global arduino
#    arduino = serial.Serial('/dev/tty.usbserial', 9600)  # LINUX
    arduino = serial.Serial('/dev/cu.usbmodem141121', 9600)  # MACBOOK

    print('[DRS]     Setting up DRS4.')

    global drs
    drs = DRS4Wrapper.DRS4Wrapper()

    if not drs.initBoard():
        raise Exception

    # For triggering off PMT pulse
    drs.SetTriggerChannel(1)
    drs.SetTriggerPolarity(0)
    print('DRS Freq: %g', drs.GetFrequency())


def get_record2():
    global drs
    return drs.record2()

def get_measure_peak_time(ch):
    global drs
    return drs.measurePeakTime(ch)

def get_measure_pos_width(ch):
    global drs
    return drs.measurePosWidth(ch)

def get_measure_neg_width(ch):
    global drs
    return drs.measureNegWidth(ch)

def get_measure_level(ch):
    global drs
    return drs.measureLevel(ch)

def get_measure_peak(ch):
    global drs
    return drs.measurePeak(ch)

def get_measure_charge1(lowBnd1, highBnd1):
    global drs
    return drs.measureCharge(1,lowBnd1, highBnd1)

def get_measure_charge2(lowBnd2, highBnd2):
    global drs
    return drs.measureCharge(2,lowBnd2, highBnd2)

def get_measure_integral1(lowBnd1, highBnd1):
    global drs
    return drs.measureIntegral(1,lowBnd1, highBnd1)

def get_measure_integral2(lowBnd2, highBnd2):
    global drs
    return drs.measureIntegral(2,lowBnd2, highBnd2)

def calc_pmt_ctrl(nphotons):
#    v_pmt_ctrl = (math.log(nphotons) + 12.0) / 11.5    #  from old calibration
#    v_pmt_ctrl = 2.1498*(nphotons**-0.096)                #  from updated calibration

    mod_nphotons = math.sqrt(nphotons**2)

    if (front_side == True):
#        v_pmt_ctrl = 1.834088*((nphotons*1.6)**-0.08921)                #  from updated calibration
#        v_pmt_ctrl = 1.834088*((nphotons*1.6)**-0.08921)*0.9                #  from updated calibration  (try 80% as it seems too high)
#        v_pmt_ctrl = 1.38*((mod_nphotons*1.6)**-0.0779)*0.9
        v_pmt_ctrl = 1.31*((nphotons)**-0.0724)  # UPDATED BY HARVEY

    if (rear_side == True):
#        v_pmt_ctrl = 2.1498*((nphotons*3.5)**-0.096)                #  from updated calibration
#        v_pmt_ctrl = 2.1498*((nphotons*3.5)**-0.096)*0.9                #  from updated calibration
#        v_pmt_ctrl = 1.45*((mod_nphotons*3.5)**-0.0812)*0.9
        v_pmt_ctrl = 1.38*((nphotons)**-0.0796) #UPDATED BY HARVEY

    v_pmt_ctrl = min(v_pmt_ctrl,1.1)                    #  enforce a maximum 
    v_pmt_ctrl = max(v_pmt_ctrl,0.50)                   #  enforce a minimum 
    return(v_pmt_ctrl)

def set_pmt_control_v(v_pmt_ctrl):
    # get the global serial comms
    # send the voltage to be set as a float
    global arduino

    v_pmt_ctrl = round(v_pmt_ctrl,3)

    arduino.write(b'%r' % v_pmt_ctrl)
    print("Control Voltage Being Set = " + str(v_pmt_ctrl))


def check_pmt_amp():
    if -400 <= get_measure_peak(2) <= -100:
        return(True)
    else:
        print("Measured peak is out of range at " + str(get_measure_peak(2)))
        return(False)


def setup_pmt( photons  ) :  # set the pmt control voltage [V]
    time.sleep(time_PMT_settle)                 # avoid switch on spike and PMT settling time 
    set_pmt_control_v(calc_pmt_ctrl(photons))

    global pmt
    data2 = drs.record2()

    peakVolt2=(drs.measurePeak(2))
    print("PeakVoltage2 = " + str(peakVolt2) )
    peakAmp2=float(peakVolt2)
    print("PeakAmp2 = " + str(peakAmp2) )


    if (peakAmp2 < -50 and peakAmp2 > -450) :
        print "PMT passed"
        pass
    else :
        print("PMT NOT IN CORRECT RANGE " + str(peakAmp2))
        dirChange = 1
        if peakAmp2 < -450 :
            dirChange = -1
        pmtStep = 0.05
        while (peakAmp2 < -450 or peakAmp2 > -50) :
            v_pmt_ctrl=v_pmt_ctrl+pmtStep*dirChange    
            set_pmt_control_v(v_pmt_ctrl)
            time.sleep(time_PMT_settle)                 # avoid switch on spike and PMT settling time 

            data2 = drs.record2()
            peakVolt2=float(drs.measurePeak(2))
            peakAmp2 = peakVolt2
            print "Test: in ctrl voltage loop. Current value = ", peakVolt2
            print "Test: V_ctrl = ", v_pmt_ctrl
            if (v_pmt_ctrl < 0.5 or v_pmt_ctrl > 1.0) :
                v_pmt_ctrl = v_pmt_ctrl - pmtStep*dirChange*0.5
                break

    pmt_gain   = 1
    pmt_v_ctrl = float(v_pmt_ctrl)
