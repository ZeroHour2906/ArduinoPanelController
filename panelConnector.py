#Importing required modules
import telemetryController.telemetryHandler as telemetryHandler
import telemetryController.requestTypes as requestTypes
import telemetryController.responseTypes as responses
import serialController.serialMonitorHandler as serialMonitorHandler
import json
import time

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

#Creating statemessages
currentCoasterIndex = 0
currentStationIndex = 0
currentCoasterName = ""

def sendRecieve(requestMessage):
    #Sending the message and getting the response
    response = transmitter.sendRecieve(requestMessage.buffer)
    # Checking if transmitter has disconnected
    if transmitter.checkConnection() == False:
        return
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

def handleMessage(sentMessage):
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

#Running the loop to manage the program
try:
    # Creating and performing set up for both serial and telemetry connections
    print("Performing connector setup")

    #Creating telemetry handlers
    print("Connecting to NL2 telemetry server")
    transmitter = telemetryHandler.TelTransmitter("localhost",15151)

    # Attempting to connect to the socket
    if transmitter.checkConnection() == False:
        # Unable to connect to server
        print("Unable to connect to server")
    else:
        # Connected
        print("Connected to server")

    # Creating serial monitor handlers
    print("Connecting to Arduino")
    serial = serialMonitorHandler.serialMessenger(timeout=None)

    # Checking if serial monitor has connected
    if serial.checkConnection() == True:
        # Successfully connected. Inform user and wait for reset
        print("Successfully connected to Arduino\nAwaiting Serial reset")
        time.sleep(5)
        print("Serial connection reset")
    else:
        # Unable to connect
        print("Unable to connect to Serial Monitor")
    
    # Informing user setup is complete and how to exit
    print("Connector setup complete - press CTRL+C to exit")

    while True:
        # Checking if the telemetry connection and arduino connections are still alive
        if transmitter.checkConnection() == True and serial.checkConnection() == True:
            try:
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
                    handleMessage(json.loads(recievedMessage)["command"])

            except AttributeError:
                # Ignoring in the event of an AttributeError
                pass
        
        # Checking if the transmitter is not connected
        elif transmitter.checkConnection() == False:
            # Attempting to connect to the address
            transmitter.connect()

        # Checking if the serial monitor is not connected
        elif serial.checkConnection() == False:
            # Attempting to connect to the serial monitor
            serial.setUp(0,9600)

except KeyboardInterrupt:
    # Program has been requested to close
    print("Closing connections")
    # Closing the connections
    serial.shutDown()
    transmitter.disconnect()
    # Displaying connections closed result
    print("Connections closed")