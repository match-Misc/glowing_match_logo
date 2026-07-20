#ifndef STATEMANAGER_H
#define STATEMANAGER_H

#include <Arduino.h>
#include <EEPROM.h>
#include "PersistentState.h"

#define MAX_LETTERS 5

class StateManager {
private:
  bool ledsEnabled;
  uint8_t brightnesPercent;
  uint8_t currentWordEffectIndex;
  bool wordModeEnabled;
  uint8_t letterEffectIndices[MAX_LETTERS];  // Track effect index for each letter

public:
  StateManager();
  
  // LED state management
  bool isLedsEnabled() const;
  void setLedsEnabled(bool enabled);
  
  // Brightness management
  uint8_t getBrightnessPercent() const;
  void setBrightnessPercent(uint8_t percent);
  
  // Word effect management
  uint8_t getCurrentWordEffectIndex() const;
  void setCurrentWordEffectIndex(uint8_t index);
  
  bool isWordModeEnabled() const;
  void setWordModeEnabled(bool enabled);
  
  // Letter effect management
  uint8_t getLetterEffectIndex(uint8_t letterIndex) const;
  void setLetterEffectIndex(uint8_t letterIndex, uint8_t effectIndex);
  
  // EEPROM operations
  void loadFromEEPROM(uint8_t defaultBrightnessPercent);
  void saveToEEPROM();
};

#endif
