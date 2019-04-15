import sys
import serial
import re

ser = serial.Serial(port='/dev/cu.usbmodem14121', baudrate=9600)
print("connected to PD")
PDCh1 = ser.readline()
PDCh1 = re.sub('[^0-9\.]','', PDCh1)
print("read out CH1 " + PDCh1)

PDCh1 = ser.readline()
PDCh1 = re.sub('[^0-9\.]','', PDCh1)
print("read out CH1 " + PDCh1)

PDCh1 = ser.readline()
PDCh1 = re.sub('[^0-9\.]','', PDCh1)
print("read out CH1 " + PDCh1)

PDCh1 = ser.readline()
PDCh1 = re.sub('[^0-9\.]','', PDCh1)
print("read out CH1 " + PDCh1)


