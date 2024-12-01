# SciOx ESP32-based Project 2025 #

This is to support the Creative Coding activity at Science Oxford in early 2025.
The 5 month making experience allows for some cool and relatively complex things to be produced, 2024's was a microbit-based robot.

The current proposal is:
* an ESP32
* a bunch of sensors, to be decided 
	* this one is using 2x DS18B20s on a single pin
	* the target one is a ENS160/AHT21 combo on a single dev board
* an LCD, which shows various values etc. as most recenlyt coded e.g.
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

*	Shortly, a paired ENS160, for CO2/VOC readings, and AHT21, for Temp/RH - the latter will be used to calibrate the ENS160, attached using I2C on pins 25/26

*	A pushbutton, connected to pin17, which just prints one of "Press event", "Double event" or "Long event" as appropriate on the Thonny REPL console

You'll have to consult your own ESP dev board instructions to work out which Dx pins are attached to which actual Espressif GPIOnn pins.
## Software Instructions ##

1.	Clone the repository or download everything onto your computer
2.	Attach the ESP32 to your computer with your choice of USB data cable
   	
   	**Caution! You may need additional USB drivers for some UARTs, especially the WCH family**
  	
3.	Using something like Thonny or Mu (the instructions are for Thonny)

	 a.	Connect to the attached ESP using "Preferences|Interpreter" - not sure what they are in Windows, but find the Interpreter tab!
	 
	 b.	Select the right mode (ESP32) in your editor, and the right serial port
	 
	 c.	Install micropython on the device, using the facilities of the tool (Update or Install Micropython)
	 
	 d. Adjust the Thonny View to show Files and Shell - this aids enormously with the next steps!
	 
	 e.	Direct the Files window to the downloaded folder in the This computer section of the Files window
	 
	 f.	Edit the `uploadToEsp/NetworkCredentials.py` file to contain your network SSID/password.
	 
	 g.	Switch focus to the `uploadToEsp/` folder, and upload the entire contents to the root of the ESP file system. The Thonny tool makes this very easy - select them, right click, upload to "/". You should see a list of files/folders appear in the MicroPython Device Files window - this is the root folder of the ESP32.
	 	
4.	From the download root folder in This computer, open the most recent `main_n.m.py` file and adjust the logging settings by modifying the line `logging.basicConfig(level=logging.INFO...`, below the line `ADJUST LOG LEVEL HERE` to use whatever level you want - DEBUG is good if you want to see what's happening.
5.	With the `main_n.m.py` file open and in focus in the IDE, click on the green *Run* button on the toolbar; the main.py should be uploaded and run. 

	Depending on your dev board, 
	*	The on-board LED should flash on and off at approximately 1Hz.
	*	The LCD should show "Starting vn.m..."
	*	switch to showing the device's IP address on row0, and on row1 the mode ("S" or "A") with the SSID and then Hostname for 5 seconds each
	*	switch to the sensor(s) value(s) on row1, with each sensor name/value being shown for 1 second on rotation
	
	**The board will not respond to commands etc. until you hit the red "Stop" button, at which point Thonny will perform a soft reset and you will regain control.**
6.	If you want to start the code running on board power-up, upload the `main_n.m.py` file onto the ESP, and rename it to `main.py`. It will then be executed on startup. If you want access to the board to modify its contents, use the red "Stop" button, and you should get command-line REPL access again.
	 
## Web Server Interface ##

The WiFiConnection component will output the assigned IP address, and it will also appear on the top line of the display. The default hostname will be "mpy-esp32.local" for ESP32. Direct your browser to this location (`http://<IpAddress>`) and you should see the home page, which currently displays two gauges, one for each temperature sensor detected on the OneWire bus.
	
## To Do ##
1.	Implement a central controller that 
	*	gets data/values from things and sends them to the LCD, with a rotating set of line subjects, maybe every second?
	*	receives inputs i.e. button presses, and makes appropriate changes
	*	receives web commands and takes action esp. Network Credentials set/change

2.	Make the button change the LCD displayed values, either for a short period or toggle around the options; maybe an Easter Egg for the student to programme??! Single, Long and Double presses available, could be Short - toggle round display; Double - change to something e.g. forecast?; Long - Easter egg? Restart?? 

3.	A web page to configure the SSID/Password that is accessible from the AP mode

4.	Decide on what we want to show on the LCD!

5.	Test the CO2 sensor(s)

6.	NeoPixels??

7.	Weather forecast from accuweather? Another topic to rotate on the display! Only if STA mode on local network
