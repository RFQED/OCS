import sys
import time
from constants import *
from config import *
import visa
import numpy as np

rm = visa.ResourceManager()

def setup_power_meter():

    print 
    print "Info: Selected wavelength   [nm] : ",wavelength_nm  
    print "Info: Selected pulse period [ms] : ",1e-3/rate  
    print 
    print rm.list_resources()

    global power_meter 
    power_meter = rm.open_resource("USB0::0x1313::0x8072::P2006380::0") # Liverpool LZ
    power_meter.write("*RST")

    print "Info: Instrument ID:",   power_meter.query("*IDN?").rstrip()
    print "Info: Self test status:",power_meter.ask("*TST?").rstrip()
    print "Info: System version: ", power_meter.ask("SYSTEM:VERSION?").rstrip()

    response = power_meter.ask("SYSTEM:SENSOR:IDN?"); 
    list = response.split(","); 
    print "Info: Sensor ID is ",list[0];
    power_meter.write("CONFIGURE:SCALAR:TEMPERATURE")
    temperature = float(power_meter.ask("READ?"))
    print "Info: Sensor temperature is %.1f Celsius" % temperature      
    power_meter.write("CONFIGURE:SCALAR:POWER")
    power_meter.write("POWER:DC:UNIT W")
    print "Info: Unit for DC power is now : ",power_meter.ask("POWER:DC:UNIT?").rstrip()
    power_meter.write("SENSE:CORRECTION:WAVELENGTH "+str(int(wavelength_nm))) 
    nm = float(power_meter.ask("SENSE:CORRECTION:WAVELENGTH?")) 
    print "Info: Wavelength now set to [nm]: ",int(nm)    
    power_meter.write("SENSE:AVERAGE:COUNT 3000")  
    counts = int(power_meter.ask("SENSE:AVERAGE:COUNT?")) 
    print "Info: Samples per average pre zero adjustment: ",int(counts)
    print "Info: Configuration is set to : ", power_meter.ask("CONFIGURE?").rstrip()
    print "Info: Power auto range status : ", power_meter.ask("POWER:RANGE:AUTO?").rstrip()


    #--- zero suppression
    for n in range( 1, 6 ) : 
      time.sleep(0.1); 
      power_meter.write("SENSE:CORRECTION:COLLECT:ZERO:INITIATE")
      state = 9
      while state > 0 : 
        time.sleep(0.1);  
        state = int(power_meter.ask("SENSE:CORRECTION:COLLECT:ZERO:STATE?"))
        # print "Info: Zero adjustment (1=waiting, 0=done) :", state
      else:
        power = float(power_meter.ask("SENSE:CORRECTION:COLLECT:ZERO:MAGNITUDE?"))
        print "Info: Pedestal [pW] : ",power/pW 

    ### reduce counts per average  (1 count takes 2 ms) 
    counts = 2000  
    cmd = "SENSE:AVERAGE:COUNT %i " % counts 
    power_meter.write(cmd)  
    counts = int(power_meter.ask("SENSE:AVERAGE:COUNT?"))
    print "Info: Samples per average post, zero adjustment: ",int(counts) 




def get_p3(sample_time=5.0) :             # measure average number of photons per pulse (p3) 
    power = np.array([ ],dtype=np.float64)
    start = time.time()                                       # start clock for OFF time 

    global power_meter # to get the instance of power meter from setup_power_meter

    while  (time.time()+86400-start)%86400 < sample_time  : 
       power = np.append(power,float(power_meter.ask("READ?")))   # start measurement; when finished read average power
    if power.size < 3 :
       print "Warning: Only %i power measurements made." % power.size 
    power_avg = np.average(power)
    power_rms = power.std()
    del power 
    #print "Info: Power [pW] : ",power_avg/pW,power_rms/pW 
    p3_value = 218.6 * (power_avg/pW)*(1e4/rate) * (wavelength_nm/435.0) # number of photons per pulse
    p3_error = 218.6 * (power_rms/pW)*(1e4/rate) * (wavelength_nm/435.0) # error estimate

    pow = (power_avg/pW) 

    return { "photons" : p3_value , "error" : p3_error}


