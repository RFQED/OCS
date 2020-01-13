import time
import os
import sys
import signal
import struct
#import gspread
import logging.handlers

from threading import Thread
from modbus_tk import hooks, modbus_tcp, utils
#from oauth2client.service_account import ServiceAccountCredentials
from LastLogsHandlerAndVerify import LastLogsHandler
from LastLogsHandlerAndVerify import Verify
from Behaviors import *
import modbus_tk.defines as cst
import dataTypes as dt
import csv

units = []


class Wrapper(Thread):

    log = logging.getLogger('Wrapper')
    log.setLevel(logging.DEBUG)

    hdlr = logging.handlers.RotatingFileHandler('/var/log/Wrapperlogs.log', mode='a', maxBytes=10*1024*1024,
                                                backupCount=1, encoding=None, delay=False)
    formatter = logging.Formatter('%(asctime)s - %(name)s %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    hdlr.setLevel(logging.INFO)
    log.addHandler(hdlr)

    hdlrdebug = logging.handlers.RotatingFileHandler('/var/log/Wrapperlogsdebug.log', mode='a', maxBytes=10*1024*1024,
                                                     backupCount=1, encoding=None, delay=False)
    hdlrdebug.setFormatter(formatter)
    hdlrdebug.setLevel(logging.DEBUG)
    log.addHandler(hdlrdebug)

    hdlremergency = logging.handlers.RotatingFileHandler('/var/log/Wrapperlogswarning.log', mode='a', maxBytes=10*1024*1024,
                                                         backupCount=1, encoding=None, delay=False)
    hdlremergency.setFormatter(formatter)
    hdlremergency.setLevel(logging.WARNING)
    log.addHandler(hdlremergency)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    log.addHandler(ch)

    # GUI log
    logHandler = LastLogsHandler(500)
    logHandler.setFormatter(formatter)
    logHandler.setLevel(logging.DEBUG)
    log.addHandler(logHandler)

    def __init__(self, pidfile):
        Thread.__init__(self)

        self.servers = []
        self.runFlag = False
        self.pidfile = pidfile
        self.setDaemon(True)
        self.period = 1

        self.toVerifyChannels = 0
        self.numberOfChannels = 0
        self.timetotalexecution = 0
        self.timeexecutionperchannel = 0

        self.lastLog = Wrapper.logHandler.getStr()

        self.port = 5555
        self.serverId = 1
        self.currentUnitID = 1
        self.channelID = 1
        self.currentMBaddress = 0
        self.modbusServernamePrefix = "Server"
        self.unitNamePrefix = "Unit"
        self.configurationApproved = False
        self.pidrunning = False
        self.serversConfiguration = [[],
                                     [str(self.serverId), self.modbusServernamePrefix + " " +
                                      str(self.serverId), "", str(self.port)]]
        self.unitsConfiguration = [[],
                                   [str(self.currentUnitID), str(self.serverId),
                                    self.unitNamePrefix + " " + str(self.currentUnitID), "", str(self.currentUnitID)]]
        self.channelsConfiguration = [[]]

        pid = self.getPID()
        if pid:
            Wrapper.log.info("Pidfile "+self.pidfile+" already exist. Daemon already running? (pid " + str(pid) + ")")
            self.pidrunning = True

        # Synchronous response
        # callbacks for client input
        def registerSync(args):
            Wrapper.log.debug("REGISTER")
            (slave, request_pdu) = args
            ch = ord(request_pdu[1])*256 + ord(request_pdu[2])
            for s in self.servers:
                for n in s.units:
                    if n.modbusSlave == slave:
                        for c in n.channels:
                            if c.modbusStartindAddress == ch:
                                Wrapper.log.debug(c)
                                Wrapper.log.debug(c.setValueFromM(request_pdu))

            return None

        def multipleRegisterSync(args):

            Wrapper.log.debug("REGISTER_MULTIPLE")
            (slave, request_pdu) = args
            ch = ord(request_pdu[1])*256 + ord(request_pdu[2])
            for s in self.servers:
                for n in s.units:
                    if n.modbusSlave == slave:
                        for c in n.channels:
                            if c.modbusStartindAddress == ch:
                                Wrapper.log.debug(c)
                                Wrapper.log.debug(c.setValueFromM(request_pdu))
            return None

        def coilSync(args):

            Wrapper.log.debug("COIL")
            (slave, request_pdu) = args
            ch = ord(request_pdu[1])*256 + ord(request_pdu[2])
            for s in self.servers:
                for n in s.units:
                    if n.modbusSlave == slave:
                        for c in n.channels:
                            if c.modbusStartindAddress == ch:
                                Wrapper.log.debug(c)
                                Wrapper.log.debug(c.setValueFromM(request_pdu))

            return None

        def multipleCoilSync(args):
            Wrapper.log.debug("COIL_MULTIPLE")
            (slave, request_pdu) = args
            ch = ord(request_pdu[1])*256 + ord(request_pdu[2])
            for s in self.servers:
                for n in s.units:
                    if n.modbusSlave == slave:
                        for c in n.channels:
                            if c.modbusStartindAddress == ch:
                                Wrapper.log.debug(c)
                                Wrapper.log.debug(c.setValueFromM(request_pdu))
            return None

        hooks.install_hook("modbus.Slave.handle_write_single_register_request", registerSync)
        hooks.install_hook("modbus.Slave.handle_write_multiple_registers_request", multipleRegisterSync)
        hooks.install_hook("modbus.Slave.handle_write_single_coil_request", coilSync)
        hooks.install_hook("modbus.Slave.handle_write_multiple_coils_request", multipleCoilSync)

    # creates a new modbus server instance
    def addServer(self, name, description, port):
        server = Server(name, description, port, self)
        self.servers.append(server)
        return server

    # the cofiguration com a text file
    # An example of the config file .txt or .csv - Configuration.csv
    def readTxt(self, get_file):

        dataServer = [['']]
        dataUnit = [['']]
        dataChannel = [['']]

        with open(get_file) as textFile:
            for line in textFile:
                if line[0:2] == "/s":
                    lines = line.rstrip('\r\n').split('\t')
                    dataServer.append(lines[1:])
                if line[0:2] == "/u":
                    lines = line.rstrip('\r\n').split('\t')
                    dataUnit.append(lines[1:])
                if line[0:2] == "/c":
                    lines = line.rstrip('\r\n').split('\t')
                    dataChannel.append(lines[1:])

        sheet_Server = dataServer[1:]
        sheet_units = dataUnit[1:]
        sheet_channel = dataChannel[1:]

        # Check for configuration error!
        return self.configurationValidation(sheet_Server, sheet_units, sheet_channel)

    # pretty much the same as .readtxt
    def readCSV(self, get_file):

        dataServer = [['']]
        dataUnit = [['']]
        dataChannel = [['']]

        with open(get_file) as csvfile:
            spamreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for line in spamreader:
                if line[0] == "/s":
                    lines = line
                    dataServer.append(lines[1:])
                if line[0] == "/u":
                    lines = line
                    dataUnit.append(lines[1:])
                if line[0] == "/c":
                    lines = line
                    dataChannel.append(lines[1:])

        sheet_Server = dataServer[1:]
        sheet_units = dataUnit[1:]
        sheet_channel = dataChannel[1:]

        # Check configuration error!
        return self.configurationValidation(sheet_Server, sheet_units, sheet_channel)

    # import the configuration file from a google spreadsheet
    # spreadsheet 0 for server configuration
    # spreadsheet 1 for units (address space) configuration
    # spreadsheet "channelSheet" for channels configuration
    def importGSpread(self, channelSheet=6):

        Wrapper.log.debug("Import Google Spread sheet")
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('Simulador-a33b00a474b9.json', scope)
        gc = gspread.authorize(credentials)
        sh = gc.open('ModbusChannels')

        server_sheet = sh.get_worksheet(0)
        units_sheet = sh.get_worksheet(1)
        channels_sheet = sh.get_worksheet(channelSheet)

        sheet_Server = server_sheet.get_all_values()
        sheet_units = units_sheet.get_all_values()
        sheet_channel = channels_sheet.get_all_values()

        # Check errors!
        return self.configurationValidation(sheet_Server, sheet_units, sheet_channel)

    # general importation from lists of servers, units and channels.
    # readTxt, readCsv and importGSpread will call this function after the configurationValidation
    # if returns True then there is a problem with the importation
    def importArrays(self, importservers, importunits, importchannels):
    
        # Channel Column defines
        Wrapper.log.info('Loading configuration.')
        s_id = 0
        s_name = 1
        s_description = 2
        s_port = 3

        u_globchannelId = 0
        u_serverid = 1
        u_name = 2
        u_description = 3
        u_mdId = 4

        c_unitglobalId = 1
        c_name = 2
        c_description = 3
        c_reverse = 4
        c_dataType = 5
        c_startingAdd = 6
        c_lenght = 7
        c_modbusType = 8
        c_behaviour = 9
        c_command = 10

        failed = False
        for server in importservers[1:]:
            if server[s_id] != "":
                serverObj = self.addServer(server[s_name], server[s_description], int(server[s_port]))
                serverSpreadsheetid = server[s_id]
                serverObj.updateId(serverSpreadsheetid)
                for unit in importunits[1:]:
                    if unit[u_globchannelId] != "":
                        if unit[u_serverid] == serverSpreadsheetid:
                            unitObj = serverObj.addUnit(unit[u_name], unit[u_description], int(unit[u_mdId]))
                            unitSpreadsheetId = unit[u_globchannelId]
                            unitObj.updateNodeID(unitSpreadsheetId)
                            for channel in importchannels[1:]:
                                if channel[c_unitglobalId] != "":
                                    if channel[c_unitglobalId] == unitSpreadsheetId:
                                        # Modbus Type
                                        modbusType = -1
                                        if channel[c_modbusType] == "ANALOG_INPUTS":
                                            modbusType = cst.ANALOG_INPUTS
                                        elif channel[c_modbusType] == "COILS":
                                            modbusType = cst.COILS
                                        elif channel[c_modbusType] == "DISCRETE_INPUTS":
                                            modbusType = cst.DISCRETE_INPUTS
                                        elif channel[c_modbusType] == "HOLDING_REGISTERS":
                                            modbusType = cst.HOLDING_REGISTERS
                                        else:
                                            Wrapper.log.error("Modbus type not known! : " + channel[c_modbusType])
                                            failed = True
                                            pass

                                        # Data type
                                        dataType = -1
                                        if channel[c_dataType] == "BOOL":
                                            dataType = dt.BOOL
                                        elif channel[c_dataType] == "BCD":
                                            dataType = dt.BCD
                                        elif channel[c_dataType] == "BCD32":
                                            dataType = dt.BCD32
                                        elif channel[c_dataType] == "DOUBLE":
                                            dataType = dt.DOUBLE
                                        elif channel[c_dataType] == "FLOAT":
                                            dataType = dt.FLOAT
                                        elif channel[c_dataType] == "INTEGER":
                                            dataType = dt.INTEGER
                                        elif channel[c_dataType] == "SHORT":
                                            dataType = dt.SHORT
                                        elif channel[c_dataType] == "UNSIGNED_INTEGER":
                                            dataType = dt.UNSIGNED_INTEGER
                                        elif channel[c_dataType] == "UNSIGNED_SHORT":
                                            dataType = dt.UNSIGNED_SHORT
                                        elif channel[c_dataType] == "STRING":
                                            dataType = dt.STRING
                                        else:
                                            Wrapper.log.error('Unknown datatype: ' + channel[c_dataType])
                                            failed = True
                                            pass

                                        # Create Channel
                                        behavior = None
                                        channelObj = unitObj.addChannel(channel[c_name], channel[c_description],
                                                                        dataType, int(channel[c_startingAdd]),
                                                                        int(channel[c_lenght]), modbusType,
                                                                        behavior, channel[c_reverse])
                                        Wrapper.log.debug("Channel added: " + str(channelObj))

                                        failed = channelObj.setBehavior(channel[c_behaviour].lower(), channel[c_command:])

        Wrapper.log.info("Wrapper created.")
        return failed

    # check if there is any problem with the configuration imported such as 
    # overlapping address, duplicated name, etc...
    def configurationValidation(self, sheet_server, sheet_units, sheet_channel):

        toVerifyChannels = sheet_channel
        toVerifyUnits = sheet_units
        toVerifyServers = sheet_server

        a = Verify()

        tupleCheckChannels = a.dataIntegrityChannels(toVerifyChannels)
        tupleCheckUnits = a.dataIntegrityUnits(toVerifyUnits)
        tupleCheckServer = a.dataIntegrityServers(toVerifyServers)

        
        if tupleCheckServer[0] == 0 and tupleCheckUnits[0] == 0 and tupleCheckChannels[0] == 0 and not self.pidrunning:
            
            # validation approved, but importArrays might return an error.
            self.configurationApproved = not self.importArrays(toVerifyServers, toVerifyUnits, toVerifyChannels)
            print self.configurationApproved
            return not self.configurationApproved

        else:
            toVerifyChannels = tupleCheckChannels[1]
            toVerifyUnits = tupleCheckUnits[1]
            toVerifyServers = tupleCheckServer[1]
            if toVerifyServers != "":
                Wrapper.log.error(toVerifyServers)
            if toVerifyUnits != "":
                Wrapper.log.error(toVerifyUnits)
            if toVerifyChannels != "":
                Wrapper.log.error(toVerifyChannels)

    # acquisition rate for reading the Behavior values
    def setPeriod(self, period):
        self.period = period

    def getLogString(self):
        return self.logHandler.getStr()

    # starts the wrapper
    def run(self):
        self.runFlag = True
        self.daemonize()
        
        # the wrapper stops if there was an error with the configuration or during the importArrays
        if self.configurationApproved:

            while self.runFlag:
                self.runCycle()
                time.sleep(self.period)
        else:
            self.log.fatal("Error in configuration")
            self.stop()
            raise SystemExit

    def runCycle(self):

        self.numberOfChannels = 0
        then = time.time()
        for s in self.servers:
            for n in s.units:
                self.numberOfChannels += len(n.channels)

        for s in self.servers:
            for n in s.units:
                for c in n.channels:
                    try:
                        c.updateMValue()
                    except Exception, e:
                        Wrapper.log.warning(str(c)+". Error: " + str(e))

        self.timetotalexecution = (time.time() - then) * 1000
        self.timeexecutionperchannel = self.timetotalexecution/self.numberOfChannels
        self.lastLog = Wrapper.logHandler.getStr()

    # stores the PID value in a temp file
    def daemonize(self):

        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()

        except IOError:
            pid = None

        if pid:

            self.runFlag = False
        else:
            pid = str(os.getpid())
            message = "Running on PID %s"
            Wrapper.log.info(message % str(pid))
            file(self.pidfile, 'w+').write("%s\n" % pid)
            self.runFlag = True

    # delete the PID file
    def delpid(self):
        try:
            os.remove(self.pidfile)
        except Exception as e:
            Wrapper.log.fatal(e, exc_info=True)

    # grabs the PID value from the temporary file and kill it
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            Wrapper.log.error(message % self.pidfile)

            return  # not an error in a restart

        # Try killing the daemon process
        try:
            message = "Killing pid %s \n"
            Wrapper.log.info(message % str(pid))
           
            os.kill(pid, signal.SIGKILL)

	    self.delpid()

        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                Wrapper.log.error(str(err))
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def getPID(self):

        pid = -1
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        except ValueError, error:

            Wrapper.log.error("While getting PID (deleting PID file: "+self.pidfile+"): " + str(error))
            self.delpid()
            pid = None

        except Exception as e:
            Wrapper.log.fatal(e, exc_info=True)

        return pid

    # extra channel are channels created accordingly with the wrapper.py file
    # 1 extra channel represents a structure of modbus addresses which is sequentially repeated.
    # nChannels - number of channels with a given structure to be created
    # Behaviors - list of behaviors inside the stucture. Can have different Behaviors
    # Commands - list of commands for each behavior with a 1-1 correspondence
    # Datatype - list of the modbus structure datatypes
    # ModbusType - list with the modbus functions codes
    def createExtraChannels(self, nChannels, Behaviors, Commands, Datatype, ModbusTypes):

        lengthGenericChannels = len(self.channelsConfiguration)
        behaviors = Behaviors
        channelsCommands = Commands
        channelsDatatypes = Datatype
        modbusTypes = ModbusTypes

        for nC in range(nChannels):
            for mbtype, datatype, behavior, command in zip(modbusTypes, channelsDatatypes, behaviors, channelsCommands):
                
                mb_length = Channel.getNumberOfRegisterModBus(datatype)

                realCommand = Behavior.getRealCommand(behavior, command, nC, len(self.channelsConfiguration)-1)
                name = behavior+str(realCommand[0])+"-"+str(self.channelID)
                self.addModbusChannel(name, datatype, mb_length, mbtype, behavior, realCommand)

        self.configurationValidation(self.serversConfiguration, self.unitsConfiguration, self.channelsConfiguration)
        self.logConfiguration(lengthGenericChannels+len(Behaviors))

        return self.serversConfiguration, self.unitsConfiguration, self.channelsConfiguration[lengthGenericChannels:]

    # extra channels are channels with some information about the wrapper it self, such as time of execution
    # number of channels and mean time of execution by channels.
    # All generic channels are handle by the wrappermanager behavior
    # it's possible to add extra Generic Channels
    def createGenericChannels(self, extraNames=(), extraDatatype=(), extraMBTypes=(), extraCommands=()):

        Wrapper.log.info("Creating Generic Channels")

        wrapperManagerCommands = ["totalexecutiontime", "executiontimeperchannel", "nchannels"] + list(extraCommands)
        Datatypes = ["FLOAT", "FLOAT", "FLOAT"] + list(extraDatatype)
        modbusDatatypes = ["HOLDING_REGISTERS", "HOLDING_REGISTERS", "HOLDING_REGISTERS"] + list(extraMBTypes)
        names = ["TotalexecutionTime", "Timeperchannel", "Nchannels"] + list(extraNames)

        for chlindex in range(len(names)):
            name = names[chlindex]
            datatype = Datatypes[chlindex]
            mb_dt = modbusDatatypes[chlindex]
            mb_length = Channel.getNumberOfRegisterModBus(datatype)
            commands = wrapperManagerCommands[chlindex]

            self.addModbusChannel(name, datatype,  mb_length, mb_dt, "wrappermanager", commands)

    # adds a modbus channel do be imported in importArrays
    def addModbusChannel(self, name, channel_datatype,  mb_length, mb_type, behavior, commands, description=''):
        reverse = "FALSE"

        channelToImport = [str(self.channelID), str(self.currentUnitID),
                           name, description,
                           reverse, str(channel_datatype),
                           str(self.currentMBaddress), str(mb_length),
                           mb_type, behavior]

        if type(commands) == list or type(commands) == tuple:
            for commamd in commands:
                channelToImport.append(commamd)
        else:
            channelToImport.append(commands)

        self.channelsConfiguration.append(channelToImport)
        self.currentMBaddress += mb_length
        self.channelID += 1


    # adds and log entry with the modbus configuration
    def logConfiguration(self, lengthChannels):
        stitle = "Server id\tServer Name\tDescription\tPort"
        utitle = "Global Id\tServer id\tUnit Name\tDescription\tMB Id"
        ctitle = "Unit Id-Channel Name-Description-MB Id-Reverse word-Datatype-Address-Length-MB type-Behavior-Commands"
        Wrapper.log.info("Wrapper Configuration")
        Wrapper.log.info(stitle)
        for s in self.serversConfiguration:
            if len(s) > 0:
                st = ''
                for sinfo in s:
                    if sinfo == '':
                        sinfo = "Na"
                    st += str(sinfo) + "\t"
                Wrapper.log.info(st)

        Wrapper.log.info(utitle)
        for u in self.unitsConfiguration:
            if len(u) > 0:
                ut = ''
                for uinfo in u:
                    if uinfo == '':
                        uinfo = "Na"
                    ut += str(uinfo) + "\t"
                Wrapper.log.info(ut)

        Wrapper.log.info(ctitle)
        for c in self.channelsConfiguration[:lengthChannels]:
            if len(c) > 0:
                ct = ''
                for cinfo in c[1:]:
                    if cinfo == '':
                        cinfo = "Na"
                    ct += str(cinfo) + "\t"
                Wrapper.log.info(ct)

    def __str__(self):
        string = "Simulator\n"
        for s in self.servers:
            string += str(s)+"\n"
            for n in s.units:
                string += "  " + str(n) + "\n"
                for c in n.channels:
                    string += "    " + str(c) + "\n"
        return string

# the extra layer on top of the modbus-tk package which represents a modbus server
class Server(object):

    log = logging.getLogger('Wrapper.Server')

    def __init__(self, name, description, port, wrapper):

        # MODBUS configuration
        self.id = 0
        self.name = str(name)
        self.description = description
        self.port = port
        self.wrapper = wrapper

        self.units = []

        self.logger = utils.create_logger(name="console", record_format="%(message)s")

        self.modbusServer = modbus_tcp.TcpServer(port=self.port)
        try:
            self.modbusServer.start()
        except Exception, e:
            self.log.fatal("Error on start: "+str(e))

    def addUnit(self, name, description, ID):
        unit = Unit(self, name, description, ID)
        self.units.append(unit)

        return unit

    def updateUnits(self):
        for u in self.units:
            u.updateChannels()

    def getUnitsChannelsMValues(self):
        for u in self.units:
            u.getChannelsMValues()

    def getUnits(self):

        return self.units

    def updateId(self, get_id):
        self.id = get_id

    def __str__(self):
        return "Server: %s %s %s" % (self.name, self.description, str(self.port))

# the extra layer on top of the modbus-tk package which represents a modbus address space
class Unit(object):
    log = logging.getLogger('Wrapper.Unit')

    def __init__(self, server, name, description, ID):
        self.nodeID = 0
        self.ID = ID
        self.name = name
        self.description = description
        self.channels = []
        self.server = server
        try:
            self.modbusSlave = self.server.modbusServer.add_slave(self.ID)
        except Exception, e:
            self.log.fatal("Error creating unit: " + str(e))

        units.append(self)

    def addChannel(self, name, description, dataType, modbusStartindAddress, modbusLength, modbusType, behaviour,
                   reverse):
        channel = Channel(self, name, description, dataType, modbusStartindAddress, modbusLength, modbusType, behaviour,
                          reverse)
        self.channels.append(channel)
        return channel

    def getChannels(self):
        return self.channels

    def updateChannels(self):
        for c in self.channels:
            c.update()

    def getChannelsMValues(self):
        for c in self.channels:
            c.getMValues()

    def updateNodeID(self, nodeID):
        self.nodeID = nodeID

    def __str__(self):
        return "Unit: %s %s" % (self.name, self.description)

# the modbus channel which make the Bhavior calls
class Channel(object):

    log = logging.getLogger('Wrapper.Channel')

    def __init__(self, unit, name, description, dataType, modbusStartindAddress, modbusLength, modbusType, behavior,
                 reverse):

        self.name = str(name)
        self.description = str(description)
        self.dataType = dataType
        self.behavior = behavior
        self.reverse = str(reverse)
        self.value = None
        self.unit = unit
        self.modbusStartindAddress = modbusStartindAddress
        self.modbusLength = modbusLength
        self.modbusType = modbusType
        self.globalId = 0

        for s in self.unit.server.wrapper.servers:
            for u in s.units:
                self.globalId += len(u.channels)-1

        self.modbusName = str(self.modbusStartindAddress)+"_"+str(self.modbusLength)+"_"+str(self.modbusStartindAddress)

        try:
            unit.modbusSlave.add_block(self.modbusName, self.modbusType, self.modbusStartindAddress, self.modbusLength)
        except Exception, e:
            self.log.fatal("Can't create " + str(self) + ". Error: " + str(e))

        self.locked = False

        self.log = logging.getLogger('Wrapper.channel.'+self.name)

        self.logHandler = LastLogsHandler(50)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s \t\t %(message)s')
        self.logHandler.setFormatter(self.formatter)
        self.logHandler.setLevel(logging.INFO)
        self.log.addHandler(self.logHandler)

        self.log.debug("Channel created")

    # gets the new value from a modbus client
    def setValueFromM(self, request_pdu):
        raw = [0, 0, 0, 0]

        conv = -1
        if self.dataType == dt.BOOL:

            teste = struct.unpack('?', request_pdu[3])

            if self.modbusType == 3:
                raw[0] = ord(request_pdu[3]) * 256 + ord(request_pdu[4])
                teste = struct.unpack('h', struct.pack('<H', raw[0]))

            conv = teste[0]

        elif self.dataType == dt.INTEGER:
            raw[0] = ord(request_pdu[6])*256+ord(request_pdu[7])
            raw[1] = ord(request_pdu[8])*256+ord(request_pdu[9])

            teste = struct.unpack('i', struct.pack('<HH', raw[0], raw[1]))
            if self.reverse.lower() == 'true':
                teste = struct.unpack('I', struct.pack('<HH', raw[1], raw[0]))
            conv = int(teste[0])

        elif self.dataType == dt.UNSIGNED_INTEGER:
            raw[0] = ord(request_pdu[6])*256+ord(request_pdu[7])
            raw[1] = ord(request_pdu[8])*256+ord(request_pdu[9])

            teste = struct.unpack('I', struct.pack('<HH', raw[0], raw[1]))

            if self.reverse.lower() == 'true':
                teste = struct.unpack('I', struct.pack('<HH', raw[1], raw[0]))

            conv = int(teste[0])

        elif self.dataType == dt.SHORT:
            raw[0] = ord(request_pdu[3])*256+ord(request_pdu[4])

            teste = struct.unpack('h', struct.pack('<H', raw[0]))
            conv = int(teste[0])

        elif self.dataType == dt.UNSIGNED_SHORT:
            raw[0] = ord(request_pdu[3]) * 256 + ord(request_pdu[4])
            teste = struct.unpack('H', struct.pack('<H', raw[0]))
            conv = int(teste[0])

        elif self.dataType == dt.FLOAT:
            raw[0] = ord(request_pdu[6])*256+ord(request_pdu[7])
            raw[1] = ord(request_pdu[8])*256+ord(request_pdu[9])

            teste = struct.unpack('f', struct.pack('<HH', raw[0], raw[1]))
            if self.reverse.lower() == 'true':
                teste = struct.unpack('f', struct.pack('<HH', raw[1], raw[0]))
            conv = float(teste[0])

        elif self.dataType == dt.DOUBLE:
            raw[0] = ord(request_pdu[6])*256+ord(request_pdu[7])
            raw[1] = ord(request_pdu[8])*256+ord(request_pdu[9])
            raw[2] = ord(request_pdu[10])*256+ord(request_pdu[11])
            raw[3] = ord(request_pdu[12])*256+ord(request_pdu[13])

            teste = struct.unpack('d', struct.pack('<HHHH', raw[0], raw[1], raw[2], raw[3]))
            if self.reverse.lower() == 'true':
                teste = struct.unpack('d', struct.pack('<HHHH', raw[3], raw[2], raw[1], raw[0]))
            conv = float(teste[0])

        elif self.dataType == dt.STRING:

            raw[0] = ord(request_pdu[6]) * 256 + ord(request_pdu[7])
            raw[1] = ord(request_pdu[8]) * 256 + ord(request_pdu[9])
            raw[2] = ord(request_pdu[10]) * 256 + ord(request_pdu[11])
            raw[3] = ord(request_pdu[12]) * 256 + ord(request_pdu[13])

            teste = struct.pack('<HHHH', raw[0], raw[1], raw[2], raw[3])

            if self.reverse.lower() == 'true':
                teste = struct.unpack('s', struct.pack('<HH', raw[1], raw[0]))
            conv = str(teste)

        # self.locked is an extra property to prevents writes to 
        if not self.locked:

            self.value = conv
            try:
                self.behavior.setSetpoint(self.value)
                self.log.info("New value from modbus client: "+str(self.value))
            except Exception, e:
                self.log.warning(str(self)+" - New modbus value error: "+str(e))

        else:
            self.log.warning("New not autorized attemp to change value from modbus client: " + str(conv) +
                             ". Wrapper channel in read-only mode!")
            pass

    # gets the value from the behavior a writes it to the modbus address
    def updateMValue(self):
        conv = []

        self.value = self.behavior.getValue()
        valueError = False
	
        if self.value is None:
            valueError = True
            self.value = 0.0

        if self.dataType == dt.INTEGER:
            word1, word2 = struct.unpack('<HH', struct.pack('i', int(self.value)))
            conv = [word1, word2]
            if self.reverse.lower() == 'true':
                conv = [word2, word1]

        elif self.dataType == dt.UNSIGNED_INTEGER:
            if self.value < 0:
                self.value = 0

            word1, word2 = struct.unpack('<HH', struct.pack('I', int(self.value)))
            conv = [word1, word2]
            if self.reverse.lower() == 'true':
                conv = [word2, word1]

        elif self.dataType == dt.SHORT:
            word1 = struct.unpack('<H', struct.pack('h', int(self.value)))
            conv = [word1[0]]

        elif self.dataType == dt.UNSIGNED_SHORT:
            if self.value < 0:
                self.value = 0
            word1 = struct.unpack('<H', struct.pack('H', int(self.value)))
            conv = [word1[0]]

        elif self.dataType == dt.FLOAT:

            word1, word2 = struct.unpack('<HH', struct.pack('f', float(self.value)))
            conv = [word1, word2]
            if self.reverse.lower() == 'true':
                conv = [word2, word1]

        elif self.dataType == dt.BOOL:
            if self.value > 0:
                self.value = True
            else:
                self.value = False

            word1 = struct.unpack('<?', struct.pack('?', bool(self.value)))

            conv = word1

        elif self.dataType == dt.DOUBLE:

            word1, word2, word3, word4 = struct.unpack('<HHHH', struct.pack('d', float(self.value)))
            conv = [word1, word2, word3, word4]
            if self.reverse.lower() == 'true':
                conv = [word4, word3, word2, word1]

        elif self.dataType == dt.STRING:
            value = str(self.value)
            # garantees that the string length is an even number. Two caraters per register.
            string_length = len(value)
            value = [value + ' ' if int(string_length / 2) - float(string_length) / 2 != 0 else value][0]
            string_length = len(value)

            conv = struct.unpack('<' + 'H' * int(string_length / 2), struct.pack(str(string_length) + 's', str(value)))
            if self.reverse.lower() == 'true':
                conv = list(reversed(conv))

        # if the behavior returns none then valueError is True
        # to create a bad quality tag, remove the modbus datablock
        # _get_block returns an error if the block name does not exists
        # this is to create a bad quality value on the client side, if not
        # the self.value would just stay the same
        try:
            if valueError:

                # remove block if exists
                try:
                    self.unit.modbusSlave._get_block(self.modbusName)
                    self.log.warning(str(self) + "Connection failed")
                    self.unit.modbusSlave.remove_block(self.modbusName)

                # do nothing if it does not exists (_get_block error raised)
                except Exception, e:

                    self.log.warning(str(self) + " " + str(e))
                    pass
            else:

                # add block if does not exists
                try:
                    self.unit.modbusSlave._get_block(self.modbusName)

                except Exception, e:
                    self.unit.modbusSlave.add_block(self.modbusName, self.modbusType,
                                                    self.modbusStartindAddress, self.modbusLength)
                    self.log.warning(str(self) + "Connection reestablished. " + str(e))

                self.unit.modbusSlave.set_values(self.modbusName, self.modbusStartindAddress, conv)
                self.log.debug("New value from behavior: " + str(self) + " -> " + str(self.value))

        except Exception, e:
            self.log.warning(str(self) + " Modbus Error: " + str(e))

    def setBehavior(self, behaviorName, behaviorextras):

        # Set Behaviour
        # You need to add another case for a new behaviour - channel[c_behaviour].lower() == 'newBehaviourName'
        # Don't forget to import the new class on Channel.py

        behavior = Behavior.setBehavior(behaviorName, behaviorextras, self)

        if type(behavior) is bool:
            if behavior:
                self.log.error("Behavior " + str(behaviorName) + "is not configured")
                return True
        else:
            self.behavior = behavior
            self.log.debug("Channel added: " + str(self))

            return False

    # the number of registers to be used are related to the datatype
    @staticmethod
    def getNumberOfRegisterModBus(modbusdatatype):

        if modbusdatatype == "BOOL" or modbusdatatype == "SHORT" or modbusdatatype == "UNSIGNED_SHORT":
            return 1
        elif modbusdatatype == "INTEGER" or modbusdatatype == "UNSIGNED_INTEGER" or modbusdatatype == "FLOAT":
            return 2
        elif modbusdatatype == "DOUBLE":
            return 4
        elif modbusdatatype == "STRING":
            return 20

    def getLogString(self):
        return self.logHandler.getStr()

    def __str__(self):
        return "Channel: %s %s %s %s" % (self.name, self.description, self.dataType, self.behavior)
