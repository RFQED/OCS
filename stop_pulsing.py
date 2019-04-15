import sys
import time
import serial
from fpga_comms import *

try:
    quick_off()
except:
    print("CONNECTION TO FPGA BOARD COULD NOT BE MADE")


