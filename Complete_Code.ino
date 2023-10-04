/*     'Stretchy' Rig Control
       by Dhruv Trehan 2023
*/

#include "HX711.h"
#include <ezButton.h>

HX711 scale;

// defines pins numbers
//Step and Dir are pins on PCB
//For Stepper
#define stepPin 12 
#define dirPin 11
//For Joystick
//#define VRX_pin A2
//#define VRY_pin A1
//#define SW_pin 7
//Potentiometer
#define Pot A3
//Load Cell
uint8_t dataPin = 3;
uint8_t clockPin = 2;

//Variables
//int xValue = 0;
//int yValue = 0;
uint32_t start, stop;
volatile float f;
int Total_time = 50; 
String readString; //main captured String 
//int Btn_State = 0;

//Initiate Joystick Button
//ezButton button (SW_pin);

void setup() {
  char *command; //Terminating Character
  // Sets the two pins as Outputs
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  //pinMode(VRX_pin, INPUT);
  Serial.begin(115200);
  Serial.setTimeout(1);
  scale.begin(dataPin, clockPin); //Initiate Load Cell
  //button.setDebounceTime(50);

  scale.set_scale(420.0983);       // TODO you need to calibrate this yourself.
  scale.tare();

}
void forward (int D){
  digitalWrite(dirPin, HIGH); //Changes the rotations direction
  // Makes D pulses, 100 pulses is one cycle
  for (int x = 0; x < D; x++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }
}

void backward (int D){
  digitalWrite(dirPin, LOW); //Changes the rotations direction
  // Makes D pulses, 100 pulses is one cycle
  for (int x = 0; x < D; x++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }
}

void manual() { //Joystick Control

//  xValue = analogRead(VRX_pin);
//  //Serial.println(xValue);
//  // Crossover Between two directions
//  if (xValue > 400 && xValue < 520)  {
//    digitalWrite(stepPin, LOW);
//  }
//
//  // Threshold for "High/Forward" Direction
//  else if (xValue < 400)  {
//    forward(1);
//  }
//
//  // Threshold for "Low/Backward" Direction
//  else if (xValue > 530)  {
//    backward(1);
//  }
}

void test_run() {
  digitalWrite(dirPin, HIGH);

  // Spin motor slowly
  for(int x = 0; x < 200; x++){
    
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(2000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(2000);
  }
  delay(1000); // Wait a second
  
  // Set motor direction counterclockwise
  digitalWrite(dirPin, LOW);

  // Spin motor quickly
  for(int x = 0; x < 200; x++)
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }
  delay(1000); // Wait a second
}

void sendData(){
    int data = analogRead(Pot); //Liinear Displacement
    f = scale.get_units(5); //Force 
    // Prints (Linear Pot Output, Load Cell Output)
    Serial.print(data);
    Serial.print(", ");
    Serial.println(f);
    delay(50);
    Serial.flush();
}

void seperate (String mystring){ //Split String into commands and execute them at the same time
  while (mystring.indexOf(", ") != -1){
      int index = mystring.indexOf(", ");
      automatic(mystring.substring(0, index));
      mystring.remove(0, index + 2);
  }
  automatic(mystring);
}

void automatic (String inp) {
  //Input to switch case should be a string with a capital letter followed by a number e.g. F10 (10 should be number of pulses for more fine control)
 
  String Instruction = inp.substring(1) ;
  if (inp[0] == 'F') { //Forward 
    forward(Instruction.toInt());
    sendData();

  }
  else if (inp[0] == 'B') {//Backwards
    backward(Instruction.toInt());
    sendData();
          //do stuff
  }
  else if (inp[0] == 'D') {//Delay
    // Don't do anything for n milliseconds
    sendData();
    //do stuff
    delay(Instruction.toInt());
  }
  else if (inp[0] =='T'){//Total time to continue sending data for after instructions recieved
    //Set Total_time
    Total_time =  Instruction.toInt()*10;
  }
  else {
    Serial.println("Error");
    delay(50);
    Serial.flush();
  }
}

void loop() {
  if (Serial.available())  {
    char c = Serial.read();  //gets one byte from serial buffer
      if (c == '*') {
        seperate(readString);
        for (int i = 0; i<Total_time; i++){ //Total_time refers to how many data points are sent for after commands are executed
          sendData();
          //do stuff
        }
      }  
      else {     
        readString += c; //makes the string readString
      }
  }
}




//  button.loop(); //Button
//  if (button.isPressed()){
//    Btn_State = !Btn_State; //Switch button state when pressed 
//    Btn_State = 0;
//  }
//  if (Btn_State == 1){ //Manual control
//    digitalWrite(LED_BUILTIN, LOW); 
//    manual();
//    //sendData();
//    
//  }
//  if (Btn_State == 0){//Controlled by the Python application
//    digitalWrite(LED_BUILTIN, HIGH);
//    if (Serial.available())  {
//    char c = Serial.read();  //gets one byte from serial buffer
//      if (c == '*') {
//        seperate(readString);
//        for (int i = 0; i<Total_time; i++){ //Total_time refers to how many data points are sent for after commands are executed
//          sendData();
//          //do stuff
//        }
//       }  
//      else {     
//        readString += c; //makes the string readString
//    }
//   
//  }
//  }
