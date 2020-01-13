###########################################################################
#  OCS Pulser Control GUI
#  Will Turner
#  wturner@FNAL.GOV
#
# from Java -> serialPort.setSerialPortParams(9600,SerialPort.DATABITS_8,SerialPort.STOPBITS_1,SerialPort.PARITY_NONE);
###########################################################################
import sys # We need sys so that we can pass argv to QApplication
import time
import serial

#ser = serial.Serial('/dev/ttyO1')  # open serial port
ser = serial.Serial('/dev/ttyUSB0')  # open serial port

sleepTime = 0.25


ser.write("\x01")
time.sleep(sleepTime)
ser.write("\x14")
time.sleep(sleepTime)
ser.write("\x17")
time.sleep(sleepTime)
ser.write("\x28")
time.sleep(sleepTime)
ser.write("\x32")
time.sleep(sleepTime)
ser.write("\x1A")
time.sleep(sleepTime)
ser.write("\x1B")
time.sleep(sleepTime)
ser.write("\x1C")
time.sleep(sleepTime)
ser.write("\x1D")
time.sleep(sleepTime)
ser.write("\x16")
time.sleep(sleepTime)
ser.write("\x0B")
