#i2ctest.py

import smbus

import time

channel = 1

address = 0x19

reg_temp = 0x00

reg_config = 0x01

bus = smbus.SMBus(channel)

val_old = 0

i = 'A'

#val = bus.read_i2c_block_data(address,reg_config,2)
#print("Old CONFIG:",val)
#bus.write_i2c_block_data(address,reg_config,val)
#val = bus.read_i2c_block_data(address,reg_config,2)
#print("New CONFIG",val)

#val[1] = val[1] & 0b00111111
#val[1] = val[1] | (0b10 <<6)

while(i != "q"):
	i = input("Press q to quit:")
	for j in range(40):
		val = bus.read_i2c_block_data(address,reg_temp,2)
		print("Val:", val)
		val_old = val
		time.sleep(1)
