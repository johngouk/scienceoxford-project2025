# ESP32 test script to run when you have connected your ESP32 to Thonny
import machine, sys
print('Hi, this script is running on the ESP32')
print('My ID is', machine.unique_id().hex().upper())
print()
print('Here some information about the Python interpreter I am running')
print(sys.implementation)
print()
print('You can type Python commands directly into the Shell window at the >>> prompt and I will execute them')
print('Try print("2+2=",2+2)')
