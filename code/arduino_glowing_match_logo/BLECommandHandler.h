#ifndef BLE_COMMANDHANDLER_H
#define BLE_COMMANDHANDLER_H

#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include "Config.h"
#include "DisplayObjects.h"
#include "Effects.h"
#include "StateManager.h"

// BLE UUIDs for LED Control Service
#define BLE_SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define BLE_COMMAND_CHAR_UUID   "87654321-4321-8765-4321-0fedcba98765"
#define BLE_RESPONSE_CHAR_UUID  "abcdef00-abcd-ef00-abcd-ef0012345678"

class BLECommandHandler;  // Forward declaration

// Callbacks for BLE server events
class MyServerCallbacks : public BLEServerCallbacks {
  BLECommandHandler *handler;
public:
  MyServerCallbacks(BLECommandHandler *h) : handler(h) {}
  void onConnect(BLEServer *pServer);
  void onDisconnect(BLEServer *pServer);
};

// Callbacks for BLE characteristic write events
class MyCharacteristicCallbacks : public BLECharacteristicCallbacks {
  BLECommandHandler *handler;
public:
  MyCharacteristicCallbacks(BLECommandHandler *h) : handler(h) {}
  void onWrite(BLECharacteristic *pCharacteristic);
};

class BLECommandHandler {
private:
  PcbWord &pcbWord;
  Adafruit_NeoPixel &strip;
  Effect **effects;
  uint8_t effectCount;
  uint8_t maxBrightness;
  StateManager &stateManager;
  
  BLEServer *pServer;
  BLECharacteristic *pCommandChar;
  BLECharacteristic *pResponseChar;
  bool deviceConnected;
  
  // Connection blink state
  bool blinkInProgress;
  uint8_t blinkCount;
  unsigned long blinkStartTime;
  unsigned long savedBrightness;
  
  void processCommand(const String &cmd);
  void setLetterEffect(char letter, uint8_t mode);
  void setWordMode(uint8_t mode);
  void setBrightness(uint8_t percent);
  void sendResponse(const String &response);
  bool isValidLetter(char letter);
  char normalizeLetterCase(char letter);
  void printHelp();
  void printEffects();
  void performConnectionBlink();

public:
  BLECommandHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, uint8_t maxBright, StateManager &sm);
  
  void begin();
  void handle();
  void setConnected(bool connected);
  bool isConnected() const;
  bool isBlinking() const;
  
  friend class MyServerCallbacks;
  friend class MyCharacteristicCallbacks;
};

#endif
