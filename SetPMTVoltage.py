from pmt import *

try:
    init_pmt()
except:
    print("\n failure to set up pmt \n ")
    sys.exit(0)

set_pmt_control_v(1) #range 0.5V to 1V
