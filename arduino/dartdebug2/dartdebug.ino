// digital pin 2 has a pushbutton attached to it. Give it a name:
int outpin[] = {37, 39, 41, 43, 45, 47, 49};
int outc = 7;
int inpin[] = {30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52};
int inc = 12;
char sdt[] = {'S', 'D', 'T'};

int c_sdt = 0;
int c_nr = 1;

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
           Serial.print(sdt[c_sdt]);
           Serial.print(c_nr);
           Serial.print(",");
           Serial.print(inpin[in]);
           Serial.print(",");
           Serial.println(outpin[out]);
           delay(250);
           c_sdt ++;
           if (c_sdt > 0) {
             c_sdt = 0;
             c_nr += 1;
           }
        }
     }
     digitalWrite(outpin[out], HIGH);
  }  
}



