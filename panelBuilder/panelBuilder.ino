// Importing required libaries
#include <ArduinoJson.h>
#include "timer.h"

//Defining complier constants
#define dispatchEnableLight 2
#define dispatchButton 3
#define canOpenHarnessLight 4
#define canCloseHarnessLight 5
#define harnessToggleButton 6
#define estopIndicator 7
#define canOpenGateLight 8
#define canCloseGateLight 9 
#define gateToggleButton 11
#define platformToggleButton 12
#define flyerToggleButton 13

// Creating global variables
struct stateContainer{
    String canDispatch = "false";
    String canCloseHarness = "false";
    String canOpenHarness = "false";
    String eStopped = "false";
    String canCloseGates = "false";
    String canOpenGates = "false";
    String canLowerPlatform = "false";
    String canRaisePlatform = "false";
    String canLockFlyer = "false";
    String canUnlockFlyer = "false";
};

struct lightStates{
    bool dispatchLights = false;
    bool closeHarness = false;
    bool openHarness = false;
    bool estopLight = false;
    bool closeGates = false;
    bool openGates = false;
    bool lowerPlatform = false;
    bool raisePlatform = false;
    bool lockFlyer = false;
    bool unlockFlyer = false;
};

stateContainer currentStates;
lightStates currentIndicatorState;
Timer flashingTimer;

int indicatorPins[] = {dispatchEnableLight,canCloseHarnessLight,canOpenHarnessLight,estopIndicator,canCloseGateLight,canOpenGateLight};

void setup(){
    // Setting pin modes
    pinMode(estopIndicator, OUTPUT);
    pinMode(dispatchEnableLight,OUTPUT);
    pinMode(dispatchButton,INPUT);
    pinMode(canOpenHarnessLight,OUTPUT);
    pinMode(canCloseHarnessLight, OUTPUT);
    pinMode(harnessToggleButton,INPUT);
    pinMode(canOpenGateLight, OUTPUT);
    pinMode(canCloseGateLight, OUTPUT);
    pinMode(gateToggleButton, INPUT);
    // Starting serial monitor
    Serial.begin(9600);
}

void loop(){
    // Checking if message has been sent
    if (Serial.available() > 10){
        // If true then update the current state
        updateState();
    }
    // Checking if the timer has lapsed
    if (flashingTimer.checkTime() == true){
        // If true invert the light states
        invertLightState();
        // Restarting the timer
        flashingTimer.setTime(1000);
    }
    // Checking if button was pressed
    sendCommand();
}

void updateState(){
    // Creating Json document to contain the decoded json
    JsonDocument decodedJson;
    // Getting message in th serial monitor
    String recievedStates = Serial.readStringUntil("}");
    // Decoding the json values
    DeserializationError error = deserializeJson(decodedJson,recievedStates);
    // Extracting to char types
    const char* canDispatch = decodedJson["dispatch"];
    const char* closeHarness = decodedJson["closeHarness"];
    const char* openHarness = decodedJson["openHarness"];
    const char* estop = decodedJson["estop"];
    const char* closeGates = decodedJson["closeGates"];
    const char* openGates = decodedJson["openGates"];
    const char* lowerPlatform = decodedJson["lowerPlatform"];
    const char* raisePlatform = decodedJson["raisePlatform"];
    const char* unlockFlyer = decodedJson["unlockFlyer"];
    const char* lockFlyer = decodedJson["lockFlyer"];
    // Updating the currentState structure to represent the sent json data
    currentStates.canDispatch = canDispatch;
    currentStates.canCloseHarness = closeHarness;
    currentStates.canOpenHarness = openHarness;
    currentStates.eStopped = estop;
    currentStates.canCloseGates = closeGates;
    currentStates.canOpenGates = openGates;
    currentStates.canLowerPlatform = lowerPlatform;
    currentStates.canRaisePlatform = raisePlatform;
    currentStates.canUnlockFlyer = unlockFlyer;
    currentStates.canLockFlyer = lockFlyer;
}

void invertLightState(){
    // Creating pointer from the first element in the structure
    String *enabledCurrentlyPointer = &currentStates.canDispatch;
    bool *illumiatedCurrentlyPointer = &currentIndicatorState.dispatchLights;
    // Looping until all the indicators have been iterated over
    for (int counter : indicatorPins) {
        // Derefering the pointer to get the value
        String currentEnabled = *enabledCurrentlyPointer;
        // Checking if the light is to be enabled
        if (currentEnabled == "false"){
            // Incrementing the pointers
            enabledCurrentlyPointer += 1;
            illumiatedCurrentlyPointer += 1;
            // Contining past this indicator 
            continue;
        }
        // Dereferencing the pointer
        bool currentState = *illumiatedCurrentlyPointer;
        // Updating the pointer to be the inverse of iself
        *illumiatedCurrentlyPointer = !currentState;
        // Printing out the currentState
        // Incrementing the pointers
        enabledCurrentlyPointer += 1;
        illumiatedCurrentlyPointer += 1;
        // Inverting the state of the LED
        digitalWrite(counter, currentState);
    }
}

void sendCommand(){
    // Creating json document
    JsonDocument outBoundJson;
    // Getting the command
    String commandToSend = checkCommand();
    // Checking if command is empty
    if (commandToSend == ""){
        // Exiting the function as no command possible
        return;
    }
    // Turning into json data
    outBoundJson["command"] = commandToSend;
    // Printing command into serial monitor
    serializeJson(outBoundJson,Serial);
    // Terminating the line
    Serial.println();
}

String checkCommand(){
    String requestedCommand = "";
    // Checking if the dispatch button has been presseed
    if (digitalRead(dispatchButton) == HIGH && currentStates.canDispatch == "true"){
        // If true send dispatch into serial monitor
        requestedCommand = "dispatch";
    }
    // Checking harness toggle button is powered
    else if (digitalRead(harnessToggleButton) == HIGH) {
        // Checking the current state of the harness
        if (currentStates.canCloseHarness == "true") {
            // Setting the command to close harness
            requestedCommand = "closeHarness";
        }
        else if (currentStates.canOpenHarness == "true") {
            // Setting the command to open harness
            requestedCommand = "openHarness";
        }
    }
    // Checking if the gate toggle button has been pressed
    else if (digitalRead(gateToggleButton) == HIGH) {
        // Current state of the gates
        if (currentStates.canCloseGates == "true"){
            // Setting the command to close gates
            requestedCommand = "closeGates";
        }
        else if (currentStates.canOpenGates == "true") {
            // Setting the command to open gates
            requestedCommand = "openGates";
        }
    }
    // Checking if the floor togggle button was pressed
    else if (digitalRead(platformToggleButton) == HIGH) {
        // Checking current state of the platform
        if (currentStates.canRaisePlatform == "true"){
            // Setting the command to raise platform
            requestedCommand = "raisePlatform";
        }
        else if (currentStates.canLowerPlatform == "true") {
            // Setting command to lower platform
            requestedCommand = "lowerPlatform";
        }
    }
    // Checking if the car toggle button was pressed
    else if (digitalRead(flyerToggleButton) == HIGH) {
        // Checking current state of the flyer
        if (currentStates.canUnlockFlyer == "true"){
            // Setting command to unlock flyer
            requestedCommand = "unlockFlyer";
        }
        else if (currentStates.canLockFlyer == "true") {
            // Setting command to lock flyer
            requestedCommand = "lockFlyer";
        }
    }
    return requestedCommand;
}