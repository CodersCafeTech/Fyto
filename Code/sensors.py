import time
import socket
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
Moisture_channel = AnalogIn(ads, ADS.P2)
LDR_channel = AnalogIn(ads, ADS.P3)
LM35_channel = AnalogIn(ads, ADS.P1)

ADC_16BIT_MAX = 65536
lm35_constant = 10.0/1000
ads_InputRange = 4.096 #For Gain = 1; Otherwise change accordingly
ads_bit_Voltage = (ads_InputRange * 2) / (ADC_16BIT_MAX - 1)

#Initialising Variables
Moisture_Recent = 100
HighIn_DataSent = 0
LowIn_DataSent = 0
Thirsty_DataSent = 0
Savory_DataSent = 0
Happy_DataSent = 0
TemperatureDataSent = 0

# Map function
def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#Setup Client for communication
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('0.0.0.0', 1013))


while True:
    
    # Read the specified ADC channels using the previously set gain value.
    LDR_Value = LDR_channel.value
    LDR_Percent = _map(LDR_Value, 22500, 50, 0, 100)
    Moisture_Value = Moisture_channel.value
    Moisture_Percent = _map(Moisture_Value, 31000, 15500, 0, 100)
    ads_ch0 = LM35_channel.value
    ads_Voltage_ch0 = ads_ch0 * ads_bit_Voltage
    Temperature = int(ads_Voltage_ch0 / lm35_constant)
    print("Temperature = ", Temperature)
    print("Light Intensity = ", LDR_Percent)
    print("Moisture % = ", Moisture_Percent)
    if (LDR_Percent < 20):
        if(LowIn_DataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('sleep','utf-8'))
            #client.close()
            HighIn_DataSent = 0
            LowIn_DataSent = 1
    elif (LDR_Percent > 20):
        if(HighIn_DataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('happy','utf-8'))
            #client.close()
            HighIn_DataSent = 1
            LowIn_DataSent = 0
        
    if (Moisture_Percent < 10):
        Moisture_Recent = Moisture_Percent
        if(Thirsty_DataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('thirs','utf-8'))
            #client.close()
            Thirsty_DataSent = 1
            Savory_DataSent = 0
            Happy_DataSent = 0
    elif (Moisture_Percent>10 and Moisture_Recent < Moisture_Percent and Moisture_Percent < 90):
        Moisture_Recent = Moisture_Percent
        if(Savory_DataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('savor','utf-8'))
            #client.close()
            Savory_DataSent = 1
            Thirsty_DataSent = 0
            Happy_DataSent = 0
    elif (Moisture_Percent > 90):
        Moisture_Recent = Moisture_Percent
        if(Happy_DataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('savor','utf-8'))
            #client.close()
            Happy_DataSent = 1
            Savory_DataSent = 0
            Thirsty_DataSent = 0

    if(Temperature>30):
        if(TemperatureDataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('hotty','utf-8'))
            #client.close()
            TemperatureDataSent = 1
    elif(Temperature<22):
        if(TemperatureDataSent == 0):
            #client.connect(('0.0.0.0', 8080))
            client.send(bytes('freez','utf-8'))
            #client.close()
            TemperatureDataSent = 1
    else:
            TemperatureDataSent = 0
