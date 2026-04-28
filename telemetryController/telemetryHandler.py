"""
Class to handle communication of telemetry data from a specific port
"""

#Importing required modules
import socket

"""Class to control the telemetry transmitter
Parameters - address (string - required address to connect to), port (int - required port to attempt to connect to), startConnect (bool - Whether to connect to the target on init - Default = True)"""
class TelTransmitter:
    def __init__(self,address,port,startConnect = True):
        self.address = address
        self.port = port
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(3)
        # Connecting if requested
        if startConnect == True:
            self.connect()
    
    """Method to connect to the address provided
    Parameters - None
    Returns - None or ConnectionRefusedError or TimeoutError"""
    def connect(self):
        try:
            #Attempting to connect to the address
            self.connection.connect((self.address,self.port))
            self.connected = True

        except (ConnectionRefusedError,TimeoutError) as e:
            self.connected = False
            return e

        except OSError:
            self.connected = True
            pass
    
    def checkConnection(self):
        """Method to check whether the object is connected
        @parameters - None
        @returns - Bool (Connected state)"""
        return self.connected
            
    """Method to disconnect from the address
    Parameters - None
    Returns - None"""
    def disconnect(self):
        try:
            #Disconnecting from the address
            self.connection.shutdown(socket.SHUT_RDWR)
            self.connection.close()
        except OSError:
            pass
        finally:
            self.connected = False
    
    """Method to send a message to the connected address
    Parameters - Message - (Bytes - The messge that is required to be sent)
    Returns - None"""
    def send(self,message):
        #Checking if the socket is connected
        if self.connected == False:
            #If false then attempt to connect
            self.connect()
        try:
            #Sending message
            self.connection.send(message)
        except ConnectionAbortedError:
            self.connected = False
    
    """Method to recieved a message from the connected address
    Parameters - bufferSize (int - size of the buffer to read on. Default = 100)
    Return - Byte (The recieved message)"""
    def recieve(self,bufferSize = 100):
        #Checking if the socket is connected
        if self.connected == False:
            #If false then attempt to connect
            self.connect()
        try:
            #Checking for message
            return self.connection.recv(bufferSize)
        except ConnectionAbortedError:
            self.connected = False

    def sendRecieve(self,message):
        """Method to send and wait for a message
        @parameters - message (The message to be sent)
        @returns - The message sent back from the address"""
        #Sending the message
        self.send(message)
        #Getting the response and returning it
        return self.recieve()
    
    """When program is closed, the connection is also closed
    Parameters - None
    Returns - None"""
    def __exit__(self):
        #Closing the connection if it was open
        if self.connected == True:
            self.disconnect()