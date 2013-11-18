int outpin[] = {37, 39, 41, 43, 45, 47, 49};
int outc = 7;
int inpin[] = {30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52};
int inc = 12;
int butpin[] = {29,28,31,33,26,51};
int butc = 6;
int butgnd = 53;
int out;
int in;
int i;

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  // set inpins/outpins
  for (i = 0; i < inc; i++) {
      pinMode(inpin[i], INPUT);
      digitalWrite(inpin[i], HIGH); // activate 20k pull-up
  }
  for (i = 0; i < outc; i++) {
      pinMode(outpin[i], OUTPUT);
      digitalWrite(outpin[i], HIGH);
  }
  // set button pins to input
  for (i = 0; i < butc; i++) {
      pinMode(butpin[i], INPUT);
      digitalWrite(butpin[i], HIGH); // activate 20k pull-up
  }
  pinMode(butgnd, OUTPUT);
  digitalWrite(butgnd, 0); // set gnd for buttons
}

// the loop routine runs over and over again forever:
void loop() {
  for (out = 0; out < outc; out++) {
     digitalWrite(outpin[out], LOW);
     for (in = 0; in < inc; in++) {
        if (! digitalRead(inpin[in])) {
           Serial.write((out << 4) + in);
           delay(250);
           while (! digitalRead(inpin[in])) {
              Serial.write(0x70);
              delay(400);
           }
           delay(250);
        }
     }
     digitalWrite(outpin[out], HIGH);
  }  
  for (i = 0; i < butc; i++) {
    if (! digitalRead(butpin[i])) {
      Serial.write(0x80 + i);
      delay(400);
      while (! digitalRead(butpin[i])) {
        delay(300);
      }
      delay(250);
    }
  }
}
