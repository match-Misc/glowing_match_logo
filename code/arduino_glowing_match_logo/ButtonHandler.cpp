#include "ButtonHandler.h"

ButtonHandler::ButtonHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, StateManager &sm)
  : pcbWord(w), strip(s), effects(eff), effectCount(effCount), 
    buttonPressed(false), buttonPressTime(0), longPressHandled(false), stateManager(sm) {}

void ButtonHandler::begin() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.println("Button handler initialized on pin " + String(BUTTON_PIN));
  
  // Apply LED state
  applyLedState();
  
  // Restore letter effects first
  for (uint8_t i = 0; i < 5; i++) {  // MAX_LETTERS = 5
    uint8_t effectIndex = stateManager.getLetterEffectIndex(i);
    if (effectIndex < effectCount && effects[effectIndex] != nullptr) {
      pcbWord.setLetterEffect(i, effects[effectIndex]);
      Serial.print("Restored letter ");
      Serial.print(i);
      Serial.print(" effect: ");
      Serial.println(effectIndex);
    }
  }
  
  // Restore word mode if it was enabled
  if (stateManager.isWordModeEnabled()) {
    uint8_t effectIndex = stateManager.getCurrentWordEffectIndex();
    if (effectIndex < effectCount && effects[effectIndex] != nullptr) {
      pcbWord.setWordEffect(effects[effectIndex]);
      Serial.print("Restored word effect: ");
      Serial.println(effectIndex);
    }
  }
}

bool ButtonHandler::isLedsEnabled() const {
  return stateManager.isLedsEnabled();
}

void ButtonHandler::setLedsEnabled(bool enabled) {
  if (stateManager.isLedsEnabled() == enabled) {
    Serial.println(enabled ? "LEDs already enabled" : "LEDs already disabled");
    return;
  }

  stateManager.setLedsEnabled(enabled);
  applyLedState();
}

void ButtonHandler::applyLedState() {
  if (stateManager.isLedsEnabled()) {
    Serial.println("LEDs enabled");
    strip.show();
  } else {
    Serial.println("LEDs disabled");
    for (int i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
  }
}

void ButtonHandler::handle() {
  bool currentButtonState = digitalRead(BUTTON_PIN);
  unsigned long now = millis();
  
  // Button pressed (HIGH when not pressed, LOW when pressed - typical for pullup)
  if (!currentButtonState && !buttonPressed) {
    // Button just pressed
    buttonPressed = true;
    buttonPressTime = now;
    longPressHandled = false;
  } 
  else if (!currentButtonState && buttonPressed && !longPressHandled) {
    // Button still held down
    if (now - buttonPressTime >= LONG_PRESS_TIME) {
      onLongPress();
      longPressHandled = true;
    }
  } 
  else if (currentButtonState && buttonPressed) {
    // Button released
    buttonPressed = false;
    
    // Only trigger short press if long press wasn't handled
    if (!longPressHandled) {
      onShortPress();
    }
  }
}

void ButtonHandler::onShortPress() {
  Serial.println("Button: Short press");
  
  // If LEDs are off, just turn them on without changing effect
  if (!stateManager.isLedsEnabled()) {
    setLedsEnabled(true);
    Serial.println("LEDs turned on");
    return;
  }
  
  // LEDs are on, so switch word effect mode
  Serial.println("Switching word effect mode");
  
  // Enter word mode with effects
  if (!pcbWord.isInWordMode()) {
    // Just entering word mode, apply first effect
    uint8_t effectIndex = 0;
    stateManager.setCurrentWordEffectIndex(effectIndex);
    stateManager.setWordModeEnabled(true);
    pcbWord.setWordEffect(effects[effectIndex]);
    Serial.print("Word mode: effect ");
    Serial.println(effectIndex);
  } else {
    // Already in word mode, switch to next effect
    nextWordEffect();
  }
}

void ButtonHandler::onLongPress() {
  toggleLEDs();
}

void ButtonHandler::toggleLEDs() {
  setLedsEnabled(!stateManager.isLedsEnabled());
}

void ButtonHandler::nextWordEffect() {
  // Move to next effect
  uint8_t effectIndex = stateManager.getCurrentWordEffectIndex();
  effectIndex++;
  if (effectIndex >= effectCount) {
    effectIndex = 0;
  }
  
  stateManager.setCurrentWordEffectIndex(effectIndex);
  
  // Enable LEDs when changing effect mode
  if (!stateManager.isLedsEnabled()) {
    setLedsEnabled(true);
  }
  
  // Apply the effect
  pcbWord.setWordEffect(effects[effectIndex]);
  Serial.print("Word effect switched to: ");
  Serial.println(effectIndex);
}
