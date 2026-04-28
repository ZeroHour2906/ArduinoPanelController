# PanelController
This project is to control a NoLimits 2 simulation via a physical control panel.

The program will translate the data provided by NL2 telemetry server and transmittered though the serial monitor into an Arduino.

This project will work off the currently selected coaster in the NL2 simulation. Where each button on the panel will control a function with indicator lights to display whether a change is possible.

# Requirements
Arduino with a connection into the host computer (Serial monitor use 9600 baudrate by default).  
As many LEDs, 220 ohm resistors as wanted indicators on the panel.  
As many push buttons and "pull down" resistors (I use 1000 ohm) as desired functions on the panel.  
NL2 telemetry server running on specified port (Default is 15151).

# Dependencies
Pyserial libary.  
Arduino Json libary.

# Instructions
Wire your selected model of Arduino board into a bread board in line with the wiring diagram provided.   
Upload the sketch (panelBuilder.ino) inside the "panelBuilder" directory.   
Start NL2 on the computer that the Arduino is connected to via USB cable.   
Ensure that NL2 has a telemetry server running on port 15151.   
Once the simulation has loaded, start the "panelConnector.exe" program on the same computer.   
Wait for the program to start and then your panel will start working.
To exit the program press CTRL + C in the terminal.

# Known issues
## Issue 1
If the next block is clear, gates closed but with the harnesses open when closing harness may cause dispatch lights not to flash and both close and open harness to flash. To solve this cycle the gates or close the harness before the gates.

## Issue 2
When connecting the board after NL2 and the connector program have been running the panel may become unresponsive to fix this change the state of the station to resume normal operation