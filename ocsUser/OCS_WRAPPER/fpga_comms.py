###########################################################################
#  minimal OCS Pulser Control script 
#  Will Turner
#  wturner@FNAL.GOV
###########################################################################

import sys # We need sys so that we can pass argv to QApplication
import time
import serial

global sleepTime
sleepTime = 0.025


# POS 0 = Always 1
# POS 1 = 20 == ON    21 == OFF
# POS 2 = Fine Inc. Scan  (not currently used) 
# POS 3 = Pulse Freq  (31 = 1 kHz     40 = 10 kHz)
# POS 4 = Pulse Width (5 = 5ns pulse width... )
# POS 5 = 26  NULL Behaviour
# POS 6 = 27  NULL Behaviour 
# POS 7 = 28  NULL Behaviour
# POS 8 = 29  NULL Behaviour
# POS 9 = 22  NULL Behaviour
# POS 10 = 11  NULL Behaviour

registers = [1,20,23,35,5,26,27,28,29,22,11]

def print_commands():
    print("init_fpga_comms \n print_registers \n turn_on_pulsers \n turn_off_pulsers \n set_pulse_freq \n set_registers \n quick_off")

def init_fpga_comms():
    # should search for USB with the correct serial number to find the correct port
    global ser
    try:

#        ser = serial.Serial(port='/dev/cu.usbserial-DN17Y0J9', baudrate=9600)    # OLD GREEN BOARD
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5SR', baudrate=9600)    # FPGA01
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5ST', baudrate=9600)    # FPGA02   --> FPGA06
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E5SS', baudrate=9600)    # FPGA03
        ser = serial.Serial(port='/dev/ttyUSB0', baudrate=9600)    # FPGA03
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E3LM', baudrate=9600)    # FPGA04
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03BM8R', baudrate=9600)    # FPGA05
#        ser = serial.Serial(port='/dev/cu.usbserial-DN03E3LL', baudrate=9600)    # FPGA06  --> FPGA02

        print("Connected")              # FPGA03

    except:
        print("CONNECTION TO FPGA BOARD COULD NOT BE MADE")


def print_registers():
    global registers
    for i in range(0, len(registers)):
        print(registers[i])


    # REGISTER 1 = Pulses ON/OFF
def turn_on_pulsers():
    # if pulses  ON = 20  OFF = 21
    global registers
    registers[1] = int(20)

def turn_off_pulsers():
    # if pulses  ON = 20  OFF = 21
    global registers
    registers[1] = int(21)


def set_pulse_freq(freq):
    global registers
    registers[3]= int(30+freq)


def set_pulse_width(width):
    if (width < 50 and width >3):
        global registers
        registers[4]= int(width)
    else:
        print("error setting width")

def set_registers():
    print("Setting Registers")
    global registers
    try:
        for i in range(0, len(registers)):
            ser.write(chr(registers[i]))
            time.sleep(sleepTime)
    except:
        print("Could not send command. Port closed?")
    
def quick_off():
    init_fpga_comms()
    turn_off_pulsers()
    set_registers()
