import logging


class LastLogsHandler(logging.Handler):
    def __init__(self, size):
        logging.Handler.__init__(self)
        self.strA = []
        self.i = 0
        self.len = size
        for i in range(self.len):
            self.strA.append(None)

    def emit(self, record):
        self.strA[self.i] = record
        self.i += 1
        if self.i == self.len:
            self.i = 0

    def getStr(self):
        s = ""
        for n in range(self.len):
            k = self.i - n-1
            if k < 0:
                k = k + self.len
            if self.strA[k] is not None:
                s += self.format(self.strA[k])+"\r\n"
        return s


class Verify(object):

    def __init__(self):
        pass

    @staticmethod
    def dataIntegrityServers(data):

        sdata = data[1:2]
        numrows = len(sdata)
        check = 0
        errors_str = ""

        for row in range(numrows):
            cvalue = sdata[row][3]
            for row1 in range(row + 1, numrows):
                if cvalue == sdata[row1][3]:
                    errors_str = errors_str + ("Duplicated TCP port: " + cvalue + "\nLine: " + str(row1 + 1) + "\n")
                    check = 1

        return check, errors_str

    @staticmethod
    def dataIntegrityUnits(data):
        sdata = data[1:2]
        numrows = len(sdata)
        check = 0
        errors_str = ""

        for row in range(numrows):
            cvalue = sdata[row][2]
            cunit = sdata[row][1]
            for row1 in range(row+1, numrows):
                if cvalue == sdata[row1][2] and cunit == sdata[row1][1]:
                    errors_str = errors_str + ("Duplicated unit name: " + cvalue + "\n" + "Line: " + str(row1+1) + "\n")
                    check = 1

        return check, errors_str

    @staticmethod
    def dataIntegrityChannels(data):
        # DO NOT MESS WITH ORDER
        datype_list = ['bool', 'unsigned_short', 'short', 'float', 'integer', 'unsigned_integer', 'double', 'string']
        modbustype_list = ['coils', 'discrete_inputs', 'holding_registers', 'analog_inputs']
        sdata = data[1:]

        numrows = len(sdata)
        units_id = []
        channels = []
        check = 0
        errors_str = ""

        for row in range(numrows):
            cvalue = sdata[row][2]
            cunit = sdata[row][1]

            for row1 in range(row+1, numrows):
                if cvalue == sdata[row1][2] and cunit == sdata[row1][1]:
                    errors_str = errors_str + ("Duplicated channel name: " + cvalue + "\n"
                                               + "Line: " + str(row1+1) + "\n")
                    check = 1

            # check if data types is valid
            if sdata[row][5].lower() not in datype_list:
                errors_str = errors_str + ("Data type is not valid: " + sdata[row][5] + "\n"
                                           + "Line: " + str(row+1) + "\n")
                check = 1

            if sdata[row][8].lower() not in modbustype_list:
                errors_str = errors_str + ("Modbus type is not valid: " + sdata[row][8] + "\n"
                                           + "Line: " + str(row+1) + "\n")
                check = 1

            # check if datatype is consistent with modbus datatype
            # from 0 to 2 in datatype_list length must be ==1
            if (sdata[row][5].lower() in datype_list[:2]) and sdata[row][7] != '1':
                errors_str = errors_str + ("Lenght of data not valid: " + sdata[row][7] + "\n"
                                           + "Line: " + str(row+1) + "\n")
                check = 1

            # from 3 to 4 in datatyp_list length must be == 2
            elif (sdata[row][5].lower()in datype_list[3:5]) and sdata[row][7] != '2':
                errors_str = errors_str + ("Lenght of data not valid: " + sdata[row][7] + "\n"
                                           + "Line: " + str(row+1) + "\n")
                check = 1

            elif sdata[row][5].lower() == 'double' and sdata[row][7] != '4':  # double
                errors_str = errors_str + ("Lenght of data not valid: " + sdata[row][7] + "\n"
                                           + "Line: " + str(row+1) + "\n")
                check = 1

            if sdata[row][1] != '':
                # unit_id, modbus address, modbus length
                channel = [int(sdata[row][1]), int(sdata[row][6]), int(sdata[row][7])]
                channels.append(channel)

            if sdata[row][1] != '' and int(sdata[row][1]) not in units_id:
                units_id.append(int(sdata[row][1]))  # unist

        addresses = [None] * max(units_id)  # cria lista com espaco para todas a unidades

        for unit in units_id:  # cria espaco de adressos total
            adress_size = 0
            for channel in channels:
                if unit == channel[0]:
                    if channel[2] + channel[1] > adress_size:
                        adress_size = channel[2] + channel[1]

            addresses[unit - 1] = ([None] * adress_size)

        for address in channels:
            for i in range(address[1], address[1] + address[2]):
                unit = address[0]
                if addresses[unit-1][i] != 1:
                    addresses[unit-1][i] = 1

                else:
                    errors_str = errors_str + 'Modbus address busy at: unit' + str(unit)+', address: '+str(i)+'\n'
                    check = 1

        return check, errors_str
