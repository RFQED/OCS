from modbusobjects import *

# If you whant to create a new behaviour check the Bexample.py
# Two changes have to be preform: in wrapper.py - configured variables
# the importArrays(...) method needs to know about a new behaviour name (ctrl+f 'example')
# the new class need to be imported on Channel.py
#  ['1', '1', 'ST', 'U1', '1', '', '', '', '', '', '']
#  ['1', '1', 'Unit 1', '', '1']
# Dependecies:
# logging.handlers
# Thread
# gspread
# ServiceAccountCredentials
# modbus_tk
# struct
# csv
# os

import fpga_comms
import Ignition_Import_2

if __name__ == '__main__':
    daemon = Wrapper("/tmp/wrapperPID.pid")
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            fpga_comms.init_fpga_comms() #FOR OCS Comms 

            # daemon.readTxt("Configuration1.csv")
            IgnitionChannelNamesList = ["Board Temperature", "Pulse Temperature", "Pulse Frequency", "Pulse Width", "Switch", "PhDoutput"]

            UDTName = "OCS Wrapper"
            UDTParent = "OCS Wrapper"
            DeviceName = "Liver-pool"
            sshUser = "user"
            sshHostAddress = "0.0.0.0"

            Behaviors = ["bocs"] * len(IgnitionChannelNamesList)

            commands = ["temperatureboard", "ledtemperature", "frequency", "pulsewidth", "switch", "phdoutput"]

            """
            ip = "192.168.2.10"
            port = '161'
            community = 'guru'
            Commands = []
            for c in commands:
                Commands.append([c, ip, port, community])
            """
            Datatypes = ["FLOAT", "FLOAT" , "FLOAT", "FLOAT", "BOOL", "FLOAT"]
            MBtype = ["HOLDING_REGISTERS"] * len(IgnitionChannelNamesList)

            nChannels = 40

            daemon.createGenericChannels()
            s, u, c = daemon.createExtraChannels(nChannels, Behaviors, commands, Datatypes, MBtype)
            print "Channels!!!!!!!!!!!!!!!"
            print len(c)
            #print c
            daemon.start()
            daemon.log.info("Creating Ignition UDT")
            Ignition_Import_2.IgnitionWrapperUdtCreator(c, UDTName, UDTParent, DeviceName, IgnitionChannelNamesList,
                                                      sshUser, sshHostAddress)

        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
