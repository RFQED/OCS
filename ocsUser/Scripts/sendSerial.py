import serial

ser = serial.Serial('/dev/ttyO1')  # open serial port
print(ser.name)

for i in range(0,10):
    ser.write('hello')   #  it was b before  ser.write(b'hello')
    ser.write("\n")
    ser.write("\r")

ser.close()
