import struct

allTypes = {}

class Response:
    responseName = ""
    
    def setData(self,data):
        self.dataArray = data
        self.setAttributes()
    
    def setAttributes(self):
        pass

class OkData(Response):
    responseName = "ok"
    responseFormat = ""

allTypes[1] = OkData()

class ErrorData(Response):
    responseName = "error"
    responseFormat = ""

    def setAttributes(self):
        self.text = self.dataArray.decode("utf-8")

allTypes[2] = ErrorData()

class VersionData(Response):
    responseName = "version"
    responseFormat = "!bbbb"
    packer = struct.Struct(responseFormat)

    def setAttributes(self):
        (
            self.main,
            self.minor,
            self.revision,
            self.build,
        ) = self.packer.unpack(self.dataArray)

allTypes[4] = VersionData()

class TelemetryData(Response):
    responseName = "telemetry"
    responseFormat = "!iiiiiiiifffffffffff"
    packer = struct.Struct(responseFormat)

    def setAttributes(self):
        (
            state,
            self.rendered_frame,
            self.view_mode,
            self.current_coaster,
            self.coaster_style_id,
            self.current_train,
            self.current_car,
            self.current_seat,
            self.speed,
            self.position_x,
            self.position_y,
            self.position_z,
            self.rotation_quaternion_x,
            self.rotation_quaternion_y,
            self.rotation_quaternion_z,
            self.rotation_quaternion_w,
            self.gforce_x,
            self.gforce_y,
            self.gforce_z,
        ) = self.packer.unpack(self.dataArray)
        self.in_play_mode = isSet(state,0)
        self.braking = isSet(state,1)
        self.paused = isSet(state,2)

allTypes[6] = TelemetryData()

class IntValueData(Response):
    responseName =  "int value"
    responseFormat = "!i"
    packer = struct.Struct(responseFormat)

    def setAttributes(self):
        (
            self.value,
        ) = self.packer.unpack(self.dataArray)

allTypes[8] = IntValueData()

class StringMessage(Response):
    responseName = "String Message"
    responseFormat = ""

    def setAttributes(self):
        self.value = self.dataArray.decode("utf-8")

allTypes[10] = StringMessage()

class IntValuePair(Response):
    responseName = "int value pair"
    responseFormat = "!ii"
    packer = struct.Struct(responseFormat)

    def setAttributes(self):
        (
            self.value0,
            self.value1
        ) = self.packer.unpack(self.dataArray)
    
allTypes[12] = IntValuePair()

class StationState(Response):
    responseName = "station state"
    responseFormat = "!I"
    packer = struct.Struct(responseFormat)

    def setAttributes(self):
        (integer, ) = self.packer.unpack(self.dataArray)

        self.e_stop = isSet(integer,0)
        self.manualDispatch = isSet(integer,1)
        self.canDispatch = isSet(integer,2)
        self.canCloseGates = isSet(integer,3)
        self.canOpenGates = isSet(integer,4)
        self.canCloseHarness = isSet(integer,5)
        self.canOpenHarness = isSet(integer,6)
        self.canRaisePlatform = isSet(integer,7)
        self.canLowerPlatform = isSet(integer,8)
        self.canLockFlyer = isSet(integer,9)
        self.canUnlockFlyer = isSet(integer,10)
        self.trainInStation = isSet(integer,11)
        self.currentRideViewInStation = isSet(integer,12)

allTypes[15] = StationState()

def isSet(integer,position):
    return integer >> position & 1 > 0