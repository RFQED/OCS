import time
import serial
from fpga_comms import *

#try:
init_fpga_comms()
set_PD_readback_ch(3)
set_registers()
#except:
#   print("CONNECTION TO FPGA BOARD COULD NOT BE MADE")


