#!/usr/bin/env python
 
# Distributed with a free-will license.
# Use it any way you want, profit or free, provided it fits in the licenses of its associated works.
# LIS3DHTR
# This code is designed to work with the LIS3DHTR_I2CS I2C Mini Module available from ControlEverything.com.
# https://www.controleverything.com/content/Accelorometer?sku=LIS3DHTR_I2CS#tabs-0-product_tabset-2
 
import smbus
import time
import RPi.GPIO as GPIO
 
# Get I2C bus
bus = smbus.SMBus(1)
 
# I2C address of the device
LIS3DHTR_DEFAULT_ADDRESS            = 0x19
LIS3DHTR_SECOND_ADDRESS             = 0x18
 
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
 
 
 
class LIS3DHTR():
    def __init__ (self):
        self.select_datarate()
        self.select_data_config()
 
    def select_datarate(self):
        """Select the data rate of the accelerometer from the given provided values"""
        DATARATE_CONFIG = (LIS3DHTR_ACCL_DR_10 | LIS3DHTR_ACCL_XAXIS | LIS3DHTR_ACCL_YAXIS | LIS3DHTR_ACCL_ZAXIS)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_CTRL1, DATARATE_CONFIG)
        bus.write_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_CTRL1, DATARATE_CONFIG)
 
    def select_data_config(self):
        """Select the data configuration of the accelerometer from the given provided values"""
        DATA_CONFIG = (LIS3DHTR_ACCL_RANGE_2G | LIS3DHTR_BDU_CONT | LIS3DHTR_HR_DS)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_CTRL4, DATA_CONFIG)
        bus.write_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_CTRL4, DATA_CONFIG)
 
    def read_accl1(self):
        """Read data back from LIS3DHTR_REG_OUT_X_L(0x28), 2 bytes
        X-Axis Accl LSB, X-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_X_L)
        data1 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_X_H)
 
        xAccl = data1 * 256 + data0
        if xAccl > 32767 :
            xAccl -= 65536
        xAccl /= 16000
        """Read data back from LIS3DHTR_REG_OUT_Y_L(0x2A), 2 bytes
        Y-Axis Accl LSB, Y-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_Y_L)
        data1 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_Y_H)
 
        yAccl = data1 * 256 + data0
        if yAccl > 32767 :
            yAccl -= 65536
        yAccl /= 16000
        """Read data back from LIS3DHTR_REG_OUT_Z_L(0x2C), 2 bytes
        Z-Axis Accl LSB, Z-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_Z_L)
        data1 = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_REG_OUT_Z_H)
 
        zAccl = data1 * 256 + data0
        if zAccl > 32767 :
            zAccl -= 65536
        zAccl /= 16000
        return {'x' : xAccl, 'y' : yAccl, 'z' : zAccl}

    def read_accl2(self):
        """Read data back from LIS3DHTR_REG_OUT_X_L(0x28), 2 bytes
        X-Axis Accl LSB, X-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_X_L)
        data1 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_X_H)

        xAccl = data1 * 256 + data0
        if xAccl > 32767 :
            xAccl -= 65536
        xAccl /= 16000
        """Read data back from LIS3DHTR_REG_OUT_Y_L(0x2A), 2 bytes
        Y-Axis Accl LSB, Y-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_Y_L)
        data1 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_Y_H)

        yAccl = data1 * 256 + data0
        if yAccl > 32767 :
            yAccl -= 65536
        yAccl /= 16000
        """Read data back from LIS3DHTR_REG_OUT_Z_L(0x2C), 2 bytes
        Z-Axis Accl LSB, Z-Axis Accl MSB"""
        data0 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_Z_L)
        data1 = bus.read_byte_data(LIS3DHTR_SECOND_ADDRESS, LIS3DHTR_REG_OUT_Z_H)

        zAccl = data1 * 256 + data0
        if zAccl > 32767 :
            zAccl -= 65536
        zAccl /= 16000
        return {'x' : xAccl, 'y' : yAccl, 'z' : zAccl}
 
    def enable_INT1(self):
        """Enables the motion interrupt for reading motion"""
        CTRL_REG3_CONF = 0x40
        INT1_CONFIG = 0x0A  # (LIS3DHTR_INT1_MOTION_DETECT)
        print(bin(INT1_CONFIG))
        CTRL_REG5_CONF = 0x08
        INT1_THRESH = 0x04
        INT1_DURATION = 0x0A
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS,LIS3DHTR_REG_CTRL3,CTRL_REG3_CONF)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS,LIS3DHTR_REG_CTRL5,CTRL_REG5_CONF)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS,LIS3DHTR_INT1_THS,INT1_THRESH)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS,LIS3DHTR_INT1_DURATION,INT1_DURATION)
        bus.write_byte_data(LIS3DHTR_DEFAULT_ADDRESS,LIS3DHTR_INT1_CFG,INT1_CONFIG)


    def read_INT1(self):
        """Reads the SRC Register"""
        data = bus.read_byte_data(LIS3DHTR_DEFAULT_ADDRESS, LIS3DHTR_INT1_SRC)
        return data
 
from LIS3DHTR import LIS3DHTR
lis3dhtr = LIS3DHTR()
 
lis3dhtr.select_datarate()
lis3dhtr.select_data_config()
lis3dhtr.enable_INT1()
print(bin(lis3dhtr.read_INT1()))
time.sleep(1)
accl_old1 = lis3dhtr.read_accl1()
accl_old2 = lis3dhtr.read_accl2()
count1 = 0
count2 = 0
lowcount1 = 0
lowcount2 = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(23,GPIO.IN)
GPIO.setup(18,GPIO.OUT)
GPIO.output(18,GPIO.LOW)
while True:
    #print(bin(lis3dhtr.read_INT1()))
    accl1 = lis3dhtr.read_accl1()
    accl2 = lis3dhtr.read_accl2()
    print(abs(accl_old1['z'] - accl1['z']),abs(accl_old1['y'] - accl1['y']))
    if abs(accl_old1['x'] - accl1['x']) > .10 or abs(accl_old1['y'] - accl1['y'])>.10:
       count1 += 1
       lowcount1 = 0
       lowcount2 = 0
       if count1 > 2 : 
           print("TURN FAN ON!")
           count1 = 0
           GPIO.output(18,GPIO.HIGH)
           time.sleep(25)
    else:
       count1 = 0
       lowcount1 += 1
    print(count1)
    print(abs(accl_old2['x'] - accl2['x']),abs(accl_old2['y'] - accl2['y']))
    if abs(accl_old2['x'] - accl2['x']) > .10 or abs(accl_old2['y'] - accl2['y'])>.10:
       count2 += 1
       lowcount2 = 0
       lowcount1 = 0
       if count2 > 2 :
           print("TURN FAN ON!")
           count2 = 0
           GPIO.output(18,GPIO.HIGH)
           print("Sleeping")
           time.sleep(25)
           print("Sleeping")
           
    else:
       count2 = 0
       lowcount2 += 1

    if lowcount2 > 4 or lowcount1 > 4:
       print("Fan Turned Off")
       GPIO.output(18,GPIO.LOW)
       lowcount2 = 0
       lowcount1 = 0

    print(count2)
    accl_old1 = accl1
    accl_old2 = accl2
    print("Acceleration in X-Axis : %f" %(accl2['x']))
    print("Acceleration in Y-Axis : %f" %(accl2['y']))
    print("Acceleration in Z-Axis : %f" %(accl2['z']))
    print(" ************************************ ")
    time.sleep(2)

