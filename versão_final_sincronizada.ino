#include <ESP32Servo.h>
#include "BluetoothSerial.h"

BluetoothSerial SerialBT;
Servo servo;

// Pinos
const int pinSensor = 23;
const int pinServo = 22;
const int pinBuzzer = 21;
const int pinLED = 19;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("ESP32_BT"); // Nome visível no Bluetooth

  pinMode(pinSensor, INPUT);
  pinMode(pinBuzzer, OUTPUT);
  pinMode(pinLED, OUTPUT);

  // Configura o servo no pino 22
  servo.attach(pinServo);
  servo.write(0);

  Serial.println("Sistema iniciado e Bluetooth pronto!");
}

void loop() {
  // --- Sensor de presença ---
  int presenca = digitalRead(pinSensor);
  if (presenca == HIGH) {
    servo.write(45);
  } else {
    servo.write(0);
  }

  // --- Bluetooth ---
  if (SerialBT.available()) {
    char comando = SerialBT.read();

    // Se receber 'A', executa o alerta uma única vez
    if (comando == 'A' || comando == 'a') {
      Serial.println("Alerta de ataque recebido!");
      SerialBT.println("Alerta executado!");

      // Liga buzzer e LED
      digitalWrite(pinBuzzer, HIGH);
      digitalWrite(pinLED, HIGH);

      delay(1000); // mudar o tempo de alerta

      // Desliga buzzer e LED
      digitalWrite(pinBuzzer, LOW);
      digitalWrite(pinLED, LOW);
    }
  }

  delay(20); // Pequeno atraso para estabilidade
}
