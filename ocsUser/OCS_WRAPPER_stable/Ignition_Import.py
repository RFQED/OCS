def IgnitionWrapperUdtCreator(channels_configuration, udtName, udtParentName, devicename, IgnitionChannelNamesList,
                              sshUser, sshIp):

    UDTSring = """\t<Tag name="{0}" path="" type="UDT_INST">
\t\t<Property name="Value"/>
\t\t<Property name="DataType">2</Property>
\t\t<Property name="UDTParentType">{1}</Property>
\t\t<Parameters>
\t\t\t<Property name="Device Name" type="String">{2}</Property>
\t\t\t<Property name="Host User" type="String">{3}</Property>
\t\t\t<Property name="Host Address" type="String">{4}</Property>
\t\t</Parameters>""".format(str(udtName), str(udtParentName), str(devicename), str(sshUser), str(sshIp))

    IMbChannel = """\t<Tag name="{0}" path="{1}" type="EXTENSION">
\t\t<Parameters>
\t\t\t<Property name="opc_path" type="String">{2}</Property>
\t\t</Parameters>
\t</Tag>"""

    def IgnitionTagCreator(iname, ipath, iunitId, iregtype, idatatype, iaddress):

        if iregtype == "ANALOG_INPUTS":
            iregtype = "IR"
        elif iregtype == "COILS":
            iregtype = "C"
        elif iregtype == "DISCRETE_INPUTS":
            iregtype = "DI"
        elif iregtype == "HOLDING_REGISTERS":
            iregtype = "HR"
        else:
            iregtype = "null"

        if idatatype == "BOOL":
            idatatype = ""
        elif idatatype == "BCD":
            idatatype = "BCD"
        elif idatatype == "BCD32":
            idatatype = "BCD_32"
        elif idatatype == "DOUBLE":
            idatatype = "D"
        elif idatatype == "FLOAT":
            idatatype = "F"
        elif idatatype == "INTEGER":
            idatatype = "I"
        elif idatatype == "SHORT":
            idatatype = "I"
        elif idatatype == "UNSIGNED_INTEGER":
            idatatype = "UI"
        elif idatatype == "UNSIGNED_SHORT":
            idatatype = "UI"
        elif idatatype == "STRING":
            idatatype = "S"
        else:
            idatatype = "null"

        opc_path = "[{Device Name}]"+str(iunitId)+"."+str(iregtype)+str(idatatype)+str(iaddress)
        return IMbChannel.format(str(iname), str(ipath), str(opc_path))

    tagsChannels = ""
    Imodbusindex = 0
    IChannelIndex = 1
    Imoduleindex = 0
    for channel in channels_configuration:
        if len(channel) > 0:
            unitId = channel[1]
            regtype = channel[8]
            datatype = channel[5]
            address = channel[6]
            TagName = IgnitionChannelNamesList[Imodbusindex]
            path = "LED "+str(IChannelIndex-1)
            # lentgh = channel[7]
            tagsChannels += IgnitionTagCreator(TagName, path, unitId, regtype, datatype, address) + "\n"

            Imodbusindex += 1
            if Imodbusindex >= len(IgnitionChannelNamesList):
                Imodbusindex = 0
                IChannelIndex += 1

                if IChannelIndex > 32:
                    pass
                    #Imoduleindex += 1
                    #IChannelIndex = 1

    finalfile = "<Tags>\n" + UDTSring + "\n" + tagsChannels + "\n</Tag></Tags>"

    f = open("udt_import.xml", "wb")
    f.write(finalfile)
    f.close()
