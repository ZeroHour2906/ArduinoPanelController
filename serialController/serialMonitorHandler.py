#Importing required libaries
import serial

class serialMessenger:
    """Class for handling serial monitor connection"""
    def __init__(self,timeout=0,baudrate=9600):
        """Creates object
        Parameters - None"""
        self.timeout = 0
        self.baudrate = 9600
        #Performing intal connection setup
        self.setUp(timeout,baudrate)
    
    def setUp(self,timeout,baudrate):
        """Method to create the connection to the arduinos serial monitor
        Parameters - None
        Returns - None"""
        try:
            #Attempting to connect to the Arduino 
            self.serialMonitor = serial.Serial("COM3",timeout=timeout,baudrate=baudrate)
            #If successful then the arduino is connected
            self.connected = True
        except serial.SerialException as e:
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
        
    def readMessage(self,waitBuffer=0):
        """Method to read a message from the Arduino's serial monitor
        Paramters - None
        Returns - String (The message that was read - not decoded)"""
        #Setting function variables
        message = ""
        try:
            #Checking how many bytes are in the in waiting buffer
            if self.serialMonitor.in_waiting >= waitBuffer:
                #Reading the message from the serial monitor
                message = self.serialMonitor.read_until(b"}")
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