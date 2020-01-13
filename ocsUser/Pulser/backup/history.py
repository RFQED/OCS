#            print(to_bytes(int(registers[i]) ,1,endianess='big'))
#            ser.write(to_bytes(int(registers[i]) ,1,endianess='big'))
#            time.sleep(0.1)

#        print(to_bytes(1 ,1,endianess='big'))
#        ser.write(to_bytes(1 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(20,1,endianess='big'))
#        ser.write(to_bytes(20 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(23,1,endianess='big'))
#        ser.write(to_bytes(23 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(40,1,endianess='big'))
#        ser.write(to_bytes(40 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(50,1,endianess='big'))
#        ser.write(to_bytes(50 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(26,1,endianess='big'))
#        ser.write(to_bytes(26 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(27,1,endianess='big'))
#        ser.write(to_bytes(27 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(28,1,endianess='big'))
#        ser.write(to_bytes(28 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(29,1,endianess='big'))
#        ser.write(to_bytes(29 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytets(22,1,endianess='big'))
#        ser.write(to_bytes(22 ,1,endianess='big'))
#        time.sleep(0.5)
#        print(to_bytes(11,1,endianess='big'))
#        ser.write(to_bytes(11 ,1,endianess='big'))
##        ser.write( )












#

#        try:
#            ser.write(registers)
#            print("reg value ", registers)
#        except:
#            self.txtEditDebugMsg.append("!!! FAILURE SENDING ONE REGISTER TO FPGA - port closed? !!!")
#            print("Could not send command. Port closed?")
#




#    register1Valuetmp = np.int8(22)
#    print("value of register 1 value = ", register1Valuetmp)
#    print("size of this varible in bits = ", sys.getsizeof(register1Valuetmp))
#
#    register1Valuetmp = register1Valuetmp + 1
#    print("add 1 to register1Valuet = ", register1Valuetmp)
#
#    global registerSTART, register1, register2, register3, register4, register5, register6, register7, register8, register9, registerSTOP
#    registerSTART = np.int8(1)
#    register1 = np.int8(20)
#    register2 = np.int8(23)
#    register3 = np.int8(32)
#    register4 = np.int8(5)
#    register5 = np.int8(26)
#    register6 = np.int8(27)
#    register7 = np.int8(28)
#    register8 = np.int8(29)
#    register9 = np.int8(22)
#    registerSTOP = np.int8(11)


#            ser.setDTR(1) # can try this is FPGA coms not working


#        ser.write(chr(1))
#        time.sleep(sleepTime)
#        ser.write(chr(20))
#        time.sleep(sleepTime)
#        ser.write(chr(23))
#        time.sleep(sleepTime)
#        ser.write(chr(40))
#        time.sleep(sleepTime)
#        ser.write(chr(50))
#        time.sleep(sleepTime)
#        ser.write(chr(26))
#        time.sleep(sleepTime)
#        ser.write(chr(27))
#        time.sleep(sleepTime)
#        ser.write(chr(28))
#        time.sleep(sleepTime)
#        ser.write(chr(29))
#        time.sleep(sleepTime)
#        ser.write(chr(22))
#        time.sleep(sleepTime)
#        ser.write(chr(11))
#
#
#    ser = serial.Serial('/dev/ttyO1')  # open serial port
#


#

#

#        try:
#            ser.write(registers)
#            print("reg value ", registers)
#        except:
#            self.txtEditDebugMsg.append("!!! FAILURE SENDING ONE REGISTER TO FPGA - port closed? !!!")
#            print("Could not send command. Port closed?")
#




#    register1Valuetmp = np.int8(22)
#    print("value of register 1 value = ", register1Valuetmp)
#    print("size of this varible in bits = ", sys.getsizeof(register1Valuetmp))
#
#    register1Valuetmp = register1Valuetmp + 1
#    print("add 1 to register1Valuet = ", register1Valuetmp)
#
#    global registerSTART, register1, register2, register3, register4, register5, register6, register7, register8, register9, registerSTOP
#    registerSTART = np.int8(1)
#    register1 = np.int8(20)
#    register2 = np.int8(23)
#    register3 = np.int8(32)
#    register4 = np.int8(5)
#    register5 = np.int8(26)
#    register6 = np.int8(27)
#    register7 = np.int8(28)
#    register8 = np.int8(29)
#    register9 = np.int8(22)
#    registerSTOP = np.int8(11)


#            ser.setDTR(1) # can try this is FPGA coms not working


#        ser.write(chr(1))
#        time.sleep(sleepTime)
#        ser.write(chr(20))
#        time.sleep(sleepTime)
#        ser.write(chr(23))
#        time.sleep(sleepTime)
#        ser.write(chr(40))
#        time.sleep(sleepTime)
#        ser.write(chr(50))
#        time.sleep(sleepTime)
#        ser.write(chr(26))
#        time.sleep(sleepTime)
#        ser.write(chr(27))
#        time.sleep(sleepTime)
#        ser.write(chr(28))
#        time.sleep(sleepTime)
#        ser.write(chr(29))
#        time.sleep(sleepTime)
#        ser.write(chr(22))
#        time.sleep(sleepTime)
#        ser.write(chr(11))
#
#
#    ser = serial.Serial('/dev/ttyO1')  # open serial port


#def to_bytes(n, length, endianess='big'):
#    h = '%x' % n
#    s = ('0'*(len(h) % 2 ) + h).zfill(length*2).decode('hex')
#    return s if endianess == 'big' else s[::-1]
#
#



#        ser.write("\x01")
#        time.sleep(sleepTime)
#        ser.write("\x14")
#        time.sleep(sleepTime)
#        ser.write("\x17")
#        time.sleep(sleepTime)
#        ser.write("\x28")
#        time.sleep(sleepTime)
#        ser.write("\x32")
#        time.sleep(sleepTime)
#        ser.write("\x1A")
#        time.sleep(sleepTime)
#        ser.write("\x1B")
#        time.sleep(sleepTime)
#        ser.write("\x1C")
#        time.sleep(sleepTime)
#        ser.write("\x1D")
#        time.sleep(sleepTime)
#        ser.write("\x16")
#        time.sleep(sleepTime)
#        ser.write("\x0B")

#        try:
#            for i in range(0, len(registers)):
#                ser.write(chr(registers[i]))
#                time.sleep(sleepTime)
#        except:
#            self.txtEditDebugMsg.append("!!! FAILURE SENDING ONE REGISTER TO FPGA - port closed? !!!")
#            print("Could not send command. Port closed?")
        


