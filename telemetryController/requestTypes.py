"""Classes for request messages to the server"""
#Importing required modules
import struct,telemetryController.responseTypes as responseTypes

"""Base class for creating request messages"""
class Message():
    magicPacker = struct.Struct("!c")
    magicStart = b"N"
    magicEnd = b"L"
    headPacker = struct.Struct("!HIH")
    typeName = ""

    """Method to check whether a request is valid
    Parameters - bytes - the bytes recieved from communication, msg - the Message object to build the request message into
    Returns - True if request is valid, False otherwise"""
    @classmethod
    def isValidRequest(cls,bytes,msg):
        #Getting the length of the bytes
        length = len(bytes)
        #Checking if the length if greater than or equal to 10
        if length >= 10:
            #If true then create a bytearray containg the bytes
            buffer = bytearray(bytes)
            #Getting the start and end values from the bytearray
            (startValue,) = cls.magicPacker.unpack(buffer[:1])
            (endValue,) = cls.magicPacker.unpack_from(buffer,length-1)
            #Checking if the start and end values are the same as the magic end and start values
            if cls.magicStart == startValue and cls.magicEnd == endValue:
                #If true then set the buffer attribute in the msg object to the bytearray
                msg.buffer = buffer
                return True
        #Otherwise return false
        return False
    
    """Method to build the request
    Parameters - recievedBytes - the bytes recieved from communication
    Returns - Message object if request is valid, None otherwise"""
    @classmethod
    def build(cls,recievedBytes):
        msg = Message()
        #Checking if the recieved bytes are valid
        if cls.isValidRequest(recievedBytes,msg) == True:
            #If true, pack the typeId,requestID and datas size into the message attributes
            (
                msg.typeId,msg.requestId,msg.dataSize
            ) = cls.headPacker.unpack(msg.buffer[1:9])
            #Setting the message data and the name of the request type
            msg.setData()
            msg.setName()
            #Returning the completed request
            return msg
        else:
            #Otherwise return None
            return None
    
    """Method for external class to create a request
    Parameters - recievedBytes - the bytes to be used to create the request
    Returns - The complete request or None if illegal data sent"""
    @classmethod
    def getData(cls,recievedBytes):
        #Building the message
        message = cls.build(recievedBytes)
        #Checking if a message was constructed
        if message is not None:
            #If true return the data inside the message
            return message.dataObject
        else:
            #Otherwise return None
            return None

    """Method to set data inside the request
    Parameters - None
    Returns - None"""
    def setData(self):
        self.dataObject = responseTypes.allTypes.get(self.typeId)
        self.dataObject.setData(self.buffer[9:9 + self.dataSize])

    """Method to set name of the request
    Parameters - None
    Returns - None"""
    def setName(self):
        self.typeName = self.dataObject.responseName

"""Class to create request messages"""
class BaseRequest(Message):
    def __init__(self):
        super().__init__()
        self.requestID = 0
        self.requestPacker = struct.Struct("!I")
        # self.generateBuffer()
    
    """Place holder method to generate a buffer - Will be overwritten by child classes"""
    def generateBuffer(self):
        pass

    """Method to set the Id of the request
    Parameters - id (int - the id number of the request)
    Returns - None"""
    def setRequestID(self,id):
        self.requestID = id
        #Packing the request ID into the objects buffer at position 3
        self.requestPacker.pack_into(self.buffer,3,self.requestID)

"""Class to create a request body with no data"""
class NoData(BaseRequest):
    def __init__(self):
        self.dataSize = 0
        self.packer = struct.Struct("!cHIHc")
        super().__init__()

    """Method to create a basic buffer
    Parameters - None
    Returns - None"""    
    def generateBuffer(self):
        #Creating the raw buffer to hold the basic data
        rawBuffer = self.packer.pack(
            self.magicStart,
            self.typeId,
            self.requestID,
            self.dataSize,
            self.magicEnd
        )
        #Creating a bytearray and storing it in the buffer
        self.buffer = bytearray(rawBuffer)

"""Class to create a request body with a fixed data size"""
class FixedDataSize(BaseRequest):
    def __init__(self,format,size):
        self.dataFormat = format
        self.dataSize = size
        self.packer = struct.Struct("!cHIH" + format + "c")
        self.dataPacker = struct.Struct("!" + format)
        super().__init__()
    
    """Method to create a buffer of the fixed data size
    Parameters - None
    Returns - None"""
    def generateBuffer(self):
        #Creating a byte array the length of the packer structure
        self.buffer = bytearray(self.packer.size)
        #Adding the magic starting character into the structure
        self.magicPacker.pack_into(self.buffer,0,self.magicStart)
        #Adding the type id into the buffer at index 1
        struct.pack_into("!H",self.buffer,1,self.typeId)
        #Adding the data size into the buffer at index 7
        struct.pack_into("!H",self.buffer,7,self.dataSize)
        #Adding the buffer at position 9 + the datasize and then adding the magic end
        self.magicPacker.pack_into(self.buffer,9 + self.dataSize,self.magicEnd)

class DynamicDataSize(BaseRequest):
    def __init__(self,format):
        self.dataFormat = format
        self.packer = struct.Struct("!cHIH")
        super().__init__()
    
    """Method to create the start of the buffer
    Parameters - None
    Return - None"""
    def generateBuffer(self):
        self.buffer = bytearray(self.packer.size)
        self.headBuffer = self.buffer
        #Adding the start value into the buffer at postion 0
        self.magicPacker.pack_into(self.buffer,0,self.magicStart)
        #Adding buffer and type id into the buffer
        struct.pack_into("!H",self.buffer,1,self.typeId)
    
    """Method to create the end of the buffer
    Parameters - None
    Returns - None"""
    def finishBuffer(self):
        #Adding the head buffer into position 7 and the datasize
        self.size_packer.pack_into(self.headBuffer,7,self.dataSize)
        #Creating the end buffer
        endBuffer = self.magicPacker.pack(self.magicEnd)
        #ADding the head, data and end buffer to the objects main buffer
        self.buffer = self.headBuffer + self.dataBuffer + endBuffer

"""Class to create request message for an idle message"""
class IdleMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "idle"
        self.typeId = 3
        self.generateBuffer()
    
"""Class to create request message for get version message"""
class GetVersionMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "get version"
        self.typeId = 5
        self.generateBuffer()

"""Class to create request message for get telemetry"""
class GetTelemetryMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "get telemetry"
        self.typeId = 5
        self.generateBuffer()
    
"""Class to create request message for get coaster count"""
class GetCoasterCountMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "get coaster count"
        self.typeId = 7
        self.generateBuffer()

"""Class to create request message for get current coaster and nearest station"""
class GetCurrentCoasterAndNearestStationMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "get current coaster and nearest station"
        self.typeId = 11
        self.generateBuffer()

"""Class to create request message to get the coaster name"""
class GetCoasterNameMessage(FixedDataSize):
    def __init__(self):
        super().__init__("i",4)
        self.typeName = "get coaster name"
        self.typeId = 9
        self.generateBuffer()
    
    def setCoasterIndex(self,index):
        #Setting the buffer to contain the coaster index at index 9
        self.dataPacker.pack_into(self.buffer,9,index)

"""Class to create reuqest message to set the emergency stop"""
class SetEmergencyStopMessage(FixedDataSize):
    def __init__(self):
        super().__init__("iB",5)
        self.typeName = "set emergency stop"
        self.typeId = 13
        self.generateBuffer()
    
    def setEmergencyStop(self,coasterIndex,status):
        #Adding the buffer and the coaster index, status to index 9
        self.dataPacker.pack_into(self.buffer,9,coasterIndex,status)

"""Class to create request message to get the station state"""
class GetStationStateMessage(FixedDataSize):
    def __init__(self):
        super().__init__("ii",8)
        self.typeName = "get station state"
        self.typeId = 14
        self.generateBuffer()
    
    def getStateFor(self,coasterIndex,stationIndex):
        self.dataPacker.pack_into(self.buffer,9,coasterIndex,stationIndex)

"""Class to create request message to set station dispatch mode"""
class SetStationMode(FixedDataSize):
    def __init__(self):
        super().__init__("iiB",9)
        self.typeName = "set station dispatch mode"
        self.typeId = 16
        self.generateBuffer()
    
    def setModeFor(self,coaster_index,station_index,status):
        #Adding the coaster index and station idex to position 9 in the buffer
        self.dataPacker.pack_into(self.buffer,9,coaster_index,station_index,status)

"""Class to create request message to dispatch from station"""
class DispatchMessage(GetStationStateMessage):
    def __init__(self):
        super().__init__()
        self.typeName = "station dispatch"
        self.typeId = 17
        self.generateBuffer()

"""Class to create request message to set station gates"""
class SetGatesMessage(SetStationMode):
    def __init__(self):
        super().__init__()
        self.typeName = "set station gates"
        self.typeId = 18
        self.generateBuffer()
    
"""Class to create request message to set station harness"""
class SetHarnessMessage(SetStationMode):
    def __init__(self):
        super().__init__()
        self.typeName = "set station harness"
        self.typeId = 19
        self.generateBuffer()

"""Class to create request message to set station platform"""
class SetPlatformMessage(SetStationMode):
    def __init__(self):
        super().__init__()
        self.typeName = "set station platform"
        self.typeId = 20
        self.generateBuffer()

"""Class to create request message to set station flyer"""
class SetFlyerMessage(SetStationMode):
    def __init__(self):
        super().__init__()
        self.typeName = "set station flyer"
        self.typeId = 21
        self.generateBuffer()

"""Class to create request message to quit the telemetry server"""
class QuitServerMessage(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "quit server"
        self.typeId = 26
        self.generateBuffer()

"""Class to create request message to set pause"""
class SetPauseMessage(FixedDataSize):
    def __init__(self):
        super().__init__("B",1)
        self.typeName = "set pause"
        self.typeId = 27
        self.generateBuffer()
    
    """Method to set the pause state message
    Parameters - requestState (int - 1 to pause and 0 to unpause)
    Returns - None"""
    def setPause(self,requestedState):
        self.dataPacker.pack_into(self.buffer,9,requestedState)

"""Class to create request message to select seat"""
class SelectSeatMessage(FixedDataSize):
    def __init__(self):
        super().__init__(self,"iiii",16)
        self.typeName = "select seat"
        self.typeId = 27
        self.generateBuffer()

    """Method to pack values into buffer
    Methods - coasterIndex (int - the index of the coaster), trainIndex (int - the index of the train), carIndex (int - index of the car), seatIndex (int - index of the seat)
    Returns - None"""
    def selectSeat(self,coasterIndex,trainIndex,carIndex,seatIndex):
        #Adding the coaster,train,car and seat index to the datapacker structure at index 9
        self.dataPacker.pack_into(self.buffer,9,coasterIndex,trainIndex,carIndex,seatIndex)

"""Class to create request message to recenter vr"""
class RecenterVR(NoData):
    def __init__(self):
        super().__init__()
        self.typeName = "recenter VR"
        self.typeId = 31
        self.generateBuffer()

"""Class to create request message to set custom view"""
class SetCustomViewMessage(FixedDataSize):
    def __init__(self):
        super().__init__(self,"fffffB",21)
        self.typeName = "set custom view"
        self.typeId = 32
        self.generateBuffer()
    
    """Method to pack values into buffer
    Methods - positionX (int - desired postion for the X axis), positionY (int - desired position for the Y axis), positionZ (int - desired position for the Z axis), azimuthAngle (int - desired position for the compass view), elevationAngle (int - desired position for the elevation angle), state (int - 0 for fly view, 1 for walk view)
    Return - None"""
    def setView(self,positionX,positionY,positionZ,azimuthAngle,elevationAngle,state):
        #Packing positioing data into index 9 of the buffer
        self.dataPacker.pack_into(self.buffer,9,positionX,positionY,positionZ,azimuthAngle,elevationAngle,state)