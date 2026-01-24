import telemetryHandler,requestTypes

transmitter = telemetryHandler.TelTransmitter("localhost",15151)

def sendRecieve(requestMessage):

    transmitter.send(requestMessage.buffer)

    response = transmitter.recieve(100)

    responseSpit = requestTypes.Message.getData(response)
    
    return responseSpit

getActiveCoaster = requestTypes.GetCurrentCoasterAndNearestStationMessage()
activeCoaster = sendRecieve(getActiveCoaster)
getStationState = requestTypes.GetStationStateMessage()
getStationState.getStateFor(activeCoaster.value0,activeCoaster.value1)

print(activeCoaster.__dict__)

transmitter.disconnect()