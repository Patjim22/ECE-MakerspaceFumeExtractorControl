#!/usr/bin/env python
 
# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# LIS3DHTR
# This code is designed to work with the LIS3DHTR_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Accelorometer?sku=LIS3DHTR_I2CS#tabs-0-product_tabset-2
 
import smbus
import time
import RPi.GPIO as GPIO
 
# Get I2C bus these parameters should be specified by the pihat best way to find them is by using i2cdetect -l in terminal
buslist = [11,12,13,14,15,16,17,18]
bus = [smbus.SMBus(buslist[0]),smbus.SMBus(buslist[1]),smbus.SMBus(buslist[2]),smbus.SMBus(buslist[3]),smbus.SMBus(buslist[4]),smbus.SMBus(buslist[5]),smbus.SMBus(buslist[6]),smbus.SMBus(buslist[7])]

#This is basic config macros you can mostly ignore these or check the datasheet if you want to operate in other modes

# I2C address of the device
LIS3DHTR_DEFAULT_ADDRESS            = 0x19
LIS3DHTR_SECOND_ADDRESS             = 0x18
LIS3DHTR_SECOND_ENABLE              = 0
 
# LIS3DHTR Register Map
LIS3DHTR_REG_WHOAMI                 = 0x0F # Who Am I Register
LIS3DHTR_REG_CTRL1                  = 0x20 # Control Register-1
LIS3DHTR_REG_CTRL2                  = 0x21 # Control Register-2
LIS3DHTR_REG_CTRL3                  = 0x22 # Control Register-3
LIS3DHTR_REG_CTRL4                  = 0x23 # Control Register-4
LIS3DHTR_REG_CTRL5                  = 0x24 # Control Register-5
LIS3DHTR_REG_CTRL6                  = 0x25 # Control Register-6
LIS3DHTR_REG_REFERENCE              = 0x26 # Reference
LIS3DHTR_REG_STATUS                 = 0x27 # Status Register
LIS3DHTR_REG_OUT_X_L                = 0x28 # X-Axis LSB
LIS3DHTR_REG_OUT_X_H                = 0x29 # X-Axis MSB
LIS3DHTR_REG_OUT_Y_L                = 0x2A # Y-Axis LSB
LIS3DHTR_REG_OUT_Y_H                = 0x2B # Y-Axis MSB
LIS3DHTR_REG_OUT_Z_L                = 0x2C # Z-Axis LSB
LIS3DHTR_REG_OUT_Z_H                = 0x2D # Z-Axis MSB
 
# Accl Datarate configuration
LIS3DHTR_ACCL_DR_PD                 = 0x00 # Power down mode
LIS3DHTR_ACCL_DR_1                  = 0x10 # ODR = 1 Hz
LIS3DHTR_ACCL_DR_10                 = 0x20 # ODR = 10 Hz
LIS3DHTR_ACCL_DR_25                 = 0x30 # ODR = 25 Hz
LIS3DHTR_ACCL_DR_50                 = 0x40 # ODR = 50 Hz
LIS3DHTR_ACCL_DR_100                = 0x50 # ODR = 100 Hz
LIS3DHTR_ACCL_DR_200                = 0x60 # ODR = 200 Hz
LIS3DHTR_ACCL_DR_400                = 0x70 # ODR = 400 Hz
LIS3DHTR_ACCL_DR_1620               = 0x80 # ODR = 1.620 KHz
LIS3DHTR_ACCL_DR_1344               = 0x90 # ODR = 1.344 KHz
 
# Accl Data update & Axis configuration
LIS3DHTR_ACCL_LPEN                  = 0x00 # Normal Mode, Axis disabled
LIS3DHTR_ACCL_XAXIS                 = 0x04 # X-Axis enabled
LIS3DHTR_ACCL_YAXIS                 = 0x02 # Y-Axis enabled
LIS3DHTR_ACCL_ZAXIS                 = 0x01 # Z-Axis enabled
 
# Acceleration Full-scale selection
LIS3DHTR_BDU_CONT                   = 0x00 # Continuous update, Normal Mode, 4-Wire Interface
LIS3DHTR_BDU_NOT_CONT               = 0x80 # Output registers not updated until MSB and LSB reading
LIS3DHTR_ACCL_BLE_MSB               = 0x40 # MSB first
LIS3DHTR_ACCL_RANGE_16G             = 0x30 # Full scale = +/-16g
LIS3DHTR_ACCL_RANGE_8G              = 0x20 # Full scale = +/-8g
LIS3DHTR_ACCL_RANGE_4G              = 0x10 # Full scale = +/-4g
LIS3DHTR_ACCL_RANGE_2G              = 0x00 # Full scale = +/-2g, LSB first
LIS3DHTR_HR_DS                      = 0x00 # High-Resolution Disabled
LIS3DHTR_HR_EN                      = 0x08 # High-Resolution Enabled
LIS3DHTR_ST_0                       = 0x02 # Self Test 0
LIS3DHTR_ST_1                       = 0x04 # Self Test 1
LIS3DHTR_SIM_3                      = 0x01 # 3-Wire Interface
 
#Self Defined Regs
LIS3DHTR_INT1_SRC		    = 0x31 # Interrupt 1 source register
LIS3DHTR_INT1_CFG		    = 0x30 # Interrupt 1 configuration register
LIS3DHTR_INT1_THS                   = 0x32 # Interrupt 1 Threshold register
LIS3DHTR_INT1_DURATION              = 0x33 # Interrupt 1 Duration register
LIS3DHTR_INT1_MOTION_DETECT         = 0x0A # 6-Direction Movement Recognition

 
#LIS3DHTR Object
#most of the params are default, however some modification had to be made to allow for concurrent running with the i2cmux
#most of this was the addition of the input params like busnum, addressList and numSensors
#these allow for you to reference parts of the objects when reading the data
#there is also a try and except block on the datarate and config this prevents the error where a sensor disconnects 
#it also logs these instances, however the system should be robust enough to keep running.
#potentially could cause an issue when log file fills up, simple enough to remove however

class LIS3DHTR():
    def __init__ (self,busnum,addressList,numSensors):
        self.objaddressList = addressList
        self.numSensors = numSensors
        self.busnum = busnum
        self.select_datarate()
        self.select_data_config()
 
    def select_datarate(self):
        """Select the data rate of the accelerometer from the given provided values"""
        DATARATE_CONFIG = (LIS3DHTR_ACCL_DR_1 | LIS3DHTR_ACCL_XAXIS | LIS3DHTR_ACCL_YAXIS | LIS3DHTR_ACCL_ZAXIS)
        try:
            for i in range(self.numSensors):
                if self.objaddressList:
                    bus[self.busnum].write_byte_data(self.objaddressList[i], LIS3DHTR_REG_CTRL1, DATARATE_CONFIG)
        except:
            print("Initalization Failed")
            log.write("{0},{1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),"Sensor Failed to Initalize Despite Finding One")) #remove this line if log file fills up
            self.numSensors = 0
            self.objaddressList = []    
 
    def select_data_config(self):
        """Select the data configuration of the accelerometer from the given provided values"""
        DATA_CONFIG = (LIS3DHTR_ACCL_RANGE_2G | LIS3DHTR_BDU_CONT | LIS3DHTR_HR_DS)
        try:
            for i in range(self.numSensors):
                if self.objaddressList:
                    bus[self.busnum].write_byte_data(self.objaddressList[i], LIS3DHTR_REG_CTRL4, DATA_CONFIG)
        except:
            print("Initalization Failed")
            log.write("{0},{1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),"Sensor Failed to Initalize Despite Finding One")) #remove this line if log file fills up
            self.numSensors = 0
            self.objaddressList = []
 
    def read_accl(self):
        """Read data back from LIS3DHTR_REG_OUT_X_L(0x28), 2 bytes
        X-Axis Accl LSB, X-Axis Accl MSB"""
        xAccl = [0]*self.numSensors
        yAccl = [0]*self.numSensors
        zAccl = [0]*self.numSensors
        for i in range(self.numSensors):
            if self.objaddressList:
                print("Data Read For: ",self.busnum, "Sensor: ",i)
                data0 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_X_L)
                data1 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_X_H)
 
                xAccl[i] = data1 * 256 + data0
                if xAccl[i] > 32767 :
                    xAccl[i] -= 65536
                xAccl[i] /= 16000
                """Read data back from LIS3DHTR_REG_OUT_Y_L(0x2A), 2 bytes
                Y-Axis Accl LSB, Y-Axis Accl MSB"""
                data0 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_Y_L)
                data1 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_Y_H)
 
                yAccl[i] = data1 * 256 + data0
                if yAccl[i] > 32767 :
                    yAccl[i] -= 65536
                yAccl[i] /= 16000
                """Read data back from LIS3DHTR_REG_OUT_Z_L(0x2C), 2 bytes
                Z-Axis Accl LSB, Z-Axis Accl MSB"""
                data0 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_Z_L)
                data1 = bus[self.busnum].read_byte_data(self.objaddressList[i], LIS3DHTR_REG_OUT_Z_H)
 
                zAccl[i] = data1 * 256 + data0
                if zAccl[i] > 32767 :
                    zAccl[i] -= 65536
                zAccl[i] /= 16000
            return {'x' : xAccl, 'y' : yAccl, 'z' : zAccl}
 
from LIS3DHTR import LIS3DHTR
#reinit function
#zeros the sensor and checks the i2c if it finds a sensor, it keeps it
def SensorReinitalization(i):
        c = 0
        addressListtemp = []
        for j in range(2,120):
                try:
                    bus[i].read_byte_data(j,LIS3DHTR_REG_OUT_X_L)
                    addressListtemp.append(j)
                    c = c + 1
                    print("Sensor Found \n Bus:",i,"\n Address: ",hex(j))
                except:
                    pass
                numAddresses[i] = c
                addressList[i] = addressListtemp
        if i == 0:
            print(numAddresses[i],addressList[i])                        
        return LIS3DHTR(i,addressList[i],numAddresses[i])
    
with open("/home/Makerspace/ECE-Makerspace-Accelerometer/error_log.csv", "a") as log: #remove this line if log file fills up
    #initalization of data storage structures for enabling the LIS3DHTR
    c = 0
    addressList = []
    addressListtemp = []
    numAddresses = []
    lis3dhtr = []
    reinit_count = [0]*8
    #first intitalization loop basically runs through all the i2c ports on the pi and checks if it got a read for one if so it found a sensor
    for i in range(0,len(bus)):
        for j in range(2,120):
            try:
                bus[i].read_byte_data(j,LIS3DHTR_REG_OUT_X_L)
                addressListtemp.append(j)
                c = c + 1
                print("Sensor Found \n Bus:",i,"\n Address: ",hex(j))
            except:
                pass
        numAddresses.append(c)
        c = 0
        addressList.append(addressListtemp)
        lis3dhtr.append(LIS3DHTR(i,addressList[i],numAddresses[i]))
        addressListtemp = []

    time.sleep(1)
    #setting up tracking variables
    accl_old = []
    count = [[0]*numAddresses[0],[0]*numAddresses[1],[0]*numAddresses[2],[0]*numAddresses[3],[0]*numAddresses[4],[0]*numAddresses[5],[0]*numAddresses[6],[0]*numAddresses[7]]
    lowcount = [[0]*numAddresses[0],[0]*numAddresses[1],[0]*numAddresses[2],[0]*numAddresses[3],[0]*numAddresses[4],[0]*numAddresses[5],[0]*numAddresses[6],[0]*numAddresses[7]]
    fanOn = [[0]*numAddresses[0],[0]*numAddresses[1],[0]*numAddresses[2],[0]*numAddresses[3],[0]*numAddresses[4],[0]*numAddresses[5],[0]*numAddresses[6],[0]*numAddresses[7]]
    sensorOn = [[0]*numAddresses[0],[0]*numAddresses[1],[0]*numAddresses[2],[0]*numAddresses[3],[0]*numAddresses[4],[0]*numAddresses[5],[0]*numAddresses[6],[0]*numAddresses[7]]
    time_before_next_loop = .5
    #getting old values, so we have something to compare against on the first run
    for i in range(0,len(bus)):
        accl_old.append(lis3dhtr[i].read_accl())
    print(accl_old)
    #configuring the output pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18,GPIO.OUT)
    GPIO.output(18,GPIO.LOW)
    #the operation loop 
    #try except block allows for robustness as if a sensor disconnects it won't throw an error and stop code
    #instead it will deinit the sensor
    #basic operation is that the sensor will read a new value, compare it to the old and if the difference is greater than the threshold
    #it will add a count to the fan, if the fan gets more counts than its threshold it will turn on
    #while it is on the loop will be less frequent until the fan turns off
    while True:
        for i in range(0,len(bus)):
            try:
                accl = lis3dhtr[i].read_accl()
                print(accl,i)
                for j in range(numAddresses[i]):
                    if abs(accl_old[i]['x'][j] - accl['x'][j]) > .15 or abs(accl_old[i]['y'][j] - accl['y'][j]) > .15 or abs(accl_old[i]['z'][j] - accl['z'][j]) > .15:
                        count[i][j] += 1
                        lowcount[i][j] = 0
                        if count[i][j] > 2:
                            sensorOn[i][j] = 1
                            count[i][j] = 0
                    else:
                        count[i][j] = 0
                        lowcount[i][j] += 1
                        if lowcount[i][j] > 4:
                            sensorOn[i][j] = 0
                            lowcount[i][j] = 0
                    print(i,"Sensor: ",j,"Accels X: ",abs(accl_old[i]['x'][j] - accl['x'][j]), count[i][j],sensorOn[i][j])
                    accl_old[i] = accl                
            except:
                log.write("{0},{1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"),"Sensor"+str(i)+"Failed"))
                print("Exception Happened")
                print(accl)
                lis3dhtr[i] = SensorReinitalization(i)
                time.sleep(1)
                sensorOn[i] = [0]*lis3dhtr[i].numSensors       
            print(sensorOn)
            print(sensorOn[i])
            if 1 in  sensorOn[i]:
                print("TURN FAN ON!")
                GPIO.output(18,GPIO.HIGH)
                time_before_next_loop = 5
            else:
                #poor wording on this if but basically checks every single part of the sensorOn list for a 1
                #if theres is no 1 it will turn off
                if 1 in (item for sublist in sensorOn for item in sublist):
                    print("Fan Kept On")
                else:
                    print("Fan Turned Off")
                    GPIO.output(18,GPIO.LOW)
                    print(time_before_next_loop)
                    time_before_next_loop = .5
            #This check is here to see if a new sensor was connected/reconnected
            if accl == None:
                print("Checking", i)
                if accl_old[i]:
                    time.sleep(1)
                lis3dhtr[i] = SensorReinitalization(i)
                if lis3dhtr[i].numSensors >= 1:
                    time.sleep(1)
                    reinit_count[i] += 1
                    print("Sensor Reinitalized",reinit_count)
            time.sleep(1)
        print(time_before_next_loop)  
        time.sleep(time_before_next_loop)

