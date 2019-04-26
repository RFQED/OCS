###########################################################################
#  minimal OCS Pulser Control script 
#  Will Turner
#  wturner@FNAL.GOV
#
#    VER2 firmware comms, byte layout is currently 
#   must start with 1
#   Byte 0    does nothing
#   Byte 1    veto (does nothing)
#   Byte 2    increment/decrement (does nothing)
#   Byte 3    Photodiode channel select 000 to 111
#   Byte 4    big steps 
#   Byte 5    small steps
#   Byte 6    select pulser to fire 00000000 = fire none   11111111 = fire all etc
#   Byte 7    not used
#   Byte 8    not used
#   must end with 11
###########################################################################

import sys # We need sys so that we can pass argv to QApplication
import time
import serial

global sleepTime
sleepTime = 0.025

#            0  1 2  3  4 5  6  7  8  9  10
register = [1,22,23,35,5,26,255,28,29,22,11]
#register = [1,22,23,35,5,26,27,28,29,22,11]

def print_commands():
    print("init_fpga_comms \n print_register \n turn_all_pulsers_on \n turn_all_pulsers_off \n set_pulse_freq \n set_register \n quick_off")

def init_fpga_comms():
    # should search for USB with the correct serial number to find the correct port, use: $ /dev/cu.usb*
    global ser
    try:
#        ser = serial.Serial(port='/dev/cu.usbserial-DN17Y0J9', baudrate=9600)    # OLD GREEN BOARD
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5SR', baudrate=9600)    # FPGA01
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5ST', baudrate=9600)    # FPGA02   --> FPGA06
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5SS', baudrate=9600)    # FPGA03
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E3LM', baudrate=9600)    # FPGA04
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03BM8R', baudrate=9600)    # FPGA05
        ser = serial.Serial(port='/dev/cu.usbserial-DN03E3LL', baudrate=9600)    # FPGA06  --> FPGA02

        print("Connected")

    except:
        print("CONNECTION TO FPGA BOARD COULD NOT BE MADE")


def print_register():
    global register
    for i in range(0, len(register)):
        print(register[i])


    # REGISTER 1 = Pulses ON/OFF
#def turn_on_pulsers():
def turn_all_pulsers_on():
    # if pulses  ON = 20  OFF = 21
    global register
    register[1] = int(20)

#def turn_off_pulsers():
def turn_all_pulsers_off():
    # if pulses  ON = 20  OFF = 21
    global register
    register[1] = int(255)

# need to write code to do binary comparisons to turn off/on indiv chs
#def turn_off_ch(x):


#def set_pulse_freq(freq):
#    global register
#    register[3]= int(30+freq)

def set_PD_readback_ch(PDCH): # Byte 3
    if (PDCH == 0):
        # byte value to send 000
        register[3] = int(31)
        print("Selected CH0")
    elif (PDCH == 1):
        # byte value to send 001
        register[3] = int(32)
        print("Selected CH1")
    elif (PDCH == 2):
        # byte value to send 010
        register[3] = int(33)
        print("Selected CH2")
    elif (PDCH == 3):
        # byte value to send 011
        register[3] = int(34)
        print("Selected CH3")
    elif (PDCH == 4):
        # byte value to send 100
        register[3] = int(35)
        print("Selected CH4")
    elif (PDCH == 5):
        # byte value to send 101
        register[3] = int(36)
        print("Selected CH5")
    elif (PDCH == 6):
        # byte value to send 110
        register[3] = int(37)
        print("Selected CH6")
    elif (PDCH == 7):
        # byte value to send 111
        register[3] = int(38)
        print("Selected CH7")
    else:
        print("PD Selection out of range 0 - 7")

#def read_PD_ch(PDCH):
    #write code here
    
    
def set_pulse_width_large(width):
    if (width < 50 and width >= 10):
        global register
        register[4]= int(width)
    else:
        print("error setting width")

def set_pulse_width_small(width):
    if (width < 64 and width >= 0):
        global register
        register[5]= int(width)
    else:
        print("error setting width")

def set_registers():
    print("Setting Registers")
    global register
    try:
        for i in range(0, len(register)):
            ser.write(chr(register[i]))
            time.sleep(sleepTime)
    except:
        print("Could not send command. Port closed?")
    
def quick_off():
    init_fpga_comms()
    turn_all_pulsers_off()
    set_registers()
