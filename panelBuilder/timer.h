//Importing 
#include "Arduino.h"
class Timer{
  private:
    //Creating private object variables
    long currentTime = 0;
    long startTime = 0;
    long endTime = 0;
  public:
    void setTime(long runTime){
      //Setting the start time to the current time
      startTime = millis();
      //Setting the endtime to the endTime paramter
      endTime = runTime;
      //Setting the current time to 0
      currentTime = 0;
    }
    bool checkTime(){
      //Checking if the current time is less than the end time
      if (currentTime < endTime){
        //If True then the timer has not been running for long enough
        //Getting the current time
        long intervalTime = round(millis());
        //Subtracting the startTime from the intervalTime to see how much time has passed and then setting that to the currentTime
        currentTime = intervalTime - startTime;
        //Returing false
        return false;
      }
      else {
        //If false then the timer has elapsed
        //Returning True
        return true;
      }
    }
};