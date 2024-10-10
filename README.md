# SciOx ESP32-based Project 2025 #

This is to support the Creative Coding activity at Science Oxford in early 2025.
The 5 month making experience allows for some cool and relatively complex things to be produced, 2024's was a microbit-based robot.

* an ESP32
* a bunch of sensors, to be decided 
	* this one is using 2x DS18B20s on a single pin
* an LCD, which shows
	* IP address
	* alternately GC mem_free, and sensor output
* a webserver, with all the html/js/css loaded on to the ESP32
* one or more Buttons, which could include
	* change the display
	* reset everything
	* allow changing the SSID/Password to connect to
	* do something entertaining (NeoPixels, sound effects?)
* all contained a box or something produced by 3D printing or laser cutting

## Hardware Instructions ##

The software is configured to use:

*	A LCD1602 with a PCF8574 I2C backpack that reduces the required pin count, attached to GPIO18 (SCL) and GPIO19 (SDA), using I2C address 0x27

  	The LCD1602 backlight requires a 5V power supply. I used the 5V pin on the ESP to power the LCD backpack, and fortunately the ESP was 5V-tolerant on its pins (Wemos-style D1 MINI Pro from AliExpress). **Be cautious about applying 5V from the backpack to any of your ESP's pins!**
	
*	One or more DS18B20s, attached using the non-parasitic power mode to GPIO26

You'll have to consult your own ESP dev board instructions to work out which Dx pins are attached to which actual Espressif GPIOnn pins.
## Software Instructions ##

1.	Clone the repository or download everything onto your computer
2.	Attach the ESP32/8266 to your computer with your choice of USB cable
   	
   	**Caution! You may need additional USB drivers for some UARTs, especially the WCH family**
  	
4.	Using something like Thonny or Mu

	 a.		Connect to the attached ESP

  	 b.		Select the right mode (ESP32/ESP8266) in your editor

   	 c.		If necessary, use the tool to install micropython on the device 

   	 d. 		Direct the tool to the downloaded folder
	 
	 e.		Edit the 'NetworkCredentials' file to contain your network SSID/password.

	 f.		From download folder, upload the following files/directories to the root of the ESP file system. The Thonny tool makes this very easy - select them, right click, upload to "/"
	

		sensors/
		webdocs/
		ESP32LogRecord.py
		LCD.py
		NetworkCredentials.py
		RequestParser.py
		ResponseBuilder.py
		WebServer.py
		WiFiConnection.py
		ds18b20.py
		esp8266_i2c_lcd.py
		flashLed.py
		lcd_api.py
		main.py
		printMem.py
	 
	 g.		Restarting the ESP will run the "main.py"; the logging settings can be adjusted in this file, by modifying line 21 `logging.basicConfig(level=logging.INFO...` to use whatever level you want - DEBUG is good of you want to see what's happening.
	 
## Web Server Interface ##

The WiFiConnection component will output the assigned IP address, and it will also appear on the top line of the display. The default hostname will be "mpy-esp32.local" for ESP32, and "???" for ESP8266. Direct your browser to this location (`http://<IpAddress>`) and you should see the home page. If your sensor(s) is/are connected then the temperatures should show on the bottom line, alternating with the gc.mem_free() output. 
