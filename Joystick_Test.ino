/*
 * Created by ArduinoGetStarted.com
 *
 * This example code is in the public domain
 *
 * Tutorial page: https://arduinogetstarted.com/tutorials/arduino-joystick
 */
#include <ezButton.h>
#define VRX_PIN  A2 // Arduino pin connected to VRX pin
#define VRY_PIN  A1 // Arduino pin connected to VRY pin
#define SW_PIN 7

int xValue = 0; // To store value of the X axis
int yValue = 0; // To store value of the Y axis

ezButton button (SW_PIN);
void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600) ;
  button.setDebounceTime(50);
}

void loop() {
  button.loop();
  // read analog X and Y analog values
  xValue = analogRead(VRX_PIN);
  yValue = analogRead(VRY_PIN);
  // print data to Serial Monitor on Arduino IDE
  if (button.isPressed()){
    digitalWrite(LED_BUILTIN, HIGH);
  }
  if(button.isReleased()){
    digitalWrite(LED_BUILTIN, LOW);
  }
  Serial.print("x = ");
  Serial.print(xValue);
  Serial.print(", y = ");
  Serial.println(yValue);
  delay(200);
}
