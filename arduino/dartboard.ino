/*
  DigitalReadSerial
 Reads a digital input on pin 2, prints the result to the serial monitor 
 
 This example code is in the public domain.
 */
 
// digital pin 2 has a pushbutton attached to it. Give it a name:
int outpin[] = {6, 7};
int outc = 2;
int inpin[] = {2,3,4};
int inc = 3;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  // set inpins/outpins
  int i;
  for (i = 0; i < inc; i++) {
      pinMode(inpin[i], INPUT);
      digitalWrite(inpin[i], HIGH); // activate 20k pull-up
  }
  for (i = 0; i < outc; i++) {
      pinMode(outpin[i], OUTPUT);
      digitalWrite(outpin[i], HIGH);
  }
}

// the loop routine runs over and over again forever:
void loop() {
  int out;
  int in;
  for (out = 0; out < outc; out++) {
     digitalWrite(outpin[out], LOW);
     for (in = 0; in < inc; in++) {
        if (! digitalRead(inpin[in])) {
           Serial.write(out + (in << 4));
           delay(250);
           if (! digitalRead(inpin[in])) {
             Serial.write(0xFF);
             while (! digitalRead(inpin[in])) {
                delay(200);
             }
             Serial.write(0xFE);
           }
           delay(250);
        }
     }
     digitalWrite(outpin[out], HIGH);
  }  
}



