import time
import smbus
HDC1000_CONFIG_ACQUISITION_MODE = (0x1000)


bus = smbus.SMBus(1)


bus.write_i2c_block_data(0x40, 0x02, [4])

time.sleep(0.0625) 
temp_data = bus.read_i2c_block_data(0x40, 0x00)

humi_data = bus.read_i2c_block_data(0x40, 0x01)

print(temp_data)
print(humi_data)


time.sleep(0.0625) 


bus.write_byte_data(0x40, 0x00, 0x00)
bus.write_byte(0x40, 0x00)

nd = bus.read_byte_data(0x40, 0x01)

print(nd)
