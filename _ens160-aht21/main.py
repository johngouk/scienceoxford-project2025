from machine import I2C, Pin, UART, deepsleep, RTC, DEEPSLEEP
from ens160 import ENS160
from ahtx0 import AHT20  # Assuming AHT20 is compatible with AHT21 and supported by ahtx0 library
import time
import ubinascii

# Initialize I2C interface (adjust pins and frequency as needed)
i2c = I2C(1, scl=Pin(25), sda=Pin(26), freq=100000)

# Initialize the ENS160 sensor
sensor_ens160 = ENS160(i2c)

# Initialize the AHT21 sensor
sensor_aht21 = AHT20(i2c)

# Initialize UART for RAK3272S communication
# uart1 = UART(1, baudrate=115200, tx=Pin(17), rx=Pin(16))

# Offset for temperature adjustment (in Celsius)
temperature_offset = -10.0  # Adjust this value as needed

# Sleeptime ms
sleeptime = 60000

# Check if waking up from deep sleep
rtc = RTC()
if not (rtc.memory() == b'wakeup'):
    # Join TTN before sending data
    # join_ttn()
    rtc.memory(b'wakeup')

# Main loop to read and send sensor data
while True:
    aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating, temp_raw = sensor_ens160.read_air_quality()
    
    # Read temperature and humidity from AHT21
    temp_aht21 = sensor_aht21.temperature  # Apply offset
    rh_aht21 = sensor_aht21.relative_humidity

    # Print sensor data
    print(f"AQI: {aqi}")
    print(f"TVOC: {tvoc} ppb")
    print(f"TVOC Rating: {tvoc_rating}")
    print(f"eCO2: {eco2} ppm")
    print(f"Temperature (ENS160): {temp:.2f} °C")
    print(f"Humidity (ENS160): {rh:.2f} %")
    print(f"Temp Raw (ENS160): {temp_raw:4x}")
    print(f"eCO2 Rating: {eco2_rating}")
    print(f"Temperature (AHT21): {temp_aht21:.2f} °C")
    print(f"Humidity (AHT21): {rh_aht21:.2f} %")
        
    # Go to deep sleep and set RTC memory for wakeup
    #rtc.memory(b'wakeup')
    #deepsleep(sleeptime)  # Delay between readings
    time.sleep(5)
    

