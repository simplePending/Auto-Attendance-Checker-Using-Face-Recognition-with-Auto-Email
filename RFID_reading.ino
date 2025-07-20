#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN 9    // Reset Pin
#define SS_PIN 10    // Slave Select Pin for RFID Module

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create MFRC522 instance

// Predefined student names mapped to RFID UIDs
const String studentIDs[] = {
  "FC1E24", "D6004", "A491422", "4B2F04", "966D24", "B4B114", "E36224"
};

// const String studentNames[] = {
//   "Name 1", "Name 2", "Name 3", "Name 4", "Name 5", "Name 6", "Name 7"
// };

void setup() {
  Serial.begin(9600);  
  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String studentID = "";

    // Read UID and store it as a string
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      studentID += String(mfrc522.uid.uidByte[i], HEX);
    }
    studentID.toUpperCase();  // Convert UID to uppercase

    // // Match UID with student name
    // String studentName = "Unknown";
    // for (int i = 0; i < sizeof(studentIDs) / sizeof(studentIDs[0]); i++) {
    //   if (studentIDs[i] == studentID) {
    //     studentName = studentNames[i];
    //     break;
    //   }
    // }

    // Print only UID and Student Name
    Serial.println(studentID);
    // Serial.print(" | ");
    // Serial.println(studentName);

    mfrc522.PICC_HaltA();
  }
}
