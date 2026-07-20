#include "SerialCommandHandler.h"
#include <string.h>
#include <ctype.h>

SerialCommandHandler::SerialCommandHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, uint8_t maxBright, StateManager &sm)
  : pcbWord(w), strip(s), effects(eff), effectCount(effCount), maxBrightness(maxBright), stateManager(sm) {}

void SerialCommandHandler::handle() {
  if (!Serial.available()) return;
  
  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  
  if (cmd.length() == 0) return;
  
  if (cmd.equalsIgnoreCase("help")) {
    printHelp();
    return;
  }
  
  if (cmd.equalsIgnoreCase("effects")) {
    printEffects();
    return;
  }
  
  if (cmd.equalsIgnoreCase("word")) {
    Serial.print("Configured word: ");
    for (uint8_t i = 0; i < pcbWord.getLetterCount(); i++) {
      Letter &letter = pcbWord.getLetter(i);
      Serial.print(letter.getName());
    }
    Serial.println();
    return;
  }
  
  if (cmd.equalsIgnoreCase("brightness")) {
    uint8_t percent = stateManager.getBrightnessPercent();
    uint8_t brightnessValue = (percent * maxBrightness) / 100;
    Serial.print("Current brightness: ");
    Serial.print(percent);
    Serial.print("% (");
    Serial.print(brightnessValue);
    Serial.println("/255)");
    return;
  }
  
  processCommand(cmd);
}

void SerialCommandHandler::processCommand(const String &cmd) {
  if (cmd.equalsIgnoreCase("on")) {
    stateManager.setLedsEnabled(true);
    Serial.println("LEDs enabled");
    // Clear all LEDs and show to apply the enabled state
    for (int i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }

  if (cmd.equalsIgnoreCase("off")) {
    stateManager.setLedsEnabled(false);
    Serial.println("LEDs disabled");
    // Turn off all LEDs
    for (int i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }

  // Check for "word.X" format
  if (cmd.startsWith("word.") || cmd.startsWith("WORD.")) {
    String modeStr = cmd.substring(5);
    uint8_t mode = modeStr.toInt();
    if (mode >= 0 && mode < effectCount) {
      setWordMode(mode);
      return;
    } else {
      Serial.print("Invalid word mode: ");
      Serial.println(mode);
      return;
    }
  }
  
  // Check for "brightness.X" format (percentage 0-100)
  if (cmd.startsWith("brightness.") || cmd.startsWith("BRIGHTNESS.")) {
    String percentStr = cmd.substring(11);
    uint8_t percent = percentStr.toInt();
    if (percent >= 0 && percent <= 100) {
      setBrightness(percent);
      return;
    } else {
      Serial.println("Brightness must be 0-100 (percent)");
      return;
    }
  }
  
  // Check for "letter.X" format (e.g., "m.8", "M.5", or "m.1 a.3 t.3 c.4 h.1")
  // Can be single or multiple space-separated pairs
  if (cmd.length() >= 3 && (cmd.indexOf('.') > 0)) {
    bool validMultiCommand = false;
    int pos = 0;
    
    // Try to parse as multiple letter.effect pairs
    while (pos < cmd.length()) {
      // Skip spaces
      while (pos < cmd.length() && cmd[pos] == ' ') {
        pos++;
      }
      
      if (pos >= cmd.length()) break;
      
      // Get letter
      char letter = cmd[pos];
      pos++;
      
      // Expect a dot
      if (pos >= cmd.length() || cmd[pos] != '.') {
        break;
      }
      pos++;
      
      // Get effect number
      String modeStr = "";
      while (pos < cmd.length() && cmd[pos] >= '0' && cmd[pos] <= '9') {
        modeStr += cmd[pos];
        pos++;
      }
      
      if (modeStr.length() == 0) {
        break;
      }
      
      uint8_t mode = modeStr.toInt();
      
      if (!isValidLetter(letter)) {
        Serial.print("Invalid letter: ");
        Serial.println(letter);
        return;
      }
      
      if (mode >= 0 && mode < effectCount) {
        setLetterEffect(letter, mode);
        validMultiCommand = true;
      } else {
        Serial.print("Invalid effect mode: ");
        Serial.println(mode);
        return;
      }
    }
    
    if (validMultiCommand) {
      return;
    }
  }
  
  Serial.println("Invalid command format. Type 'help' for instructions.");
}

void SerialCommandHandler::setLetterEffect(char letter, uint8_t mode) {
  // If we're in word mode, exit first
  if (pcbWord.isInWordMode()) {
    pcbWord.clearWordEffect();
  }
  
  char normalized = normalizeLetterCase(letter);
  String letterStr(normalized);
  
  Letter *targetLetter = pcbWord.getLetterByName(letterStr.c_str());
  
  if (targetLetter) {
    if (mode < effectCount && effects[mode]) {
      targetLetter->setEffect(effects[mode]);
      Serial.print("Letter ");
      Serial.print(letter);
      Serial.print(" set to effect ");
      Serial.println(mode);
      stateManager.setWordModeEnabled(false);
      
      // Save letter effect index to StateManager
      uint8_t letterIndex = pcbWord.getLetterIndexByName(letterStr.c_str());
      if (letterIndex < 255) {
        stateManager.setLetterEffectIndex(letterIndex, mode);
      }
      
      // Enable LEDs when changing effect mode (except for effect 0 which is off)
      if (mode != 0) {
        stateManager.setLedsEnabled(true);
      }
    }
  }
}

void SerialCommandHandler::setWordMode(uint8_t mode) {
  if (mode < effectCount && effects[mode]) {
    pcbWord.setWordEffect(effects[mode]);
    Serial.print("Word mode enabled with effect ");
    Serial.println(mode);
    stateManager.setCurrentWordEffectIndex(mode);
    stateManager.setWordModeEnabled(true);
    // Enable LEDs when changing effect mode (except for effect 0 which is off)
    if (mode != 0) {
      stateManager.setLedsEnabled(true);
    }
  }
}

void SerialCommandHandler::setBrightness(uint8_t percent) {
  // Convert percentage (0-100) to brightness value (0-maxBrightness)
  uint8_t brightnessValue = (percent * maxBrightness) / 100;
  strip.setBrightness(brightnessValue);
  Serial.print("Brightness set to ");
  Serial.print(percent);
  Serial.print("% (");
  Serial.print(brightnessValue);
  Serial.println("/255)");
  
  // Save to state manager
  stateManager.setBrightnessPercent(percent);
}

bool SerialCommandHandler::isValidLetter(char letter) {
  char normalized = normalizeLetterCase(letter);
  Letter *test = pcbWord.getLetterByName(String(normalized).c_str());
  return test != nullptr;
}

char SerialCommandHandler::normalizeLetterCase(char letter) {
  return toupper(letter);
}

void SerialCommandHandler::printHelp() {
  Serial.println("\n========== COMMAND HELP ==========");
  Serial.println("Format: LETTER.MODE or word.MODE or brightness.PERCENT or on/off/effects/word/brightness");
  Serial.println("\nLETTER: Use any letter from the word (M, A, T, C, H)");
  Serial.println("        Case-insensitive (m or M both work)");
  Serial.println("MODE:   Effect number (0 to " + String(effectCount - 1) + ")");
  Serial.println("PERCENT: Brightness (0-100)");
  Serial.println("\nExamples:");
  Serial.println("  m.0           - Turn off letter M");
  Serial.println("  m.1           - Set letter M to effect 1");
  Serial.println("  A.3           - Set letter A to effect 3");
  Serial.println("  word.0        - Turn off word mode");
  Serial.println("  word.5        - Enable word mode with effect 5");
  Serial.println("  brightness.75 - Set brightness to 75%");
  Serial.println("  on            - Enable LEDs");
  Serial.println("  off           - Disable LEDs");
  Serial.println("  effects       - List all available effects");
  Serial.println("  word          - Show configured word");
  Serial.println("  brightness    - Show current brightness level");
  Serial.println("\nBrightness:");
  Serial.println("  Maximum: " + String(maxBrightness) + "/255");
  Serial.println("  Format:  brightness.0 to brightness.100 (to set)");
  Serial.println("           brightness (to query current)");
  Serial.println("\nWhen switching from word mode back to letter mode,");
  Serial.println("the last letter effects will be restored automatically.");
  Serial.println("==================================\n");
}

void SerialCommandHandler::printEffects() {
  Serial.println("\n========== AVAILABLE EFFECTS ==========");
  for (uint8_t i = 0; i < effectCount; i++) {
    Serial.print(i);
    Serial.print(" - ");
    Serial.println(effects[i]->getName());
  }
  Serial.println("======================================\n");
}
