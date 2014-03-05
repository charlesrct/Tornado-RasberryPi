#include <Wire.h>
#include <LiquidCrystal.h>

#define SLAVE_ADDRESS 0x04
int number = 0;

//Led que indica la recepcion de un dato.
int led = 13;

//Pines para ultrasonido.
int trig = 7;
int echo = 8;

//var para guardar la ditancia
int distance;

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(12, 11, 5, 4, 1, 0);

void setup() {
  //Conf. pines del sensor ultrasonido
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(led, OUTPUT);

  // set up the LCD's number of columns and rows:
  lcd.begin(16, 2);

  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);

  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

}

void loop() {
  delay(100);
  sonar();
  lcd.setCursor(0, 0);
  lcd.print("num= ");
  lcd.print(number);
}

// callback for received data
void receiveData(int byteCount) {

  while (Wire.available()) {
    number = Wire.read();

    if (number == 1) {
      digitalWrite(led, HIGH); // set the LED on
    }
    else {
      digitalWrite(led, LOW); // set the LED off
    }
  }
}

// callback for sending data
void sendData() {
  Wire.write(distance);
}

void sonar() {
  //Disparo de 15uSeg
  digitalWrite(trig, HIGH);
  delayMicroseconds(15);
  digitalWrite(trig, LOW);

  //medimos el pulso de entrada
  distance = pulseIn(echo, HIGH);
  lcd.setCursor(0, 1);
  distance = distance * 0.01657; //Convertimos el tiempo en distancia cm
  if (distance < 500) {
    lcd.print(distance);
    lcd.print("cm   ");
  }
  else {
    lcd.print("         ");
  }
}
