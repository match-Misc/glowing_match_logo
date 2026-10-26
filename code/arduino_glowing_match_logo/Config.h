#ifndef CONFIG_H
#define CONFIG_H

// ==================================================
// HARDWARE CONFIGURATION
// ==================================================
#define LED_PIN           3      // Pin connected to NeoPixel data line
#define NUM_LEDS          60     // Total number of LEDs in the strip
#define RING_PIN          2      // Additional WS2812 ring data input (GPIO)
#define RING_NUM_LEDS     16
#define RING_HALF_LEDS    8

// Viewed from the front: each list runs from bottom to top.
// Rotate/reorder these indices to match the physical ring orientation.
const uint16_t RING_LEFT_LEDS[RING_HALF_LEDS] = {0, 1, 2, 3, 4, 5, 6, 7};
const uint16_t RING_RIGHT_LEDS[RING_HALF_LEDS] = {15, 14, 13, 12, 11, 10, 9, 8};

// ==================================================
// BRIGHTNESS CONFIGURATION
// ==================================================
#define BRIGHTNESS        50     // Initial brightness in percent (0-100)
#define MAX_BRIGHTNESS    15    // Maximum brightness cap
#define RING_MAX_BRIGHTNESS 255  // Independent ring cap (0-255); 0 disables ring

static_assert(RING_MAX_BRIGHTNESS >= 0 && RING_MAX_BRIGHTNESS <= 255,
              "RING_MAX_BRIGHTNESS must be between 0 and 255");

// ==================================================
// BLE (BLUETOOTH LOW ENERGY) CONFIGURATION
// ==================================================
//#define BT_NAME           "GlowingMatch"  // Device name displayed in BLE scanner
#define BT_NAME           "RolfsGlowingMatch"  // Device name displayed in BLE scanner

// ==================================================
// LED LAYOUT - Define LED indices for each letter
// IMPORTANT: change these to match your real physical layout
// ==================================================
const uint16_t M_leds[] = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
const uint16_t A_leds[] = {14, 15, 16, 17, 18, 19, 20, 21, 22, 23};
//const uint16_t T_leds[] = {24, 25, 26, 27, 28, 29, 30, 31};   //different order
const uint16_t T_leds[] = {24, 25, 30, 31, 26, 27, 28, 29};
const uint16_t C_leds[] = {32, 33, 34, 35, 36, 37, 38};
const uint16_t H_leds[] = {39, 40, 41, 42, 43, 44, 45, 46, 47, 48};

// ==================================================
// WORD DEFINITION
// IMPORTANT: Define the word to display and its letter sequence
// Each letter must have corresponding LED indices defined above
// ==================================================
#define WORD_TEXT "MATCH"
#define WORD_LETTER_COUNT 5

// Array of letter definitions - letter name, LED indices, LED count
struct LetterDef {
  const char *name;
  const uint16_t *indices;
  uint16_t count;
};

const LetterDef WORD_LETTERS[] = {
  {"M", M_leds, sizeof(M_leds) / sizeof(uint16_t)},
  {"A", A_leds, sizeof(A_leds) / sizeof(uint16_t)},
  {"T", T_leds, sizeof(T_leds) / sizeof(uint16_t)},
  {"C", C_leds, sizeof(C_leds) / sizeof(uint16_t)},
  {"H", H_leds, sizeof(H_leds) / sizeof(uint16_t)}
};


// ==================================================
// EFFECT COLOR CONFIGURATION
// ==================================================

// Solid effect colors
#define COLOR_SOLID_GREEN   0, 255, 0
#define COLOR_SOLID_RED     255, 0, 0
#define COLOR_SOLID_BLUE    0, 0, 255
#define COLOR_SOLID_WHITE   255, 255, 255

// Blink effect colors and timings
#define COLOR_BLINK_RED     255, 0, 0
#define COLOR_BLINK_GREEN   0, 255, 0
#define COLOR_BLINK_YELLOW  255, 180, 0
#define BLINK_INTERVAL      400   // milliseconds

// Breathe effect colors and timings
#define COLOR_BREATHE_RED     255, 0, 0
#define COLOR_BREATHE_GREEN   0, 255, 0
#define COLOR_BREATHE_PURPLE  180, 0, 255
#define BREATHE_PERIOD        4000  // milliseconds (full cycle)

// Chase effect colors and timing
#define COLOR_CHASE_PRIMARY   255, 255, 255  // White
#define COLOR_CHASE_TAIL      0, 0, 20       // Dark blue
#define CHASE_SPEED           120            // milliseconds per step
#define CHASE_LENGTH          3              // LEDs

// Wipe effect color and timing
#define COLOR_WIPE_BLUE       0, 0, 255
#define WIPE_SPEED            100            // milliseconds per step

// Rainbow effect configuration
#define RAINBOW_SPEED         3              // Speed multiplier
#define RAINBOW_DENSITY       12             // Color density/width

// Pulse effect configuration (more dramatic than breathe)
#define PULSE_PERIOD          3000           // milliseconds (full cycle)

// Strobe effect configuration (fast blink)
#define STROBE_INTERVAL       100            // milliseconds (fast!)

// Sparkle effect configuration
#define SPARKLE_INTERVAL      200            // milliseconds

// Color Alternate effect configuration
#define COLOR_ALT_INTERVAL    500            // milliseconds

// Theater Chase effect configuration
#define THEATER_SPEED         100            // milliseconds per step

// Wave effect configuration
#define WAVE_PERIOD           2000           // milliseconds

// Fire effect - uses random flickering
#define FIRE_FLICKER          50             // milliseconds

// ==================================================
// EFFECT DEFINITIONS
// ==================================================
// This array defines all available effects in order
// Modify this section to add/remove/reorder effects
//
// Format: effect_type(parameters)  // N - Description
//
// Available effects:
//   SolidEffect(color)
//   BlinkEffect(onColor, offColor, interval)
//   BreatheEffect(r, g, b, period)
//   RainbowEffect(speed, density)
//   ChaseEffect(primaryColor, tailColor, speed, length)
//   WipeEffect(color, offColor, speed)

#endif
