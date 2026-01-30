#Importing required libaries
import serial
import serial.tools.list_ports

class serialMessenger:
    """Class for handling serial monitor connection"""
    def __init__(self,timeout=0,baudrate=9600):
        """Creates object
        Parameters - timeout (int - The timeout on the read/write operations (Default = 0)), baudrate (int - The bit rate of the serial monitor (Default = 9600))"""
        self.timeout = 0
        self.baudrate = 9600
        #Performing intal connection setup
        self.setUp(timeout,baudrate)
    
    def findArduinoPort(self):
        """Method to find which port the Arduino is connected to
        Parameters - None
        Returns - String (The port that the Arduino is connected to or empty if not connected)"""
        #Looping over all the ports on the device
        for port in serial.tools.list_ports.comports():
            #Checking if the port is connected to an arduino
            if "Arduino" in port.description or "CH340" in port.description:
                #Returning the port if one was found
                return port.device
        #Else return empty string
        return ""
    
    def setUp(self,timeout,baudrate):
        """Method to create the connection to the arduinos serial monitor
        Parameters - timeout (int - The timeout on the read/write operations (Default = 0)), baudrate (int - The bit rate of the serial monitor (Default = 9600))
        Returns - None"""
        try:
            #Attempting to connect to the Arduino 
            self.serialMonitor = serial.Serial(self.findArduinoPort(),timeout=timeout,baudrate=baudrate)
            #If successful then the arduino is connected
            self.connected = True
        except serial.SerialException:
            #If exception is raised then no arduino is connected
            self.connected = False
    
    def shutDown(self):
        """Method to disconnect from the Arduino serial monitor
        Paramters - None
        Returns - None"""
        #Closing the connection
        try:
            self.serialMonitor.close()
            #Deleting the serial monitor variable
            del self.serialMonitor
        except AttributeError:
            #If exception occured then no connection to the serial montior was found at serial monitor shutdown, continuing on with program
            pass
        #Setting the connected variable to false
        self.connected = False
    
    def __exit__(self):
        """When program is closed - close the connection"""
        self.shutDown()
    
    def checkConnection(self):
        return self.connected
    
    def sendMessage(self,command):
        """Method to send a message to the arduinos serial monitor
        Parameters - string: command (The command desired to be sent)
        Returns - None"""
        #Encoding command
        encodedMessage = str.encode(command)
        # encodedMessage = json.dumps(command)
        try:
            #Injecting message into serial monitor
            self.serialMonitor.write(encodedMessage)
        except serial.SerialException:
            #If execption is raised then no Arduino connected
            self.connected = False
            #Attempting setup again
            self.setUp(self.timeout,self.baudrate)
        except AttributeError:
            #If exeception is raised means that there was no arduino connected during setup or setup was never called
            self.setUp(self.timeout,self.baudrate)
        
    def readMessageUntil(self,terminatingCharacter,waitBuffer=0):
        """Method to read a message from the Arduino's serial monitor
        Paramters - terminatingChracters (Bytes - what character to readuntil), waitBuffer (int - the amount of characters that need to be in buffer until read operation is performed (Default = 0))
        Returns - Byte (The message that was read - not decoded)"""
        #Setting function variables
        message = ""
        try:
            #Checking how many bytes are in the in waiting buffer
            if self.serialMonitor.in_waiting >= waitBuffer:
                #Reading the message from the serial monitor
                message = self.serialMonitor.read_until(terminatingCharacter)
        except serial.SerialException:
            #If execption is raised then no Arduino is connected
            self.connected = False
            #Attempting setup again
            self.setUp(self.timeout,self.baudrate)
        except AttributeError:
            #If exception is raised means that there was no Arduino connected during setup or setup function was never called
            self.setUp(self.timeout,self.baudrate)
        
        #Returning the message
        return message

    def readMessage(self,waitBuffer=0):
        """Method to read message from the Arduino's serial monitor
        Parameters - waitBuffer (int - the amount of characters that need to be in the buffer until read operation is peformed (Default = 0))
        Returns - Byte (The message that was read - not decoded)"""
        #Setting the function variables
        message = ""
        try:
            #Checking how many bytes are in the waitng buffer
            if self.serialMonitor.in_waiting >= waitBuffer:
                #Reading the message from the serial monitor
                message = self.serialMonitor.read()
        except serial.SerialException:
            #If exception is raised then Arduino is not connected
            self.connected = False
            #Attempting setup again
            self.setUp(self.timeout,self.baudrate)
        except AttributeError:
            #If exception is raised means that there was no Arduino found during setup
            self.setUp(self.timeout,self.baudrate)
        
        #Returning the found message
        return message