#ifndef EFFECTS_H
#define EFFECTS_H

#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

// Helper function declaration
uint32_t colorWheel(Adafruit_NeoPixel &strip, uint8_t pos);

// Base class
class Effect {
public:
  virtual void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) = 0;
  virtual const char* getName() const = 0;
  virtual ~Effect() {}
};

// Solid effect
class SolidEffect : public Effect {
private:
  uint32_t color;
  const char* effectName;

public:
  SolidEffect(uint32_t c, const char* name = "Solid");
  void setColor(uint32_t c);
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Blink effect
class BlinkEffect : public Effect {
private:
  uint32_t colorOn;
  uint32_t colorOff;
  unsigned long interval;
  const char* effectName;

public:
  BlinkEffect(uint32_t onColor, uint32_t offColor, unsigned long ms, const char* name = "Blink");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Breathe effect
class BreatheEffect : public Effect {
private:
  uint8_t r, g, b;
  unsigned long period;
  const char* effectName;

public:
  BreatheEffect(uint8_t red, uint8_t green, uint8_t blue, unsigned long p, const char* name = "Breathe");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Rainbow effect
class RainbowEffect : public Effect {
private:
  uint8_t speed;
  uint8_t spacing;
  const char* effectName;

public:
  RainbowEffect(uint8_t s = 2, uint8_t sp = 12, const char* name = "Rainbow");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Chase effect
class ChaseEffect : public Effect {
private:
  uint32_t fg;
  uint32_t bg;
  unsigned long interval;
  uint8_t tailLength;
  const char* effectName;

public:
  ChaseEffect(uint32_t foreground, uint32_t background, unsigned long ms, uint8_t tail = 1, const char* name = "Chase");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Wipe effect
class WipeEffect : public Effect {
private:
  uint32_t color;
  uint32_t bg;
  unsigned long interval;
  const char* effectName;

public:
  WipeEffect(uint32_t c, uint32_t background, unsigned long ms, const char* name = "Wipe");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Off effect - disables the LEDs
class OffEffect : public Effect {
private:
  const char* effectName;

public:
  OffEffect(const char* name = "Off (LEDs disabled)");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Rainbow Cycle effect - cycles through full spectrum
class RainbowCycleEffect : public Effect {
private:
  unsigned long cyclePeriod;
  const char* effectName;

public:
  RainbowCycleEffect(unsigned long period, const char* name = "Rainbow Cycle");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Strobe effect - fast on/off blink
class StrobeEffect : public Effect {
private:
  uint32_t color;
  unsigned long interval;
  const char* effectName;

public:
  StrobeEffect(uint32_t c, unsigned long ms, const char* name = "Strobe");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Sparkle effect - random pixels light up
class SparkleEffect : public Effect {
private:
  uint32_t color;
  unsigned long interval;
  const char* effectName;

public:
  SparkleEffect(uint32_t c, unsigned long ms, const char* name = "Sparkle");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Color Alternate effect - alternates between two colors
class ColorAlternateEffect : public Effect {
private:
  uint32_t color1;
  uint32_t color2;
  unsigned long interval;
  const char* effectName;

public:
  ColorAlternateEffect(uint32_t c1, uint32_t c2, unsigned long ms, const char* name = "Color Alternate");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Theater Chase effect - moving dots with gaps
class TheaterChaseEffect : public Effect {
private:
  uint32_t color;
  uint32_t bg;
  unsigned long interval;
  const char* effectName;

public:
  TheaterChaseEffect(uint32_t c, uint32_t background, unsigned long ms, const char* name = "Theater Chase");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Wave effect - traveling wave
class WaveEffect : public Effect {
private:
  uint32_t color;
  unsigned long period;
  const char* effectName;

public:
  WaveEffect(uint32_t c, unsigned long p, const char* name = "Wave");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

// Fire effect - orange/red flickering
class FireEffect : public Effect {
private:
  const char* effectName;

public:
  FireEffect(const char* name = "Fire");
  void apply(Adafruit_NeoPixel &strip, const uint16_t *indices, uint16_t count, unsigned long now) override;
  const char* getName() const override;
};

#endif