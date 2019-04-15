# set trigger width
# scan over control voltage from 0.5 to 1
    # recording num photons from power meter. 
    # find control voltage which gets the peak at 250mV   (RANGE IS FROM +0.5  to   -0.5  )
    # plot nph vs Vcontrol


import sys
import time
import string
import threading
from array import *
import math
import scipy.constants as sc
import ROOT

from fpga_comms import *
from constants import *
from powermeter import *
from pmt import *
from fpga_comms import *
from config import *


init_fpga_comms()
turn_all_pulsers_off()
set_registers()

setup_power_meter()

init_pmt()

sleepTime = 5

def get_nphot():
    turn_all_pulsers_off()
    set_registers()
    p3_off = get_p3()
    
    time.sleep(2)
    turn_all_pulsers_on()
    set_registers()

    p3_on = get_p3()     
    p3_value =          ( p3_on["photons"]  - p3_off["photons"]  )   
    p3_error = math.sqrt( p3_on["error"]**2 + p3_off["error"]**2 )   
    nphot = max(p3_value,1)
    return(nphot)
    

# loop over control voltage
def get_250mv_control_v():
    foundVoltage = 0
    for i in range(50, 105, 2):
        #set voltage
        set_pmt_control_v(i/100.0)
        time.sleep(sleepTime)

        # get number of photons from power meter
        data2 = get_record2()
        Amp2=abs(get_measure_peak(2))
        
        print("Amplitude found = " + str(Amp2) + " at control voltage " + str(i/100.0)  )
    
        if (Amp2 > 275):
            foundVoltage = i/100.0
            break

    if (foundVoltage == 0):
        foundVoltage = 1
    
    return(foundVoltage)


print("Starting Scan")

for i in range(0,len(calibrationSetPoints)):
    print("Setting pulse width to " + str(calibrationSetPoints[i]))
    
    turn_all_pulsers_on()
    set_pulse_width(calibrationSetPoints[i])
    set_registers()
    
    nphot = get_nphot()
    
    voltage_at_250mv = get_250mv_control_v()
    print("nphot " + str(nphot) + " ctrl voltage at amp closest to 250mv " + str(voltage_at_250mv))



