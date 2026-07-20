#include <Adafruit_NeoPixel.h>
#include <EEPROM.h>
#include "Config.h"
#include "Effects.h"
#include "DisplayObjects.h"
#include "StateManager.h"
#include "SerialCommandHandler.h"
#include "BLECommandHandler.h"
#include "ButtonHandler.h"
#include "PersistentState.h"

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

// --------------------------------------------------
// Shared State Manager
// --------------------------------------------------
StateManager stateManager;

// local color helper for global object construction
uint32_t makeColor(uint8_t r, uint8_t g, uint8_t b) {
  return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b;
}

// --------------------------------------------------
// Build word from Config.h definition
// IMPORTANT: Edit Config.h to change word and LED layout
// --------------------------------------------------
Letter letters[] = {
  Letter(WORD_LETTERS[0].name, WORD_LETTERS[0].indices, WORD_LETTERS[0].count),
  Letter(WORD_LETTERS[1].name, WORD_LETTERS[1].indices, WORD_LETTERS[1].count),
  Letter(WORD_LETTERS[2].name, WORD_LETTERS[2].indices, WORD_LETTERS[2].count),
  Letter(WORD_LETTERS[3].name, WORD_LETTERS[3].indices, WORD_LETTERS[3].count),
  Letter(WORD_LETTERS[4].name, WORD_LETTERS[4].indices, WORD_LETTERS[4].count)
};

PcbWord pcbWord(letters, sizeof(letters) / sizeof(Letter));

// --------------------------------------------------
// Effects - See Config.h for color/timing settings
// --------------------------------------------------
OffEffect offEffect("Off (LEDs disabled)");

SolidEffect solidGreen(makeColor(COLOR_SOLID_GREEN), "Solid Green (default)");
SolidEffect solidRed(makeColor(COLOR_SOLID_RED), "Solid Red");
SolidEffect solidBlue(makeColor(COLOR_SOLID_BLUE), "Solid Blue");
SolidEffect solidWhite(makeColor(COLOR_SOLID_WHITE), "Solid White");

BlinkEffect blinkRed(makeColor(COLOR_BLINK_RED), 0, BLINK_INTERVAL, "Blink Red");
BlinkEffect blinkGreen(makeColor(COLOR_BLINK_GREEN), 0, BLINK_INTERVAL, "Blink Green");
BlinkEffect blinkYellow(makeColor(COLOR_BLINK_YELLOW), 0, BLINK_INTERVAL, "Blink Yellow");

BreatheEffect breatheRed(COLOR_BREATHE_RED, BREATHE_PERIOD, "Breathe Red");
BreatheEffect breatheGreen(COLOR_BREATHE_GREEN, BREATHE_PERIOD, "Breathe Green");
BreatheEffect breathePurple(COLOR_BREATHE_PURPLE, BREATHE_PERIOD, "Breathe Purple");

RainbowEffect rainbowWord(RAINBOW_SPEED, RAINBOW_DENSITY, "Rainbow");
ChaseEffect chaseWhite(makeColor(COLOR_CHASE_PRIMARY), makeColor(COLOR_CHASE_TAIL), CHASE_SPEED, CHASE_LENGTH, "Chase White");
ChaseEffect chaseGreen(makeColor(COLOR_CHASE_PRIMARY), makeColor(COLOR_SOLID_GREEN), CHASE_SPEED, CHASE_LENGTH, "Chase Green");
WipeEffect wipeBlue(makeColor(COLOR_WIPE_BLUE), 0, WIPE_SPEED, "Wipe Blue");
WipeEffect wipeGreen(makeColor(COLOR_SOLID_GREEN), 0, WIPE_SPEED, "Wipe Green");

RainbowCycleEffect rainbowCycle(3000, "Rainbow Cycle");
StrobeEffect strobeWhite(makeColor(255, 255, 255), STROBE_INTERVAL, "Strobe White");
SparkleEffect sparkleGreen(makeColor(COLOR_SOLID_GREEN), SPARKLE_INTERVAL, "Sparkle Green");
ColorAlternateEffect colorAltRedBlue(makeColor(COLOR_SOLID_RED), makeColor(COLOR_SOLID_BLUE), COLOR_ALT_INTERVAL, "Color Alt Red/Blue");
TheaterChaseEffect theaterWhite(makeColor(255, 255, 255), 0, THEATER_SPEED, "Theater Chase White");
WaveEffect waveGreen(makeColor(COLOR_SOLID_GREEN), WAVE_PERIOD, "Wave Green");
FireEffect fireEffect("Fire");

// Array of all effects for the command handler
Effect *allEffects[] = {
  &offEffect,       // 0 - Off (LEDs disabled)
  &solidGreen,      // 1 - Solid Green (default)
  &solidRed,        // 2 - Solid Red
  &solidBlue,       // 3 - Solid Blue
  &solidWhite,      // 4 - Solid White
  &blinkRed,        // 5 - Blink Red
  &blinkGreen,      // 6 - Blink Green
  &blinkYellow,     // 7 - Blink Yellow
  &breatheRed,      // 8 - Breathe Red
  &breatheGreen,    // 9 - Breathe Green
  &breathePurple,   // 10 - Breathe Purple
  &rainbowWord,     // 11 - Rainbow
  &chaseWhite,      // 12 - Chase White
  &chaseGreen,      // 13 - Chase Green
  &wipeBlue,        // 14 - Wipe Blue
  &wipeGreen,       // 15 - Wipe Green
  &rainbowCycle,    // 16 - Rainbow Cycle
  &strobeWhite,     // 17 - Strobe White
  &sparkleGreen,    // 18 - Sparkle Green
  &colorAltRedBlue, // 19 - Color Alt Red/Blue
  &theaterWhite,    // 20 - Theater Chase White
  &waveGreen,       // 21 - Wave Green
  &fireEffect       // 22 - Fire
};
const uint8_t numEffects = sizeof(allEffects) / sizeof(Effect*);

// Serial command handler
SerialCommandHandler serialHandler(pcbWord, strip, allEffects, numEffects, MAX_BRIGHTNESS, stateManager);

// BLE command handler
BLECommandHandler bleHandler(pcbWord, strip, allEffects, numEffects, MAX_BRIGHTNESS, stateManager);

// Button handler
ButtonHandler buttonHandler(pcbWord, strip, allEffects, numEffects, stateManager);

// --------------------------------------------------
void clearAll() {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, 0);
  }
}

void setPerLetterDemo() {
  pcbWord.clearWordEffect();

  letters[0].setEffect(&solidGreen);
  letters[1].setEffect(&solidGreen);
  letters[2].setEffect(&solidGreen);
  letters[3].setEffect(&solidGreen);
  letters[4].setEffect(&solidGreen);
}

void setup() {
  Serial.begin(115200);

  EEPROM.begin(EEPROM_SIZE_BYTES);

  strip.begin();
  strip.show();

  setPerLetterDemo();

  Serial.println("\nSystem ready.");
  
  // Load state from EEPROM
  stateManager.loadFromEEPROM(BRIGHTNESS);
  
  // Apply the brightness from saved state
  uint8_t brightnessPercent = stateManager.getBrightnessPercent();
  uint8_t brightnessValue = (brightnessPercent * MAX_BRIGHTNESS) / 100;
  strip.setBrightness(brightnessValue);
  Serial.print("Brightness restored: ");
  Serial.print(brightnessPercent);
  Serial.println("%");
  
  // Initialize button handler
  buttonHandler.begin();
  
  // Initialize BLE handler
  bleHandler.begin();
  
  serialHandler.printHelp();
}

void loop() {
  unsigned long now = millis();

  serialHandler.handle();
  bleHandler.handle();
  buttonHandler.handle();

  if (!buttonHandler.isLedsEnabled()) {
    delay(20);
    return;
  }

  // Skip effect application if BLE connection blink is in progress
  if (bleHandler.isBlinking()) {
    delay(20);
    return;
  }

  clearAll();
  pcbWord.apply(strip, now);
  strip.show();

  delay(20);
}