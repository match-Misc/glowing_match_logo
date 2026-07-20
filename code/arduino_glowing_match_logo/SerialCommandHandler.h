#ifndef SERIALCOMMANDHANDLER_H
#define SERIALCOMMANDHANDLER_H

#include <Arduino.h>
#include <EEPROM.h>
#include "DisplayObjects.h"
#include "Effects.h"
#include "StateManager.h"

class SerialCommandHandler {
private:
  PcbWord &pcbWord;
  Adafruit_NeoPixel &strip;
  
  // Array to store effect pointers
  Effect **effects;
  uint8_t effectCount;
  
  // Brightness settings
  uint8_t maxBrightness;
  
  // Reference to shared state
  StateManager &stateManager;

public:
  SerialCommandHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, uint8_t maxBright, StateManager &sm);
  
  void handle();
  void printHelp();
  void printEffects();
  
private:
  void processCommand(const String &cmd);
  void setLetterEffect(char letter, uint8_t mode);
  void setWordMode(uint8_t mode);
  void setBrightness(uint8_t percent);
  bool isValidLetter(char letter);
  char normalizeLetterCase(char letter);
};

#endif
