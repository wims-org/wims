#include <SPI.h>
#include <MFRC522.h>
 
#define SS_PIN 10
#define RST_PIN 9
MFRC522 myRFID(SS_PIN, RST_PIN);

void setup() 
{
  Serial.begin(115200);
  SPI.begin();
  myRFID.PCD_Init();
}

String buildUID(byte *buffer, byte bufferSize) {
    String uid = "";
    for (byte i = 0; i < myRFID.uid.size; i++) {
      if (myRFID.uid.uidByte[i] < 0x10) uid += "0";
      uid += String(myRFID.uid.uidByte[i], HEX);
      if (i < myRFID.uid.size - 1) uid += "-";
    }
    return uid;
}

void loop() 
{
  if ( ! myRFID.PICC_IsNewCardPresent()) 
  {
    return;
  }

  if ( ! myRFID.PICC_ReadCardSerial()) 
  {
    return;
  }

  Serial.println(buildUID(myRFID.uid.uidByte, myRFID.uid.size));

  myRFID.PICC_HaltA();
} 
