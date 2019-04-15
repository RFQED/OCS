outputDirectory = "/Users/lzosc/Desktop/MountPoint/data_V2.1/"

widthIndex = 0

#widthSetPoints = [11,10,9,8,7,6,5,4]
widthSetPoints = [29,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,12,11] #firmware v2 has different clock speeds so the width set points 
                                     #no longer corresspond to the pulse width we once knew. 

n_repeats = 4             # number of repeat measurements at each delay
nit = 500 #not sure what this is in the code, could be number of times the DRS4 is recorded from..?xxs
n = 500  # again, not sure what this does in the code, think its the same as above but for a different section of the code..? 


widthSetNph1 = [7.352e5,5.632e5,3.961e5,2.471e5,1.214e5,38010.0,3758.0,111.5]
widthSetVintg = [6375.0,7010.0,7418.0,7204.0,6343.0,5005.0,2974.0,87.0]
widthSetVctrl = [0.5212241,0.5346759,0.5530708,0.5786837,0.6194687,0.6924862,0.8621573,1.00]

calibrationSetPoints = [5,6,7,8,9,10] 

LEDWavelength_nm = 435
wavelength_nm = 435

front_side = True
rear_side = False
