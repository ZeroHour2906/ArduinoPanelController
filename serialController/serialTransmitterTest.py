from serialMonitorHandler import serialMessenger
import time,json

allValues = {"dispatch":"false",
             "closeHarness":"false",
             "openHarness":"true",
             "closeGates":"false",
             "openGates":"false",
             "lowerPlatform":"false",
             "raisePlatform":"false",
             "unlockFlyer":"false",
             "lockFlyer":"false"}

serialMonitor = serialMessenger(timeout=None)

time.sleep(5)

serialMonitor.sendMessage(json.dumps(allValues))

print("Sent inital values")

try:
    while True:
        message = serialMonitor.readMessage(10)
        if message != "":
            message.decode(encoding="utf8").rstrip()
            print(json.loads(message))
except KeyboardInterrupt:
    serialMonitor.shutDown()
    quit()