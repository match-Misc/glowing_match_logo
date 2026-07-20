#ifndef BUTTONHANDLER_H
#define BUTTONHANDLER_H

#include <Arduino.h>
#include "DisplayObjects.h"
#include "Effects.h"
#include "StateManager.h"

#define BUTTON_PIN 21
#define LONG_PRESS_TIME 1000  // milliseconds to trigger long press

class ButtonHandler {
private:
  PcbWord &pcbWord;
  Adafruit_NeoPixel &strip;
  
  // Array to store effect pointers
  Effect **effects;
  uint8_t effectCount;
  
  // Button state tracking
  bool buttonPressed;
  unsigned long buttonPressTime;
  bool longPressHandled;
  
  // Reference to shared state
  StateManager &stateManager;

public:
  ButtonHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, StateManager &sm);
  
  void begin();
  void handle();
  bool isLedsEnabled() const;
  void setLedsEnabled(bool enabled);
  
private:
  void onShortPress();
  void onLongPress();
  void toggleLEDs();
  void nextWordEffect();
  void applyLedState();
};

#endif
