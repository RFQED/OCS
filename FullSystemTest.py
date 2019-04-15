# To get version numbers:  python -c "from pyvisa import util; util.get_debug_info()"
#
# Installation on Linux 
# - download and install LabView runtime libraries 
# - get Python VISA libraries from https://pypi.python.org/pypi/PyVISA
# import serial                    # Needed for temperature sensor
# import serial.tools.list_ports   # Needed for temperature sensor
#import DRS4Wrapper
#import numpy as np


# FOR ONE MEASUREMENT LOOP
#  SET TRIGGER WIDTH
#  RECORD POWERMETER numphotons 
#  USE CALIBRATION CURVE TO CALCULATE THE PMT CONTROL VOLTAGE FOR THIS MEASUREMTN
#  TAKE n MEASUREMENTS AT THIS CONTROL VOLTAGE. 
#  MOVE TO NEXT TRIGGER WIDTH. 

import sys
import time
import string
import re
import threading
from array import *
import math
import ROOT
import os

from constants import *
from powermeter import *
from pmt import *
from fpga_comms import *
from config import *
# global parameter 

global pulserboardnum 
print("Pulser Board Number: " + str(sys.argv[1]))
pulserboardnum = str(sys.argv[1])

class Measurement(threading.Thread ): 
    def __init__(self, threadID, name, wavelength_nm=LEDWavelength_nm, rate=pulsingFreq):

        threading.Thread.__init__(self)

        self.exit_flag = 0
        self.next_flag = 0
        self.numMeasurInBlock = n_repeats
        self.name = name 
        self.threadID = threadID      
        self.wavelength_nm = wavelength_nm
        self.rate = rate
   
        try:
            init_pmt()
        except:
           print("\n failure to set up pmt \n ")
           sys.exit(0)
        
        set_pmt_control_v(0.75) #calc_pmt_ctrl(50000))      # set pmt control voltage [V]    


#    def takePDReading(self):
#        serPD = serial.Serial(port='/dev/cu.usbmodem14121', baudrate=9600)
#        print("connected to PD")
#        global PDCh1
#        PDCh1 = serPD.readline()
#        PDCh1 = re.sub('[^0-9\.]', '', PDCh1)
#        print("Recieved " + PDCh1 + " from PD" )
#        
#        if(PDCh1 == ''):
#            PDCh1 = 0

    def run(self):
        init_fpga_comms()

        #      n_repeats = 1             # number of repeat measurements at each delay // should now be in config file
        counter = 0
        
        print('Start measurements')
        print('Switching off pulses')
        turn_all_pulsers_off()
        set_registers()

        setup_power_meter()
        p3_off = get_p3()

        print('Switching on pulses')
        turn_all_pulsers_on()
        set_pulse_width(widthSetPoints[0])
        set_registers()

        # get nphot then change control voltage
        p3_on = get_p3()
        p3_value =          ( p3_on["photons"]  - p3_off["photons"]  )
        p3_error = math.sqrt( p3_on["error"]**2 + p3_off["error"]**2 )
        nphot = max(p3_value,1)

        print("nphotons = " + str(nphot))
        print("PMT control voltage is " + str(calc_pmt_ctrl(nphot)))
        set_pmt_control_v(calc_pmt_ctrl(nphot))      # set pmt control voltage [V]

        fname1 = "PB" + str(pulserboardnum) + "_Freq" + str(pulsingFreq) + "khz_" + "Date_"
        fname = fname1 + time.strftime("%Y%m%d") + "_" + time.strftime("%H_%M_%S") + ".txt"
        fnameroot = outputDirectory + fname1 + time.strftime("%Y%m%d") + "t" + time.strftime("%H_%M_%S") + ".root"
        textFileOutput = open(outputDirectory + fname,"w")

        outputRootFile = ROOT.TFile(fnameroot, "RECREATE")
        tree = ROOT.TTree("tree","tree")

        nph  = array("d", [0.0]) ; tree.Branch("nph",nph,"nph/D",64000)
        nphe = array("d", [0.0]) ; tree.Branch("nphe",nphe,"nphe/D",64000)
        tsec = array("d", [0.0]) ; tree.Branch("tsec",tsec,"tsec/D",64000)
        temp = array("d", [0.0]) ; tree.Branch("temp",temp,"temp/D",64000)
        width1 = array("d", [0.0]) ; tree.Branch("width1",width1,"width1/D",64000)
        amp1 = array("d", [0.0]) ; tree.Branch("amp1",amp1,"amp1/D",64000)
        charge1 = array("d", [0.0]) ; tree.Branch("charge1",charge1,"charge1/D",64000)
        intg1 = array("d", [0.0]) ; tree.Branch("intg1",intg1,"intg1/D",64000)
        pkpos1 = array("d", [0.0]) ; tree.Branch("pkpos1",pkpos1,"pkpos1/D",64000)
        width2 = array("d", [0.0]) ; tree.Branch("width2",width2,"width2/D",64000)
        amp2 = array("d", [0.0]) ; tree.Branch("amp2",amp2,"amp2/D",64000)
        charge2 = array("d", [0.0]) ; tree.Branch("charge2",charge2,"charge2/D",64000)
        intg2 = array("d", [0.0]) ; tree.Branch("intg2",intg2,"intg2/D",64000)
        pkpos2 = array("d", [0.0]) ; tree.Branch("pkpos2",pkpos2,"pkpos2/D",64000)
        width3 = array("d", [0.0]) ; tree.Branch("width3",width3,"width3/D",64000)
        widthset = array("d", [0.0]) ; tree.Branch("widthset",widthset,"widthset/D",64000)

#        pdReadingCh1 = array("d", [0.0]) ; tree.Branch("pdReadingCh1",pdReadingCh1,"pdReadingCh1/D",64000)
#        pdReadingCh2 = array("d", [0.0]) ; tree.Branch("pdReadingCh2",pdReadingCh2,"pdReadingCh2/D",64000)
#        pdReadingCh3 = array("d", [0.0]) ; tree.Branch("pdReadingCh3",pdReadingCh3,"pdReadingCh3/D",64000)
#        pdReadingCh4 = array("d", [0.0]) ; tree.Branch("pdReadingCh4",pdReadingCh4,"pdReadingCh4/D",64000)
#        pdReadingCh5 = array("d", [0.0]) ; tree.Branch("pdReadingCh5",pdReadingCh5,"pdReadingCh5/D",64000)
#        pdReadingCh6 = array("d", [0.0]) ; tree.Branch("pdReadingCh6",pdReadingCh6,"pdReadingCh6/D",64000)
#        pdReadingCh7 = array("d", [0.0]) ; tree.Branch("pdReadingCh7",pdReadingCh7,"pdReadingCh7/D",64000)


        stime = time.time()

#       nit = 100     # should now be in the config file
        peakPosAvg1 = 0.0
        widthAvg1 = 0.0
        peakPosAvg2 = 0.0
        widthAvg2 = 0.0

        for i in range(nit):
            data = get_record2()
            peakPosIn1 = get_measure_peak_time(1)
            widthIn1 = get_measure_neg_width(1)

            peakPosAvg1 = peakPosAvg1 + peakPosIn1
            widthAvg1 = widthAvg1 + widthIn1

            peakPosIn2 = get_measure_peak_time(2)
            widthIn2 = get_measure_neg_width(2)

            peakPosAvg2 = peakPosAvg2 + peakPosIn2
            widthAvg2 = widthAvg2 + widthIn2

        peakPosAvg1 = peakPosAvg1 / nit
        widthAvg1 = widthAvg1 / nit
        lowBnd1 = peakPosAvg1 - 3. * widthAvg1
        highBnd1 = peakPosAvg1 + 3. * widthAvg1
        peakPosAvg2 = peakPosAvg2 / nit
        widthAvg2 = widthAvg2 / nit
        lowBnd2 = peakPosAvg2 - 3. * widthAvg2
        highBnd2 = peakPosAvg2 + 3. * widthAvg2

        p3_on = get_p3()     
        p3_value =          ( p3_on["photons"]  - p3_off["photons"]  )   
        p3_error = math.sqrt( p3_on["error"]**2 + p3_off["error"]**2 )   
        nphot = max(p3_value,1)

        set_pmt_control_v(calc_pmt_ctrl(nphot))      # set pmt control voltage [V]

        global widthIndex

        while self.exit_flag < 1 :
            temp1 = temperature = peakAvg = chargeAvg = widthAvg = widthAvg1 = integralAvg = peakPosAvg = 0.0
#            n = 1000 previously before PD reading 



            # get nphot then change control voltage 
            p3_on = get_p3()     
            p3_value =          ( p3_on["photons"]  - p3_off["photons"]  )   
            p3_error = math.sqrt( p3_on["error"]**2 + p3_off["error"]**2 )   

            for i in range(n):
                data = get_record2()
                peakPosIn = get_measure_peak_time(1)
                widthIn = get_measure_pos_width(1)
                chargeIn = get_measure_charge1(lowBnd1,highBnd1)
                integralIn = get_measure_integral1(lowBnd1,highBnd1)
                peakIn = get_measure_peak(1)
                widthset[0] = widthSetPoints[widthIndex]

#                self.takePDReading()
#                global PDCh1
#                print("PD Channel 1")
#                print(PDCh1)

                widthAvg1 = widthAvg1 + widthIn

                tt = time.time() - stime

                nph[0] = float(p3_value)
                nphe[0] = float(p3_error)
                tsec[0] = float(tt)
                temp[0] = float(temperature)

                width1[0] = float(widthIn)
                amp1[0] = float(peakIn)
                charge1[0] = float(chargeIn)
                intg1[0] = float(integralIn)
                pkpos1[0] = float(peakPosIn)

                peakPosIn = get_measure_peak_time(2)
                widthIn = get_measure_neg_width(2)
                chargeIn = get_measure_charge2(lowBnd2,highBnd2)
                integralIn = get_measure_integral2(lowBnd2,highBnd2)
                peakIn = get_measure_peak(2)
                peakAvg = peakAvg + peakIn
                widthAvg = widthAvg + widthIn
                chargeAvg = chargeAvg + chargeIn
                integralAvg = integralAvg + integralIn
                peakPosAvg = peakPosAvg + peakPosIn

                width2[0] = float(widthIn)
                amp2[0] = float(peakIn)
                charge2[0] = float(chargeIn)
                intg2[0] = float(integralIn)
                pkpos2[0] = float(peakPosIn)
 
#                pdReadingCh1[0] = float(PDCh1)

                tree.Fill()

            peakAvg = peakAvg / n
            widthAvg = widthAvg / n
            chargeAvg = chargeAvg / n
            integralAvg = integralAvg / n
            peakPosAvg = peakPosAvg / n
            widthAvg1 = widthAvg1 / n
            pmt_flag = 1
    
            pmtGain =1# self.pmt_gain  

            pmtCtrl = calc_pmt_ctrl( nphot)

            print "%d %g %g %g %g %g %g %f %g %g %g %g" % (tt,p3_value,p3_error, widthAvg, peakAvg, chargeAvg, integralAvg, pmtCtrl, widthAvg1, temp1, widthset[0], widthIndex)
            outstr= "%d %g %g %g %g %g %g %f %g %g %g %g" % (tt,p3_value,p3_error, widthAvg, peakAvg, chargeAvg, integralAvg, pmtCtrl, widthAvg1, temp1, widthset[0], widthIndex)

            textFileOutput.write(outstr)
            counter = counter + 1

            if (counter % self.numMeasurInBlock == 0):
                if (widthIndex >= len(widthSetPoints)-1):
                    print("Measurements done - exit now.")
                    self.exit_flag = 1
                else:
                    # this is a hack till we do the flow of taking data better
                    widthIndex = widthIndex + 1
                    time.sleep(5)

                    set_pulse_width(widthSetPoints[widthIndex])
                    set_registers()
                    print(str(self.numMeasurInBlock) + " measurements taken, to changing width to " + str(widthSetPoints[widthIndex]) + "ns ")

                    
                    # get nphot then change control voltage 
                    p3_on = get_p3()     
                    p3_value =          ( p3_on["photons"]  - p3_off["photons"]  )   
                    p3_error = math.sqrt( p3_on["error"]**2 + p3_off["error"]**2 )   
                    nphot = max(p3_value,1)
                    
                    set_pmt_control_v(calc_pmt_ctrl(nphot))      # set pmt control voltage [V]
                    print("in LED Pulser and the check of the pulse amplitdue is " + str(check_pmt_amp()))
                    # check amp is between 100 and 400 
                    
            
        textFileOutput.close()
        outputRootFile.cd()
        tree.Write()
        outputRootFile.Close()
        print "Info: Exiting " + self.name
        os.system('say "Pulser Board Scan Finished.. Good Job!!"')
        measurement.exit_flag = 1 
#        outputfullpath = "/ "+str(fnameroot)
#        scpcommand = "scp " + str(outputfullpath) + " wturner@gateway.ph.liv.ac.uk:/hepstore/wturner/LZ/"
#        os.system(scpcommand)


measurement = Measurement(1,"measurement",wavelength_nm=LEDWavelength_nm, rate=pulsingFreq) 
 
while  measurement.exit_flag < 1  : 
  
  choice = raw_input(" start/stop/quit > ")

  if choice == 'start' :
     measurement.exit_flag = 0  
     measurement.start()  
  elif choice == 'stop' :
     measurement.exit_flag = 1 
  elif choice == 'quit' :
     measurement.exit_flag = 1 
     print "Info: All exit flags raised."
  elif choice == 'next' :
      measurement.next_flag = 1
  elif choice == '' :
     pass 
  else :
     print "Unknown commmand: ",choice 

print "Info: Exiting main thread."

sys.exit(0)
