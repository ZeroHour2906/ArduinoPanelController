#Importing required modules
import telemetryController.telemetryHandler as telemetryHandler,telemetryController.requestTypes as requestTypes,serialController.serialMonitorHandler as serialMonitorHandler,json,time

#Creating dictionary for default values
defaultValues = {
    "dispatch": "false",
    "closeHarness": "false",
    "openHarness": "false",
    "estop": "false",
    "closeGates": "false",
    "openGates": "false",
    "lowerPlatform": "false",
    "raisePlatform": "false",
    "unlockFlyer": "false",
    "lockFlyer":"false"
}

#Creating dictionary for previous values
previousValues = defaultValues.copy()

#Creating dictionary for new values
newValues = defaultValues.copy()

#Creating message objects
dispatchMessage = requestTypes.DispatchMessage()
gateMessage = requestTypes.SetGatesMessage()
barMessage = requestTypes.SetHarnessMessage()
platformMessage = requestTypes.SetPlatformMessage()
flyerMessage = requestTypes.SetFlyerMessage()
activeCoasterMessage = requestTypes.GetCurrentCoasterAndNearestStationMessage()
coasterNameMessage = requestTypes.GetCoasterNameMessage()
stationStateMessage = requestTypes.GetStationStateMessage()
telemetryMessage = requestTypes.GetTelemetryMessage()
eStopMessage = requestTypes.SetEmergencyStopMessage()

#Creating serial monitor and telemetry handlers
transmitter = telemetryHandler.TelTransmitter("localhost",15151)
serial = serialMonitorHandler.serialMessenger(timeout=None)

#Creating statemessages
currentCoasterIndex = 0
currentStationIndex = 0
currentCoasterName = ""

def sendRecieve(requestMessage):
    #Sending the message and getting the response
    response = transmitter.sendRecieve(requestMessage.buffer)
    #Decrypting the message and returning
    return requestTypes.Message.getData(response)

def getClosetCoaster():
    #Getting the active coaster and station index
    currentActiveCoaster = sendRecieve(activeCoasterMessage)
    #Setting index to get the coaster name
    coasterNameMessage.setCoasterIndex(currentActiveCoaster.value0)
    #Getting the coaster name
    currentActiveName = sendRecieve(coasterNameMessage)
    #Returning the coaster, station index and the coaster name
    return currentActiveCoaster.value0,currentActiveCoaster.value1,currentActiveName.value

def getStationState():
    #Setting the coaster and station index for the station state message
    stationStateMessage.getStateFor(currentCoasterIndex,currentStationIndex)
    #Getting the station state and returning it
    return sendRecieve(stationStateMessage)

def updateValues(stationStatus,newValues):
    #Checking if the estop is pressed
    #Updating values in the new value dictionary
    newValues["estop"]  = str(stationStatus.get("e_stop")).lower()
    newValues["dispatch"]  = str(stationStatus.get("canDispatch")).lower()
    newValues["closeGates"] = str(stationStatus.get("canCloseGates")).lower()
    newValues["openGates"] = str(stationStatus.get("canOpenGates")).lower()
    newValues["closeHarness"] = str(stationStatus.get("canCloseHarness")).lower()
    newValues["openHarness"] = str(stationStatus.get("canOpenHarness")).lower()
    newValues["raisePlatform"] = str(stationStatus.get("canRaisePlatform")).lower()
    newValues["lowerPlatform"] = str(stationStatus.get("canLowerPlatform")).lower()
    newValues["unlockFlyer"] = str(stationStatus.get("canUnlockFlyer")).lower()
    newValues["lockFlyers"] = str(stationStatus.get("canLockFlyer")).lower()
    #Checking if the dictionarys are different and returning result
    return newValues != previousValues,newValues

def handleMessage(sentMessage,stationState):
    #Checking what message was sent
    if sentMessage == "dispatch":
        #If dispatch was sent then dispatch the train
        dispatchMessage.getStateFor(currentCoasterIndex,currentStationIndex)
        sendRecieve(dispatchMessage)
    elif sentMessage == "openHarness":
        #If open harness was sent then open the harness
        barMessage.setModeFor(currentCoasterIndex,currentStationIndex,1)
        sendRecieve(barMessage)
    elif sentMessage == "closeHarness":
        #If close harness was sent then close the harness
        barMessage.setModeFor(currentCoasterIndex,currentStationIndex,0)
        sendRecieve(barMessage)
    elif sentMessage == "openGates":
        #If open gates was sent then open the gates
        gateMessage.setModeFor(currentCoasterIndex,currentStationIndex,1)
        sendRecieve(gateMessage)
    elif sentMessage == "closeGates":
        #If close gates was sent then close the gates
        gateMessage.setModeFor(currentCoasterIndex,currentStationIndex,0)
        sendRecieve(gateMessage)
    elif sentMessage == "raisePlatform":
        #If raise platform was sent then raise the platform
        platformMessage.setModeFor(currentCoasterIndex,currentStationIndex,1)
        sendRecieve(platformMessage)
    elif sentMessage == "lowerPlatform":
        #If lower platform was sent then raise the platform
        platformMessage.setModeFor(currentCoasterIndex,currentStationIndex,0)
        sendRecieve(platformMessage)
    elif sentMessage == "lockFlyer":
        #If lock flyer was sent lock the flyer car
        flyerMessage.setModeFor(currentCoasterIndex,currentStationIndex,1)
        sendRecieve(flyerMessage)
    elif sentMessage == "unlockFlyer":
        #If unlock flyer was sent unlock the flyer car
        flyerMessage.setModeFor(currentCoasterIndex,currentStationIndex,0)
        sendRecieve(flyerMessage)
    elif sentMessage == "estop":
        #If estop was sent then estop the coaster
        eStopMessage.setEmergencyStop(currentCoasterIndex,1)
        sendRecieve(eStopMessage)

# Delay to allow the Arduino to reset
time.sleep(5)

#Running the loop to manage the program
try:
    while True:
        #Checking which coaster is active
        currentCoasterIndex,currentStationIndex,currentCoasterName = getClosetCoaster()
        #Getting the station state
        stationState = getStationState()
        #Updating the new values dictionary
        differentValues,newValues = updateValues(stationState.__dict__,newValues)
        #Checking if the values were different
        if differentValues == True:
            #If true then send the dictionary to the arduino serial monitor
            serial.sendMessage(json.dumps(newValues))
            #Replacing the previous values dictionary with the newValues one
            previousValues = newValues.copy()
        #Checking if a message has been sent from arduino serial monitor
        recievedMessage = serial.readMessageUntil(b"}",10)
        if recievedMessage != "":
            #Decoding the message
            recievedMessage.decode(encoding="utf8").rstrip()
            handleMessage(json.loads(recievedMessage)["command"],stationState)
except KeyboardInterrupt:
    #Close program in the event of keyboard interrupt
    quit()