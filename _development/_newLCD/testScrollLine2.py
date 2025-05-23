alwaysDisplay = "From serial:"; #The message that will always be displayed on row 1.
inputTxt = "This is a long string that will exceed 16 chars"
inputTxtLength = len(inputTxt); #Where the length of the inputTxt string is stored.
inputTxtArray = bytearray[40];

inputTxt = Serial.readString(); #Store the incoming data in "inputTxt" as a string.
inputTxtLength = inputTxt.length(); #Store the length of the string in "inputTxtLength".
lcd.clear(); #Clear the LCD screen of data from the last loop.
lcd.print(alwaysDisplay); #Print the message on row 1.
if (inputTxtLength <= 16): # #If the string is up to 16 characters we simply need to move the cursor to row 2 and print the string.
    lcd.setCursor(0,1);
    lcd.print(inputTxt);

elif (inputTxtLength > 39):
    print("This string is too long."); #Due to RAM constraints, strings longer than 39 characters
                                                                       #  are too buggy to be output to the display.
else: # #Strings longer than 16 characters, but still within RAM constraints get complicated...
    lcd.setCursor(0,1); #Move the cursor to row 2.
    inputTxt.toCharArray(inputTxtArray,40); #Convert the string stored in "inputTxt" into a character array.
    for (int i = 0; i <= 16; i++): # #For the first 16 characters, simply print them to the LCD screen.
        lcd.char(inputTxtArray[i]);
  #
  delay(1500); #Delay for 1.5 seconds so the user has time to read.
  for j in range(17, inputTxtLength+1) # #Now we begin printing from character 17 onward...
    lcd.char(inputTxtArray[j]); #Write the j-th character (for now it will be off-screen).
    lcd.shl(); #Scroll the text left one character-space.

    #This is where things get tricky, because both rows will be scrolled. But we want row 1 to remain stationary!
    lcd.setCursor(j-16,0); #Set the cursor to the first character space on the first row [visually].
                           # cursor space (0,0) has been scrolled off-screen!
    lcd.print(alwaysDisplay); #Re-print the row 1 message.
    lcd.setCursor(j+1,1); #Set the cursor one character space to the right of the last printed character on row 2.
                          #  Which is visually one character space off-screen, in preparation for the next itteration.
    delay(300); #delay for .3 seconds so the user has time to read.
