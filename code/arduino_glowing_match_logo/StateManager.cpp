#include "StateManager.h"

StateManager::StateManager()
  : ledsEnabled(true), brightnesPercent(50), currentWordEffectIndex(0), wordModeEnabled(false) {
  // Initialize all letter effect indices to 0 (Off)
  for (uint8_t i = 0; i < MAX_LETTERS; i++) {
    letterEffectIndices[i] = 0;
  }
}

bool StateManager::isLedsEnabled() const {
  return ledsEnabled;
}

void StateManager::setLedsEnabled(bool enabled) {
  ledsEnabled = enabled;
  saveToEEPROM();
}

uint8_t StateManager::getBrightnessPercent() const {
  return brightnesPercent;
}

void StateManager::setBrightnessPercent(uint8_t percent) {
  if (percent <= 100) {
    brightnesPercent = percent;
    saveToEEPROM();
  }
}

uint8_t StateManager::getCurrentWordEffectIndex() const {
  return currentWordEffectIndex;
}

void StateManager::setCurrentWordEffectIndex(uint8_t index) {
  currentWordEffectIndex = index;
  saveToEEPROM();
}

bool StateManager::isWordModeEnabled() const {
  return wordModeEnabled;
}

void StateManager::setWordModeEnabled(bool enabled) {
  wordModeEnabled = enabled;
  saveToEEPROM();
}

uint8_t StateManager::getLetterEffectIndex(uint8_t letterIndex) const {
  if (letterIndex < MAX_LETTERS) {
    return letterEffectIndices[letterIndex];
  }
  return 0;
}

void StateManager::setLetterEffectIndex(uint8_t letterIndex, uint8_t effectIndex) {
  if (letterIndex < MAX_LETTERS) {
    letterEffectIndices[letterIndex] = effectIndex;
    saveToEEPROM();
  }
}

void StateManager::loadFromEEPROM(uint8_t defaultBrightnessPercent) {
  if (!eepromHasValidData()) {
    eepromMarkInitialized();
    ledsEnabled = true;
    brightnesPercent = defaultBrightnessPercent;
    currentWordEffectIndex = 0;
    wordModeEnabled = false;
    for (uint8_t i = 0; i < MAX_LETTERS; i++) {
      letterEffectIndices[i] = 0;
    }
    saveToEEPROM();
    return;
  }

  uint8_t enabledValue = EEPROM.read(EEPROM_ADDR_LED_ENABLED);
  if (enabledValue == 0 || enabledValue == 1) {
    ledsEnabled = (enabledValue == 1);
  } else {
    ledsEnabled = true;
  }

  uint8_t brightnessValue = EEPROM.read(EEPROM_ADDR_BRIGHTNESS_PERCENT);
  if (brightnessValue <= 100) {
    brightnesPercent = brightnessValue;
  } else {
    brightnesPercent = defaultBrightnessPercent;
  }

  wordModeEnabled = (EEPROM.read(EEPROM_ADDR_WORD_MODE_ENABLED) == 1);
  
  uint8_t savedWordEffectIndex = EEPROM.read(EEPROM_ADDR_WORD_EFFECT_INDEX);
  currentWordEffectIndex = savedWordEffectIndex;
  
  // Load letter effect indices
  for (uint8_t i = 0; i < MAX_LETTERS; i++) {
    uint8_t savedEffectIndex = EEPROM.read(EEPROM_ADDR_LETTER_EFFECTS + i);
    if (savedEffectIndex <= 13) {  // Valid effect indices are 0-13
      letterEffectIndices[i] = savedEffectIndex;
    } else {
      letterEffectIndices[i] = 0;  // Default to off if invalid
    }
  }
}

void StateManager::saveToEEPROM() {
  if (!eepromHasValidData()) {
    eepromMarkInitialized();
  }

  EEPROM.write(EEPROM_ADDR_LED_ENABLED, ledsEnabled ? 1 : 0);
  EEPROM.write(EEPROM_ADDR_BRIGHTNESS_PERCENT, brightnesPercent);
  EEPROM.write(EEPROM_ADDR_WORD_MODE_ENABLED, wordModeEnabled ? 1 : 0);
  EEPROM.write(EEPROM_ADDR_WORD_EFFECT_INDEX, currentWordEffectIndex);
  
  // Save letter effect indices
  for (uint8_t i = 0; i < MAX_LETTERS; i++) {
    EEPROM.write(EEPROM_ADDR_LETTER_EFFECTS + i, letterEffectIndices[i]);
  }

#if defined(ESP32)
  EEPROM.commit();
#endif
}
