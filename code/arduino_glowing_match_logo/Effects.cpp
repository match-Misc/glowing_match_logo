#include "Effects.h"
#include <math.h>

uint32_t colorWheel(Adafruit_NeoPixel &strip, uint8_t pos) {
  if (pos < 85) {
    return strip.Color(pos * 3, 255 - pos * 3, 0);
  } else if (pos < 170) {
    pos -= 85;
    return strip.Color(255 - pos * 3, 0, pos * 3);
  } else {
    pos -= 170;
    return strip.Color(0, pos * 3, 255 - pos * 3);
  }
}

// --------------------------------------------------
// SolidEffect
// --------------------------------------------------
SolidEffect::SolidEffect(uint32_t c, const char* name) : color(c), effectName(name) {}

void SolidEffect::setColor(uint32_t c) {
  color = c;
}

void SolidEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], color);
  }
}

const char* SolidEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// BlinkEffect
// --------------------------------------------------
BlinkEffect::BlinkEffect(uint32_t onColor, uint32_t offColor, unsigned long ms, const char* name)
  : colorOn(onColor), colorOff(offColor), interval(ms), effectName(name) {}

void BlinkEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  uint32_t c = ((now / interval) % 2 == 0) ? colorOn : colorOff;
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], c);
  }
}

const char* BlinkEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// BreatheEffect
// --------------------------------------------------
BreatheEffect::BreatheEffect(uint8_t red, uint8_t green, uint8_t blue, unsigned long p, const char* name)
  : r(red), g(green), b(blue), period(p), effectName(name) {}

void BreatheEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  float phase = (now % period) / (float)period;
  float x = 0.5 - 0.5 * cos(2.0 * PI * phase);

  uint8_t rr = (uint8_t)(r * x);
  uint8_t gg = (uint8_t)(g * x);
  uint8_t bb = (uint8_t)(b * x);

  uint32_t c = strip.Color(rr, gg, bb);

  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], c);
  }
}

const char* BreatheEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// RainbowEffect
// --------------------------------------------------
RainbowEffect::RainbowEffect(uint8_t s, uint8_t sp, const char* name) : speed(s), spacing(sp), effectName(name) {}

void RainbowEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  uint8_t shift = (now / 20) * speed;

  for (uint16_t i = 0; i < count; i++) {
    uint8_t pos = (i * spacing + shift) & 255;
    strip.setPixelColor(indices[i], colorWheel(strip, pos));
  }
}

const char* RainbowEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// ChaseEffect
// --------------------------------------------------
ChaseEffect::ChaseEffect(uint32_t foreground, uint32_t background, unsigned long ms, uint8_t tail, const char* name)
  : fg(foreground), bg(background), interval(ms), tailLength(tail), effectName(name) {}

void ChaseEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  if (count == 0) return;

  uint16_t head = (now / interval) % count;

  for (uint16_t i = 0; i < count; i++) {
    bool on = false;
    for (uint8_t t = 0; t < tailLength; t++) {
      uint16_t pos = (head + count - t) % count;
      if (i == pos) {
        on = true;
        break;
      }
    }
    strip.setPixelColor(indices[i], on ? fg : bg);
  }
}

const char* ChaseEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// WipeEffect
// --------------------------------------------------
WipeEffect::WipeEffect(uint32_t c, uint32_t background, unsigned long ms, const char* name)
  : color(c), bg(background), interval(ms), effectName(name) {}

void WipeEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  uint16_t filled = (now / interval) % (count + 1);

  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], (i < filled) ? color : bg);
  }
}

const char* WipeEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// OffEffect
// --------------------------------------------------
OffEffect::OffEffect(const char* name) : effectName(name) {}

void OffEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], 0);
  }
}

const char* OffEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// RainbowCycleEffect
// --------------------------------------------------
RainbowCycleEffect::RainbowCycleEffect(unsigned long period, const char* name)
  : cyclePeriod(period), effectName(name) {}

void RainbowCycleEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  // Cycle all pixels through the full color spectrum
  float phase = (now % cyclePeriod) / (float)cyclePeriod;
  uint16_t hue = (uint16_t)(phase * 65536.0);  // 0-65535 represents full HSV hue circle

  uint32_t c = strip.gamma32(strip.ColorHSV(hue, 255, 255));

  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], c);
  }
}

const char* RainbowCycleEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// StrobeEffect
// --------------------------------------------------
StrobeEffect::StrobeEffect(uint32_t c, unsigned long ms, const char* name)
  : color(c), interval(ms), effectName(name) {}

void StrobeEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  uint32_t c = ((now / interval) % 2 == 0) ? color : 0;
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], c);
  }
}

const char* StrobeEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// SparkleEffect
// --------------------------------------------------
SparkleEffect::SparkleEffect(uint32_t c, unsigned long ms, const char* name)
  : color(c), interval(ms), effectName(name) {}

void SparkleEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  // Clear all
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], 0);
  }
  
  // Add random sparkles
  randomSeed(now / interval);  // Seed for pseudo-random pattern
  for (uint16_t i = 0; i < count; i++) {
    if (random(10) < 2) {  // 20% chance
      strip.setPixelColor(indices[i], color);
    }
  }
}

const char* SparkleEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// ColorAlternateEffect
// --------------------------------------------------
ColorAlternateEffect::ColorAlternateEffect(uint32_t c1, uint32_t c2, unsigned long ms, const char* name)
  : color1(c1), color2(c2), interval(ms), effectName(name) {}

void ColorAlternateEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  uint32_t c = ((now / interval) % 2 == 0) ? color1 : color2;
  for (uint16_t i = 0; i < count; i++) {
    strip.setPixelColor(indices[i], c);
  }
}

const char* ColorAlternateEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// TheaterChaseEffect
// --------------------------------------------------
TheaterChaseEffect::TheaterChaseEffect(uint32_t c, uint32_t background, unsigned long ms, const char* name)
  : color(c), bg(background), interval(ms), effectName(name) {}

void TheaterChaseEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  if (count == 0) return;
  
  uint16_t step = (now / interval) % count;
  
  for (uint16_t i = 0; i < count; i++) {
    // Show 3 pixels on, 3 off pattern
    if ((i + step) % 6 < 3) {
      strip.setPixelColor(indices[i], color);
    } else {
      strip.setPixelColor(indices[i], bg);
    }
  }
}

const char* TheaterChaseEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// WaveEffect
// --------------------------------------------------
WaveEffect::WaveEffect(uint32_t c, unsigned long p, const char* name)
  : color(c), period(p), effectName(name) {}

void WaveEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  if (count == 0) return;
  
  float phase = (now % period) / (float)period;
  
  for (uint16_t i = 0; i < count; i++) {
    // Wave effect using sine wave
    float x = (i / (float)count + phase);
    float brightness = 0.5 + 0.5 * sin(2.0 * PI * x);
    
    uint8_t r = (uint8_t)((color >> 16) & 0xFF);
    uint8_t g = (uint8_t)((color >> 8) & 0xFF);
    uint8_t b = (uint8_t)(color & 0xFF);
    
    strip.setPixelColor(indices[i], strip.Color(r * brightness, g * brightness, b * brightness));
  }
}

const char* WaveEffect::getName() const {
  return effectName;
}

// --------------------------------------------------
// FireEffect
// --------------------------------------------------
FireEffect::FireEffect(const char* name)
  : effectName(name) {}

void FireEffect::apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) {
  // Fire effect with orange/red flickering
  for (uint16_t i = 0; i < count; i++) {
    randomSeed(now + i);
    uint8_t flicker = random(100, 255);
    uint8_t r = 255;
    uint8_t g = random(80, 180);
    uint8_t b = 0;
    
    // Dim based on flicker
    r = (r * flicker) / 255;
    g = (g * flicker) / 255;
    
    strip.setPixelColor(indices[i], strip.Color(r, g, b));
  }
}

const char* FireEffect::getName() const {
  return effectName;
}