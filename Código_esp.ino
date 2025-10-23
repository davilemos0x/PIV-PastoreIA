#include "BluetoothSerial.h"

// Cria um objeto para a comunicação Bluetooth Serial
BluetoothSerial SerialBT;

// Se você tiver um LED, conecte a perna longa no pino 22 e a curta no GND
const int pinoLedAlerta = 22; 

void setup() {
  // Inicia a comunicação serial com o computador
  Serial.begin(115200);
  
  // inicia o Bluetooth do ESP32 com um nome visível
  SerialBT.begin("esp32_alerta_ovelhas"); 
  
  Serial.println("O dispositivo ESP32 está pronto para parear!");

  pinMode(pinoLedAlerta, OUTPUT);
  digitalWrite(pinoLedAlerta, LOW); // Garante que o LED comece desligado
}

void loop() {
  // Verifica se há alguma mensagem chegando via Bluetooth
  if (SerialBT.available()) {
    // Lê o caractere recebido
    char comandoRecebido = SerialBT.read();

    // Se o comando for 'A' (de "Ataque" ou "Alerta", enfim), aciona o alerta
    if (comandoRecebido == 'A') {
      Serial.println("Alerta de ataque recebido!");
      digitalWrite(pinoLedAlerta, HIGH); // Liga o LED/Buzzer
      delay(1000); //1 segundo de carga
      digitalWrite(pinoLedAlerta, LOW);  // desliga o LED
    }
  }
  
  // Pequeno delay para não sobrecarregar o processador
  delay(20); 
}
