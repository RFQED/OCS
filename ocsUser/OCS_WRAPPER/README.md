# Generic Wrapper to interface Ignition with another subsystem

- This wrapper allows to gather data (via a python script) and transmits this data via modbus-tpc. 
    
    This wrapper created in python with an object oriented approach creates a sync. between modbus blocks of memory and predefined commands. 
    The data is acquired by predefined get commands and is written to modbus blocks and read by a client. 
    When the client writes to modbus blocks, the data is forward from modbus blocks by set commands. 
    The data in transit between the modbus and the get/set commands is store in a python like class.
    
    Client <-> Modbus <-> Wrapper (translate data) <-> Predefined Commands

    Features:
    1. Predefined commands can be implemented via scripting if there is a common structure between them, i.e. parsing, filtering etc...
    2. Predefined commands can be implemented .csv, .txt, or googleSpreadsheet (see the Configurtion1.csv file)
    3. The number of modbus registers used by a command depends only by the datatype when implemented via scripting.
    4. Modbus configuration validation - check errors
    5. Bad quality value raised in a client when a command returns a None value
    6. Developing a new wrapper depends only on the non-modbus part of the wrapper
    7. Runs in a daemon (one wrapper per machine).
    8. Different levels of logging - Debug, Info, Warning
    9. (Optional) For Ignition, an .xml file is automatically written with the channel mapping for udt usage.
    10. Developed mainly for Linux. For Windows, daemon feature needs to be disabled.
    
- Installation:
    - Install the wrapper in /opt/
    - Add /opt/Generic_Wrapper/bin to path
    - Run setup.sh to create logs files in /var/log/ with the 666 permission
        - Three levels of log files: a general with everything, a debug and a warning 
    
- Start the wrapper: wrapperStart.sh 
    - Runs on port 5555
    - A daemon is created and a temp file is created (/tmp/wrapperPID.pid) with the PID value
    - The actual command to start is "python /opt/Generic_Wrapper/wrapper.py start", but wrapperStart relies on nohup.
    
- Stop the wrapper: wrapperStop.sh
    - Kills the PID process.
    - The command is "python /opt/Generic_Wrapper/wrapper.py stop"
    
- If something goes wrong:
    - "lsof -i :5555" to get information about the PID
    - "kill -9 PID" to manually kill the PID 

## How everything works
- There are 5 classes: Wrapper, Server, Unit, Channel and Behavior.
    - Wrapper class: everything is put together here. Has one Server class .
    - Server class: is a modbus server which has a list with Unit classes.
    - Unit class: acts as a modbus address space and has a list with Channel classes.
    - Channel class: acts as a modbus block of memory. One Channel object has one Behavior. The Channel will 
        get and set the Behavior value. It's in the Channel class where the data translation takes place.
    - Behavior class: this class executes the get and set commands of what the Wrapper is interfacing to. 
  
- The wrapper.py file is where the configuration is written.    
- A for loop gets all Behaviors objects values (get commands) and writes modbus.
- Hooks callbacks to get values from modbus client and sets the value in the Behavior.
- **If the Behavior object gets a None value**, the modbus block (associated with the Channel object) is deleted until a 
    new non-None value is return. This will create a bad quality tag in the modbus client connecting to the wrapper.
     
## If you want to create a new Wrapper

##### Example 
- Assuming that you want to interface with an hardware that has 2 modules and each module has 3 channels 
    (making a total of 6 channels - quick maths), an IP and a PORT. 
    In this example a channel controls a voltage, so:
     - "channelPower" is a bool command to turn the channel on and off
     - "channelVoltage" is a float command to set and get the channel voltage
     
    The command "IP-PORT-channelPower-102-False" would turn the channel 2 in module 1 off.
    
    The command "IP-PORT-channelVoltage-001-50.01" would change the channel 1 in module 0 voltage to 50.01.
    
    The command "IP-PORT-channelVoltage-001" would get the voltage value for the channel.
    
    Given this data structure one might observe that a total of 12 modbus channels are required 
    (two modbus channels per hardware channel due to two commands per channel). **The different set and get commands
     are preformed under the Behavior respective methods.**
    
    The Wrapper gets 5 parameters to create the channels via scripting:
    - nChannels: total number of hardware channels (3*2 in this example - 3 channels per module) 
    - Behaviors: a list with Behavior name reference ("example" in this case)
        - ["example","example"]
        - this allows to have different behaviors inside the same wrapper
    - Commands: a list of list with the commands to be created and parameters to be passed onto the Behavior. 
        - [["channelPower","IP","PORT"],["channelPower","IP","PORT"]]
    - Datatypes: a list with the datatype 
        - ["BOOL","FLOAT"]
    - MBtype: the modbus function code
        - ["HOLDING_REGISTERS","HOLDING_REGISTERS"]
        
    The wrapper will create nChannels * (size of Command list) modbus locks of memory - hence 12 modbus channels.
    By default bool, short and unsigned-short takes 1 registers (2 bytes); float, integer and unsigned_integer takes
    two register (4 bytes) and double takes 4 register (8 bytes).
    The 12 modbus channels are created sequentially, respecting the number of registers given by the data type.
    The entire sequence of starting modbus addresses would be:
    [0,1,3,4,6,7,9,10,12,13,15,16]
        
    Step 1:
    - The wrapper has to know what to do with each element of the Commands list
        - Under Behaviors.py the abstract class Behavior has the method **getRealCommand** where you can properly
         concatenate the IP, PORT and command. And do some magic with the channel global ID 
         (goes from 0 to 11 in this example) that the **getRealCommand** method also gets. It's better to return a list with only one element. 
    
    Step 2:
    - The wrapper has to know how to declare the new Behavior class.
        - The abstract Behavior class has a method called **setBehavior**. Check that method. It has some other examples. 
        You're a strong and independent programmer. You can do it. 
     
    **Check the wiener_driver branch for a more complete example.**

## Dependecies (I think):

- logging.handlers
- Thread
- gspread
- ServiceAccountCredentials
- modbus_tk
- struct
- csv
- os

More info:
    https://docs.google.com/presentation/d/1GAnYu1WVZyUabQfvp0sDQXC-y3HvE99qwtfCIP4uP_Q/edit?ts=58da9b08#slide=id.g214373c5d1_0_17