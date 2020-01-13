import dataTypes as dt
from abc import ABCMeta, abstractmethod
import fpga_comms
import random

class Behavior:
    __metaclass__ = ABCMeta

    def __init__(self, channel):
        self.value = 0
        self.channel = channel

    @staticmethod
    def setBehavior(behaviorName, behaviorextras, channel):

        # Set Behaviour
        # You need to add another case for a new behaviour - channel[c_behaviour].lower() == 'newBehaviourName'

        if behaviorName.lower() == 'example':
            behavior = Bexample(behaviorextras, channel)
        elif behaviorName.lower() == 'wrappermanager':
            behavior = Bwrappermanager(behaviorextras, channel)
        elif behaviorName.lower() == 'setpoint':
            behavior = Bsetpoint(behaviorextras[0], channel)
        elif behaviorName.lower() == "bocs":
            behavior = Bocs(behaviorextras,channel)
        else:
            return True

        return behavior

    @staticmethod
    def getRealCommand(behaviorName, command, channelStructureId, globalChannelId):

        # do something to filter channel command.
        # if you want to do something about the commands
        # channelStructureId - represents the index of channels structures (nChannels index)
        # globalChannelId - the global index of the modbus channels

        nchannelperBoard = 8
        channelStructureId += 1
        module = ((channelStructureId - 1) / nchannelperBoard)
        chIndex = format(channelStructureId - module * nchannelperBoard, '02d')

        if chIndex != "01" and command == "temperatureboard":
            return None
        else:
            #print channelStructureId
            #print [str(command) + "." + str(module)+"."+chIndex]
            return [str(command) + "." + str(module)+"."+chIndex] # strings

        #return command

    @abstractmethod
    def getValue(self):
        pass


class Bsetpoint(Behavior):

    def __init__(self, setpoint, channel):

        self.channel = channel
        self.dataType = channel.dataType

        if self.dataType == dt.BOOL:
            setpoint = bool(setpoint)

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            setpoint = float(setpoint)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            setpoint = int(setpoint)

        self.setpoint = setpoint

    def getValue(self):

        self.value = self.setpoint

        if self.dataType == dt.BOOL:
            if self.value > 0:
                self.value = True
            else:
                self.value = False

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            self.value = float(self.value)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            self.value = int(self.value)

        return self.value

    def setSetpoint(self, setpoint):

        if self.dataType == dt.BOOL:
            setpoint = bool(int(setpoint))

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            setpoint = float(setpoint)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            setpoint = int(setpoint)

        self.setpoint = setpoint

    def __str__(self):
        return "Bsetpoint"


class Bexample(Behavior):

    def __init__(self, command, channel):

        self.channel = channel
        self.dataType = channel.dataType
        self.value = command[2]
        # pre defined command to use R/W values.
        # This is just an example and depends on the other protocol package

        self.command = command

    def getValue(self):

        # here is where the values from the non-modbus part comes from.
        # For example getParameterValue(self.command)
        # self.value = getParameterValue(self.command)

        if self.dataType == dt.BOOL:
            if float(self.value) >= 0.5:
                self.value = True
            else:
                self.value = False

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:

            self.value = float(self.value)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            self.value = int(self.value)

        elif self.dataType == dt.STRING:
            self.value = str(self.value)

        return self.value

    def setSetpoint(self, setpoint):

        value = setpoint
        if self.dataType == dt.BOOL:
            value = bool(int(setpoint))

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            value = float(setpoint)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            value = int(setpoint)
        elif self.dataType == dt.STRING:
            value = str(setpoint)

        self.value = value
        # use a command to write the self.value into the other protocol
        # for example writeParameterValue(self.command, self.value)

    def __str__(self):
        return "Bexample"


class Bwrappermanager(Behavior):

    def __init__(self, command, channel):

        self.channel = channel
        self.dataType = channel.dataType
        self.value = 0

        self.wrapperObj = self.channel.unit.server.wrapper
        # pre defined command to use R/W values.
        # This is just an example and depends on the other protocol package

        self.command = command[0]

    def getValue(self):

        # here is where the values from the non-modbus part comes from.
        # For example getParameterValue(self.command)
        # self.value = getParameterValue(self.command)
        self.value = self.getWrapperInfo(self.command)
        if self.dataType == dt.BOOL:
            if self.value > 0:
                self.value = True
            else:
                self.value = False

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:

            self.value = float(self.value)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            self.value = int(self.value)

        elif self.dataType == dt.STRING:
            self.value = str(self.value)

        return self.value

    def setSetpoint(self, setpoint):

        value = setpoint
        if self.dataType == dt.BOOL:
            value = bool(int(setpoint))

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            value = float(setpoint)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            value = int(setpoint)
        elif self.dataType == dt.STRING:
            value = str(setpoint)

        self.value = value
        self.controlWrapper(self.command, self.value)
        # use a command to write the self.value into the other protocol
        # for example writeParameterValue(self.command, self.value)

    def getWrapperInfo(self, parameter):
        if parameter == "totalexecutiontime":
            return self.wrapperObj.timetotalexecution
        elif parameter == "executiontimeperchannel":
            return self.wrapperObj.timeexecutionperchannel
        elif parameter == "nchannels":
            return self.wrapperObj.numberOfChannels
        elif parameter == "killwrapper":
            return self.value
        elif parameter == "lastlog":
            return self.wrapperObj.lastLog
        else:
            self.channel.log.debug("Command '" + parameter + "' not valid")

    def controlWrapper(self, parameter, value):
        if parameter == "killwrapper":
            if value:
                self.wrapperObj.stop()
                self.value = False

    def __str__(self):
        return "Bexample"


class Bocs(Behavior):

    def __init__(self, command, channel):

        self.channel = channel
        self.dataType = channel.dataType
        # pre defined command to use R/W values. This is just an example and depends on the other protocol package
        splitcommand = command[0].split(".")

        self.command = splitcommand[0]
        self.board = splitcommand[1]
        self.channel = splitcommand[2]
        self.value = 0


    def getValue(self):
    
        if self.command == "phdoutput":
          self.value = random.random()*10
        elif self.command == "temperatureboard":
            self.value = 50 + random.random()*10
        elif self.command == "ledtemperature":
            self.value = 23 + random.random()*2
          #print self.value
        if self.value is None:
            return None

        if self.dataType == dt.BOOL:
            if self.value > 0:
                self.value = True
            else:
                self.value = False

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:

            self.value = float(self.value)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            self.value = int(self.value)

        return self.value

    def setSetpoint(self, setpoint):

        value = 0
        if self.dataType == dt.BOOL:
            value = bool(int(setpoint))

        elif self.dataType == dt.DOUBLE or self.dataType == dt.FLOAT:
            value = float(setpoint)

        elif self.dataType == dt.INTEGER or self.dataType == dt.UNSIGNED_INTEGER \
                or self.dataType == dt.SHORT or self.dataType == dt.UNSIGNED_SHORT:
            value = int(setpoint)

        self.value = value
          
        if self.command == "frequency":
            print self.command
            print value
            fpga_comms.set_pulse_freq(value)
            fpga_comms.set_registers()

        elif self.command == "pulsewidth":
            print self.command
            print value
            fpga_comms.set_pulse_width(value)
            fpga_comms.set_registers()

        elif self.command == "switch":
            print self.command
            print value
            if value:
                fpga_comms.turn_on_pulsers()
                fpga_comms.set_registers()
            else:
                fpga_comms.turn_off_pulsers()
                fpga_comms.set_registers()
        
        
        # use a command to write the self.value into the other protocol
        # for example writeParameterValue(command, self.value)

    def dataTypeTranslate(self, modbusdatatype):
        return dt.type_arrays[modbusdatatype]

    def __str__(self):
        return "Bocs"


