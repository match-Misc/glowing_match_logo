#ifndef PERSISTENTSTATE_H
#define PERSISTENTSTATE_H

#include <Arduino.h>
#include <EEPROM.h>

#define EEPROM_SIZE_BYTES 64

#define EEPROM_ADDR_MAGIC 0
#define EEPROM_MAGIC_VALUE 0xA5

#define EEPROM_ADDR_BRIGHTNESS_PERCENT 1
#define EEPROM_ADDR_LED_ENABLED 2
#define EEPROM_ADDR_WORD_MODE_ENABLED 3
#define EEPROM_ADDR_WORD_EFFECT_INDEX 4
#define EEPROM_ADDR_LETTER_EFFECTS 5  // 5 bytes for up to 5 letters (indices 5-9)

inline bool eepromHasValidData() {
  return EEPROM.read(EEPROM_ADDR_MAGIC) == EEPROM_MAGIC_VALUE;
}

inline void eepromMarkInitialized() {
  EEPROM.write(EEPROM_ADDR_MAGIC, EEPROM_MAGIC_VALUE);
}

#endif
