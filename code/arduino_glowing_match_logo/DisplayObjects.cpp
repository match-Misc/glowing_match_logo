#include "DisplayObjects.h"
#include <string.h>

// Letter
Letter::Letter() : name(""), indices(nullptr), count(0), effect(nullptr), lastEffect(nullptr) {}

Letter::Letter(const char *n, const uint16_t *idx, uint16_t c)
  : name(n), indices(idx), count(c), effect(nullptr), lastEffect(nullptr) {}

void Letter::setEffect(Effect *e) {
  effect = e;
}

Effect* Letter::getEffect() {
  return effect;
}

void Letter::saveLastEffect() {
  lastEffect = effect;
}

void Letter::restoreLastEffect() {
  if (lastEffect) {
    effect = lastEffect;
  }
}

const char* Letter::getName() const {
  return name;
}

const uint16_t* Letter::getIndices() const {
  return indices;
}

uint16_t Letter::getCount() const {
  return count;
}

void Letter::apply(Adafruit_NeoPixel &strip, unsigned long now) {
  if (effect) {
    effect->apply(strip, indices, count, now);
  }
}

// PcbWord
PcbWord::PcbWord(Letter *ltrs, uint8_t cnt)
  : letters(ltrs), letterCount(cnt), wordEffect(nullptr), inWordMode(false), combinedCount(0) {
  rebuildCombinedIndices();
}

void PcbWord::rebuildCombinedIndices() {
  combinedCount = 0;

  for (uint8_t i = 0; i < letterCount; i++) {
    const uint16_t *idx = letters[i].getIndices();
    uint16_t c = letters[i].getCount();

    for (uint16_t j = 0; j < c; j++) {
      if (combinedCount < MAX_WORD_LEDS) {
        combinedIndices[combinedCount++] = idx[j];
      }
    }
  }
}

void PcbWord::setWordEffect(Effect *e) {
  // Save last effects from all letters before switching to word mode
  if (!inWordMode) {
    for (uint8_t i = 0; i < letterCount; i++) {
      letters[i].saveLastEffect();
    }
    inWordMode = true;
  }
  wordEffect = e;
}

void PcbWord::clearWordEffect() {
  // Restore last effects to all letters
  if (inWordMode) {
    for (uint8_t i = 0; i < letterCount; i++) {
      letters[i].restoreLastEffect();
    }
    inWordMode = false;
  }
  wordEffect = nullptr;
}

void PcbWord::setLetterEffect(uint8_t letterIndex, Effect *e) {
  if (letterIndex < letterCount) {
    letters[letterIndex].setEffect(e);
  }
}

bool PcbWord::isInWordMode() const {
  return inWordMode;
}

void PcbWord::apply(Adafruit_NeoPixel &strip, unsigned long now) {
  if (wordEffect) {
    wordEffect->apply(strip, combinedIndices, combinedCount, now);
  } else {
    for (uint8_t i = 0; i < letterCount; i++) {
      letters[i].apply(strip, now);
    }
  }
}

Letter* PcbWord::getLetterByName(const char *target) {
  for (uint8_t i = 0; i < letterCount; i++) {
    if (strcmp(letters[i].getName(), target) == 0) {
      return &letters[i];
    }
  }
  return nullptr;
}

uint8_t PcbWord::getLetterIndexByName(const char *target) {
  for (uint8_t i = 0; i < letterCount; i++) {
    if (strcmp(letters[i].getName(), target) == 0) {
      return i;
    }
  }
  return 255;  // Return invalid index if not found
}

Letter& PcbWord::getLetter(uint8_t i) {
  return letters[i];
}

uint8_t PcbWord::getLetterCount() const {
  return letterCount;
}

uint16_t PcbWord::getCombinedCount() const {
  return combinedCount;
}