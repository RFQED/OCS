#outputDirectory = "/Users/lzosc/Desktop/MountPoint/data_V2.1/"
outputDirectory = "/Users/lzosc/Desktop/RefactoredDataStore/"

widthIndex = 0

#debug
#widthSetPointsLarge = [11,15]
#widthSetPointsSmall = [1,5,59,63]

#SUPER FAST SCAN
#widthSetPointsLarge = [11,12,13,14,15]
#widthSetPointsSmall = [1,5,9,13,17,21,27,31,35,39,43,47,51,55,59,63]

#FAST SCAN
#widthSetPointsLarge = [11,12,13,14,15]
#widthSetPointsSmall = [1,3,5,7,9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39,41,43,45,47,49,51,53,55,57,59,61,63]


# SLOW SCAN
widthSetPointsLarge = [10,11,12,13,14,15,16,17,18,19]
widthSetPointsSmall = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64]


n_repeats = 2             # number of repeat measurements at each delay
nit = 500 #not sure what this is in the code, could be number of times the DRS4 is recorded from..?xxs
n = 500  # again, not sure what this does in the code, think its the same as above but for a different section of the code..? 
numPointsToTake = 500 #renamed from n

calibrationSetPoints = [10,11,12,13,14,15,16,17,18,19,20] # maybe need more 

LEDWavelength_nm = 435
wavelength_nm = 435

front_side = True
rear_side = False

sleepTime = 5
