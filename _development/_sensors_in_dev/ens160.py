from machine import I2C
from micropython import const


class ENS160:
    # register values
    # Taken from datasheet https://www.sciosense.com/wp-content/uploads/2023/12/ENS160-Datasheet.pdf
    ENS160_PARTID		= const(0x0160)
    
    ENS160_REG_PART_ID 	= const(0x00) # 1 reg
    ENS160_REG_OPMODE 		= const(0x10) # 1 reg
    ENS160_REG_CONFIG 		= const(0x11) # 1 reg
    ENS160_REG_COMMAND 	= const(0x12) # 1 reg
    ENS160_REG_TEMP_IN 	= const(0x13) # 2 regs
    ENS160_REG_RH_IN 		= const(0x15) # 2 regs
    ENS160_REG_DATA_STATUS = const(0x20) # 1 reg
    ENS160_REG_DATA_AQI 	= const(0x21) # 1 reg
    ENS160_REG_DATA_TVOC 	= const(0x22) # 2 regs
    ENS160_REG_DATA_ETOH 	= const(0x22) # 2 regsDatasheet: "This 2-byte register reports the calculated ethanol concentration in ppb. For dual use the DATA_ETOH register is a virtual mirror of the ethanol-calibrated DATA_TVOC register."
    ENS160_REG_DATA_ECO2 	= const(0x24) # 2 regs
    ENS160_REG_DATA_T 		= const(0x30) # 2 regs
    ENS160_REG_DATA_RH 	= const(0x32) # 2 regs
    ENS160_REG_DATA_MISR 	= const(0x38) # 1 reg
    ENS160_REG_GPR_WRITE 	= const(0x40) # 8 regs
    ENS160_REG_GPR_READ 	= const(0x48) # 8 regs
    
    ENS160_COMMAND_NOP			= const(0x00)
    ENS160_COMMAND_GET_APPVER 	= const(0x0E)
    ENS160_COMMAND_CLRGPR 		= const(0xCC)

    ENS160_MODE_DEEPSLEEP 	= const(0x00)
    ENS160_MODE_IDLE 		= const(0x01)
    ENS160_MODE_STANDARD 	= const(0x02)
    ENS160_MODE_RESET 		= const(0xF0)
  
    ENS160_STATUS_NORMAL	= const(0)	# Normal operation
    ENS160_STATUS_WARMUP	= const(1)	# Warm-Up phase
    ENS160_STATUS_STARTUP	= const(2)	# Initial Start-Up phase
    ENS160_STATUS_INVALID	= const(3)	# Initial Start-Up phase
    ENS160_STATUS_TEXT = [const("Normal operation"), const("Warm-Up phase"),
                       const("Initial Start-Up phase"), const("Initial Start-Up phase")]

    def __init__(self, i2c, address=0x53):
        self.i2c = i2c
        self.address = address
        self.part_id = self.get_id()
        self.set_mode(ENS160_MODE_STANDARD)

    def _read_register(self, reg, length):
        return self.i2c.readfrom_mem(self.address, reg, length)

    def _write_register(self, reg, data):
        self.i2c.writeto_mem(self.address, reg, data)

    def set_mode(self, mode):
        self._write_register(ENS160_REG_OPMODE, bytes([mode]))  # Operating Mode
        
    def _clear(self):
        self._write_register(ENS160_REG_COMMAND, bytes([ENS160_COMMAND_NOP]));
        self._write_register(ENS160_REG_COMMAND, bytes([ENS160_COMMAND_CLRGPR]));


    def get_id(self):
        data = self._read_register(ENS160_REG_PART_ID, 2)  # Device Identity
        return (data[1] << 8) | data[0]

    # FW version is provided via
    #	- OPMODE in IDLE
    #	- Write COMMAND reg with 0x0E: ENS160_COMMAND_GET_APPVER – Get FW Version
    #	- Read ENS160_REG_GPR_READ for GPR_READ4 (Version Major), GPR_READ5(Version Minor), GPR_READ6(Version Release)
    def get_firmware_version(self):
        self._clear()
        self._write_register(ENS160_REG_COMMAND, bytes([ENS160_COMMAND_GET_APPVER]))
        data = self._read_register(ENS160_REG_GPR_READ, 8)  # GPR READ
        # Good stuff in regs 4, 5, 6
        version = f'{data[4]}.{data[5]}.{data[6]}'
        return version

    def get_status(self):
        data = self._read_register(ENS160_REG_DATA_STATUS, 1)  # Operating Mode
        self._validity = data[0] >> 2 & 3 # bits 3:2 0 Normal, 1 Warmup, 2 Initial Startup, 3 Invalid
        self._newgpr = data[0] & 1 # bit 0 - new data available in GPR_READx
        self._newdat = data[0] >> 1 & 1 # bit 1 - new data available in DATA_x
        self._stater = data[0] >> 6 & 1 # bit 6 - error indicator
        self._statas = data[0] >> 7 & 1 # bit 7 - OPMODE running
        return data[0]
    
    def get_aqi(self):
        data = self._read_register(ENS160_REG_DATA_AQI, 1)  # Air Quality Index
        aqi_uba = data[0] & 0x07  # Extract the lower 3 bits
        return aqi_uba
    
    def get_tvoc(self):
        data = self._read_register(ENS160_REG_DATA_TVOC, 2)  # TVOC Concentration (ppb)
        tvoc = (data[1] << 8) | data[0]  # LSB first, then MSB
        return tvoc

    def get_eco2(self):
        data = self._read_register(ENS160_REG_DATA_ECO2, 2)  # Equivalent CO2 Concentration (ppm)
        eco2 = (data[1] << 8) | data[0]  # LSB first, then MSB
        return eco2

    def get_temperature(self):
        data = self._read_register(ENS160_REG_DATA_T, 2)  # Temperature used in calculations
        temp_raw = (data[1] << 8) | data[0]
        temp_kelvin = temp_raw / 64.0
        temp_celsius = temp_kelvin - 273.15
        return temp_celsius, temp_raw

    def get_humidity(self):
        data = self._read_register(self.ENS160_REG_DATA_RH, 2)  # Relative Humidity used in calculations
        rh_raw = (data[1] << 8) | data[0]
        rh = rh_raw / 512.0  # Assuming the format is the same as ENS21x: RH% * 512
        return rh

    def interpret_eco2_level(self, eco2):
        if eco2 > 1500:
            return "Bad - Heavily contaminated indoor air / Ventilation required"
        elif eco2 > 1000:
            return "Poor - Contaminated indoor air / Ventilation recommended"
        elif eco2 > 800:
            return "Fair - Optional ventilation"
        elif eco2 > 600:
            return "Good - Average"
        elif eco2 >= 400:
            return "Excellent - Target level"
        else:
            return "Unknown"

    def interpret_tvoc_level(self, tvoc):
        if tvoc <= 50:
            return "Excellent"
        elif tvoc <= 100:
            return "Good"
        elif tvoc <= 150:
            return "Moderate"
        elif tvoc <= 200:
            return "Unhealthy"
        elif tvoc <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"

    def measure():
        data = self._read_register(ENS160_REG_DATA_AQI, 7)  # Read AQ data
        aqi = data[0] & 0x07
        tvoc = (data[2] << 8) | data[1]
        eco2 = (data[4] << 8) | data[3]
        return aqi, tvoc, eco2

    def read_air_quality(self):
        aqi = self.get_aqi()
        tvoc = self.get_tvoc()
        eco2 = self.get_eco2()
        temp, temp_raw = self.get_temperature()
        rh = self.get_humidity()
        eco2_rating = self.interpret_eco2_level(eco2)
        tvoc_rating = self.interpret_tvoc_level(tvoc)
        self.get_status() # get the current status mode values
        return self.ENS160_STATUS_TEXT[self._validity],aqi, tvoc, eco2, temp, rh, eco2_rating, tvoc_rating

    def set_envdata(self, t, h):
        treg = round((t+273.15)*64.0)
        tb = treg.to_bytes(2,'little')
        rhreg = round(h * 512.0)
        rb = rhreg.to_bytes(2,'little')
        b = bytearray()
        b[0:1] = tb
        b[2:3] = rb
        print(b)
        self._write_register(self.ENS160_REG_TEMP_IN, b)