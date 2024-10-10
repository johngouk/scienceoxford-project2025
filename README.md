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
	 
