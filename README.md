# SciOx ESP32-based Project 2025 #

This is to support the Creative Coding activity at Science Oxford in early 2025.
The 5 month making experience allows for some cool and relatively complex things to be produced, 2024's was a microbit-based robot.

The current proposal is:
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
	* allow changing the SSID/Password to connect to, via the website, probably using AP access
	* do something entertaining (NeoPixels, sound effects?)
* all in a container produced by 3D printing or laser cutting

## Hardware Instructions ##

The software is configured to use:

*	A LCD1602 with a PCF8574 I2C backpack that reduces the required pin count, attached to GPIO18 (SCL) and GPIO19 (SDA), using I2C address 0x27

  	The LCD1602 backlight requires a 5V power supply. I used the 5V pin on the ESP to power the LCD backpack, and fortunately the ESP was 5V-tolerant on its pins (Wemos-style D1 MINI Pro from AliExpress). **Be cautious about applying 5V from the backpack to any of your ESP's pins!**
	
*	One or more DS18B20s, attached using the non-parasitic power mode to GPIO26, and a 4R7 resistor between VCC and the data pin, although it seems to work without it (!)

You'll have to consult your own ESP dev board instructions to work out which Dx pins are attached to which actual Espressif GPIOnn pins.
## Software Instructions ##

1.	Clone the repository or download everything onto your computer
2.	Attach the ESP32/8266 to your computer with your choice of USB data cable
   	
   	**Caution! You may need additional USB drivers for some UARTs, especially the WCH family**
  	
3.	Using something like Thonny or Mu

	 a.		Connect to the attached ESP using "Preferences|Interpreter"

  	 b.		Select the right mode (ESP32/ESP8266) in your editor, and the right serial port

   	 c.		If necessary, use the tool to install micropython on the device 

   	 d. 	Direct the tool to the downloaded folder
	 
	 e.		Edit the `uploadToEsp/NetworkCredentials.py` file to contain your network SSID/password.

	 f.		Switch focus to the `uploadToEsp/` folder, and upload the entire contents to the root of the ESP file system. The Thonny tool makes this very easy - select them, right click, upload to "/"
	 
	 g.		You now need to install the additional micropython-lib libs using `mip`. Switch focus back to the download root folder, and execute the `imstallLogging.py` script. 
	 		This will install the `logging` and additional `time` modules on the ESP for use. You should see a `lib/` directory in the ESP root folder. 
	
4.	From the download root folder, open the `main_n.m.py` file and adjust the logging settings by modifying the line `logging.basicConfig(level=logging.INFO...`, below the line `ADJUST LOG LEVEL HERE` to use whatever level you want - DEBUG is good if you want to see what's happening.
5.	With the `main_n.m.py` file open and in focus in the IDE, click on the green *Run* button on the toolbar; the main.py should be uploaded and run. 

	Depending on your dev board, 
	*	The on-board LED should flash on and off at approximately 1Hz.

	*	The LCD should show "Starting vn.m...", and then switch to showing the device's IP address on row0, and the temperature sensor(s) value(s) on row1, alternating with a display of the current heap space.
	
	**The board will not respond to commands etc. until you hit the red "Stop" button, at which point Thonny will perform a soft reset and you will regain control.**
6.	If you want to start the code running on board power-up, upload the `main_n.m.py` file onto the ESP, and rename it to `main.py`. It will then be executed on startup. If you want access to the board to modify its contents, use the red "Stop" button, and you should get command-line REPL access again.
	 
## Web Server Interface ##

The WiFiConnection component will output the assigned IP address, and it will also appear on the top line of the display. The default hostname will be "mpy-esp32.local" for ESP32, and "???" for ESP8266. Direct your browser to this location (`http://<IpAddress>`) and you should see the home page, which currently displays two gauges, one for each temperature sensor detected on the OneWire bus.
