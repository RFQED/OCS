import sys # We need sys so that we can pass argv to QApplication
import time
import serial
from fpga_comms import *

try:
    init_fpga_comms()
    set_pulse_width(10)
    turn_all_pulsers_on()
    set_registers()
except:
    print("CONNECTION TO FPGA BOARD COULD NOT BE MADE")




########### 1
########### 20 = on   21 = off
########### 23 
########### 31 = 1khz  35 = 5khz   40 = 10khz    
########### 5 = 5 unit pulse width  10 = 10 unit pulse width
########### 26
########### 27
########### 28
########### 29
########### 22
########### 11

#registers = [1,20,23,35,10,26,27,28,29,22,11]
#sleepTime = 0.25

