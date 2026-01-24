"""
Class to handle communication of telemetry data from a specific port
"""

#Importing required modules
import socket

"""Class to control the telemetry transmitter
Parameters - address (string - required address to connect to), port (int - required port to attempt to connect to)"""
class TelTransmitter:
    def __init__(self,address,port):
        self.address = address
        self.port = port
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(3)
        self.connect()
    
    """Method to connect to the address provided
    Parameters - None
    Returns - None"""
    def connect(self):
        try:
            #Attempting to connect to the address
            self.connection.connect((self.address,self.port))
            self.connected = True
        except ConnectionRefusedError:
            self.connected = False
        
        except TimeoutError:
            self.connected = False
    
    """Method to disconnect from the address
    Parameters - None
    Returns - None"""
    def disconnect(self):
        #Disconnecting from the address
        self.connection.shutdown(socket.SHUT_RDWR)
        self.connection.close()
        self.connected = False
    
    """Method to send a message to the connected address
    Parameters - Message - (Bytes - The messge that is required to be sent)
    Returns - None"""
    def send(self,message):
        #Checking if the socket is connected
        if self.connected == False:
            #If false then attempt to connect
            self.connect()
        #Sending message
        self.connection.send(message)
    
    """Method to recieved a message from the connected address
    Parameters - bufferSize (int - size of the buffer to read on. Default = 100)
    Return - Byte (The recieved message)"""
    def recieve(self,bufferSize = 100):
        #Checking if the socket is connected
        if self.connected == False:
            #If false then attempt to connect
            self.connect()
        #Checking for message
        return self.connection.recv(bufferSize)

    def sendRecieve(self,message):
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