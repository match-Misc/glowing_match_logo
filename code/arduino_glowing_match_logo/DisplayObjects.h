#ifndef DISPLAYOBJECTS_H
#define DISPLAYOBJECTS_H

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include "Effects.h"

#define MAX_WORD_LEDS 200
#define MAX_EFFECTS 10

class Letter {
private:
  const char *name;
  const uint16_t *indices;
  uint16_t count;
  Effect *effect;
  Effect *lastEffect;  // Track last effect before word mode

public:
  Letter();
  Letter(const char *n, const uint16_t *idx, uint16_t c);

  void setEffect(Effect *e);
  Effect* getEffect();
  void saveLastEffect();
  void restoreLastEffect();

  const char* getName() const;
  const uint16_t* getIndices() const;
  uint16_t getCount() const;

  void apply(Adafruit_NeoPixel &strip, unsigned long now);
};

class PcbWord {
private:
  Letter *letters;
  uint8_t letterCount;
  Effect *wordEffect;
  bool inWordMode;

  uint16_t combinedIndices[MAX_WORD_LEDS];
  uint16_t combinedCount;

public:
  PcbWord(Letter *ltrs, uint8_t cnt);

  void rebuildCombinedIndices();

  void setWordEffect(Effect *e);
  void clearWordEffect();
  bool isInWordMode() const;
  
  void setLetterEffect(uint8_t letterIndex, Effect *e);

  void apply(Adafruit_NeoPixel &strip, unsigned long now);

  Letter* getLetterByName(const char *target);
  uint8_t getLetterIndexByName(const char *target);
  Letter& getLetter(uint8_t i);
  uint8_t getLetterCount() const;

  uint16_t getCombinedCount() const;
};

#endif