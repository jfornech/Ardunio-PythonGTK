#include "Wire.h"    // imports the wire library for talking over I2C 
#include "Adafruit_BMP085.h"  // import the Pressure Sensor Library
Adafruit_BMP085 mySensor;  // create sensor object called mySensor
 
float tempC;  // Variable for holding temp in C
float tempF;  // Variable for holding temp in F
float pressure; //Variable for holding pressure reading
 
void setup(){
  Serial.begin(9600); //turn on serial monitor
  mySensor.begin();   //initialize mySensor

  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);


  int cmd = readData();
    for (int i = 0; i < cmd; i++) {
      pinMode(readData(), OUTPUT);
      }
}
 
void loop() {
  tempC = mySensor.readTemperature(); //  Read Temperature
  tempF = tempC*1.8 + 32.; // Convert degrees C to F
  pressure=mySensor.readPressure(); //Read Pressure
  
  Serial.println(tempC);
  //Serial.print("The Pressure is: ");
  Serial.println(pressure / 100);
  //delay(10); //Pause between readings.
  
  switch (readData()) {
        case 0 :
            //set digital low
            digitalWrite(readData(), LOW); break;
        case 1 :
            //set digital high
            digitalWrite(readData(), HIGH); break;
        case 2 :
            //get digital value
            Serial.println(digitalRead(readData())); break;
        case 3 :
            // set analog value
            analogWrite(readData(), readData()); break;
        case 4 :
            //read analog value
            Serial.println(analogRead(readData())); break;
        case 99:
            //just dummy to cancel the current read, needed to prevent lock 
            //when the PC side dropped the "w" that we sent
            break;
}


}
char readData() {
    //Serial.println("w");
    while (Serial.available() > 0){
            return Serial.parseInt();
    }
}

