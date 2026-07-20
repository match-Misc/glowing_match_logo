#include "BLECommandHandler.h"
#include <string.h>
#include <ctype.h>

// Global pointer for callbacks
BLECommandHandler *g_handler = nullptr;

void MyServerCallbacks::onConnect(BLEServer *pServer) {
  if (handler) {
    handler->setConnected(true);
    Serial.println("✓ BLE Client Connected");
  }
}

void MyServerCallbacks::onDisconnect(BLEServer *pServer) {
  if (handler) {
    handler->setConnected(false);
    Serial.println("✗ BLE Client Disconnected");
    // Restart advertising
    pServer->getAdvertising()->start();
  }
}

void MyCharacteristicCallbacks::onWrite(BLECharacteristic *pCharacteristic) {
  if (handler) {
    // Get the value as raw bytes and length
    uint8_t *pData = pCharacteristic->getData();
    size_t length = pCharacteristic->getLength();
    
    if (length > 0 && pData != nullptr) {
      // Convert bytes to String
      String cmd = "";
      for (size_t i = 0; i < length; i++) {
        cmd += (char)pData[i];
      }
      cmd.trim();
      if (cmd.length() > 0) {
        Serial.print("[BLE] ");
        Serial.println(cmd);
        handler->processCommand(cmd);
      }
    }
  }
}

// =============================================

BLECommandHandler::BLECommandHandler(PcbWord &w, Adafruit_NeoPixel &s, Effect **eff, uint8_t effCount, uint8_t maxBright, StateManager &sm)
  : pcbWord(w), strip(s), effects(eff), effectCount(effCount), maxBrightness(maxBright), stateManager(sm),
    pServer(nullptr), pCommandChar(nullptr), pResponseChar(nullptr), deviceConnected(false),
    blinkInProgress(false), blinkCount(0), blinkStartTime(0), savedBrightness(0) {
  g_handler = this;
}

void BLECommandHandler::begin() {
  Serial.println("\n[BLE] Initializing BLE...");
  
  // Initialize BLE device
  BLEDevice::init(BT_NAME);
  
  // Create BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks(this));
  
  // Create BLE Service
  BLEService *pService = pServer->createService(BLE_SERVICE_UUID);
  
  // Create Command Characteristic (write from client)
  pCommandChar = pService->createCharacteristic(
    BLE_COMMAND_CHAR_UUID,
    BLECharacteristic::PROPERTY_WRITE |
    BLECharacteristic::PROPERTY_WRITE_NR
  );
  pCommandChar->setCallbacks(new MyCharacteristicCallbacks(this));
  pCommandChar->setValue("Ready for commands");
  
  // Create Response Characteristic (read from client)
  pResponseChar = pService->createCharacteristic(
    BLE_RESPONSE_CHAR_UUID,
    BLECharacteristic::PROPERTY_READ |
    BLECharacteristic::PROPERTY_NOTIFY
  );
  pResponseChar->addDescriptor(new BLE2902());
  pResponseChar->setValue("Connected");
  
  pService->start();
  
  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(BLE_SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);
  pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();
  
  Serial.println("[BLE] ✓ BLE initialized successfully!");
  Serial.print("[BLE] Device Name: ");
  Serial.println(BT_NAME);
  Serial.println("[BLE] Waiting for connection...");
}

void BLECommandHandler::handle() {
  // Handle connection blink animation
  if (blinkInProgress) {
    unsigned long elapsed = millis() - blinkStartTime;
    
    // Total duration: 3 blinks, 1 second per blink = 3 seconds
    // Each blink: 500ms on, 500ms off
    const unsigned long blinkDuration = 500;  // 500ms per phase
    const unsigned long totalBlinkTime = 3000; // 3 seconds for 3 complete blinks
    
    if (elapsed < totalBlinkTime) {
      // Currently blinking
      uint8_t phase = (elapsed / blinkDuration) % 2;  // 0 = on, 1 = off
      
      if (phase == 0) {
        // Blink ON - show blue
        for (int i = 0; i < strip.numPixels(); i++) {
          strip.setPixelColor(i, strip.Color(0, 0, 255));  // Blue
        }
      } else {
        // Blink OFF - turn off
        for (int i = 0; i < strip.numPixels(); i++) {
          strip.setPixelColor(i, 0);
        }
      }
      strip.show();
    } else {
      // Blinking complete - restore previous state
      blinkInProgress = false;
      
      // Restore saved brightness
      uint8_t brightnessValue = (savedBrightness * maxBrightness) / 100;
      strip.setBrightness(brightnessValue);
      
      // Reapply the word effect to restore state
      pcbWord.apply(strip, millis());
      strip.show();
      
      Serial.println("[BLE] Connection blink complete, state restored");
    }
  }
  
  // BLE is event-driven, so we just need to process any pending commands
  // The callbacks will trigger when data is received
  delay(10);
}

void BLECommandHandler::setConnected(bool connected) {
  deviceConnected = connected;
  if (connected) {
    pResponseChar->setValue("Connected");
    pResponseChar->notify();
    // Start connection blink
    performConnectionBlink();
  }
}

bool BLECommandHandler::isConnected() const {
  return deviceConnected;
}

bool BLECommandHandler::isBlinking() const {
  return blinkInProgress;
}

void BLECommandHandler::processCommand(const String &cmd) {
  if (cmd.equalsIgnoreCase("on")) {
    stateManager.setLedsEnabled(true);
    sendResponse("OK:LEDS_ON");
    Serial.println("[BLE] LEDs enabled");
    for (int i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }

  if (cmd.equalsIgnoreCase("off")) {
    stateManager.setLedsEnabled(false);
    sendResponse("OK:LEDS_OFF");
    Serial.println("[BLE] LEDs disabled");
    for (int i = 0; i < strip.numPixels(); i++) {
      strip.setPixelColor(i, 0);
    }
    strip.show();
    return;
  }

  if (cmd.equalsIgnoreCase("help")) {
    printHelp();
    return;
  }

  if (cmd.equalsIgnoreCase("effects")) {
    printEffects();
    return;
  }

  if (cmd.equalsIgnoreCase("word")) {
    String word = "Configured word: ";
    for (uint8_t i = 0; i < pcbWord.getLetterCount(); i++) {
      Letter &letter = pcbWord.getLetter(i);
      word += letter.getName();
    }
    sendResponse(word);
    Serial.println("[BLE] " + word);
    return;
  }

  if (cmd.equalsIgnoreCase("brightness")) {
    uint8_t percent = stateManager.getBrightnessPercent();
    uint8_t brightnessValue = (percent * maxBrightness) / 100;
    String response = "Current brightness: ";
    response += String(percent);
    response += "% (";
    response += String(brightnessValue);
    response += "/255)";
    sendResponse(response);
    Serial.println("[BLE] " + response);
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
      sendResponse("ERR:INVALID_MODE");
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
      sendResponse("ERR:BRIGHTNESS_RANGE");
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
        sendResponse("ERR:INVALID_LETTER");
        return;
      }
      
      if (mode >= 0 && mode < effectCount) {
        setLetterEffect(letter, mode);
        validMultiCommand = true;
      } else {
        sendResponse("ERR:INVALID_MODE");
        return;
      }
    }
    
    if (validMultiCommand) {
      sendResponse("OK:EFFECTS_SET");
      return;
    }
  }
  
  sendResponse("ERR:INVALID_COMMAND");
}

void BLECommandHandler::setLetterEffect(char letter, uint8_t mode) {
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
      sendResponse("OK:" + String(letter) + "_EFFECT_" + String(mode));
      Serial.print("[BLE] Letter ");
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

void BLECommandHandler::setWordMode(uint8_t mode) {
  if (mode < effectCount && effects[mode]) {
    pcbWord.setWordEffect(effects[mode]);
    sendResponse("OK:WORD_MODE_" + String(mode));
    Serial.print("[BLE] Word mode enabled with effect ");
    Serial.println(mode);
    stateManager.setCurrentWordEffectIndex(mode);
    stateManager.setWordModeEnabled(true);
    // Enable LEDs when changing effect mode (except for effect 0 which is off)
    if (mode != 0) {
      stateManager.setLedsEnabled(true);
    }
  }
}

void BLECommandHandler::setBrightness(uint8_t percent) {
  // Convert percentage (0-100) to brightness value (0-maxBrightness)
  uint8_t brightnessValue = (percent * maxBrightness) / 100;
  strip.setBrightness(brightnessValue);
  sendResponse("OK:BRIGHTNESS_" + String(percent));
  Serial.print("[BLE] Brightness set to ");
  Serial.print(percent);
  Serial.println("%");
  
  // Save to state manager
  stateManager.setBrightnessPercent(percent);
}

void BLECommandHandler::sendResponse(const String &response) {
  if (pResponseChar) {
    pResponseChar->setValue(response.c_str());
    pResponseChar->notify();
  }
}

bool BLECommandHandler::isValidLetter(char letter) {
  char normalized = normalizeLetterCase(letter);
  Letter *test = pcbWord.getLetterByName(String(normalized).c_str());
  return test != nullptr;
}

char BLECommandHandler::normalizeLetterCase(char letter) {
  return toupper(letter);
}

void BLECommandHandler::printHelp() {
  String help = "\n=== LED CONTROL COMMANDS ===\n";
  help += "Letter: m.0 a.1 t.5 c.9 h.13\n";
  help += "Word: word.1 word.11\n";
  help += "Brightness: brightness.50 brightness.100\n";
  help += "Control: on off help effects word brightness\n";
  help += "Use 'effects' for list of effects\n";
  help += "Use 'word' for configured word\n";
  help += "Use 'brightness' for current brightness\n";
  help += "=============================\n";
  
  sendResponse(help);
  Serial.println(help);
}

void BLECommandHandler::printEffects() {
  String effects_list = "\n=== AVAILABLE EFFECTS ===\n";
  for (uint8_t i = 0; i < effectCount; i++) {
    effects_list += String(i) + " - ";
    effects_list += effects[i]->getName();
    effects_list += "\n";
  }
  effects_list += "========================\n";
  
  sendResponse(effects_list);
  Serial.println(effects_list);
}

void BLECommandHandler::performConnectionBlink() {
  blinkInProgress = true;
  blinkStartTime = millis();
  blinkCount = 0;
  
  // Save current brightness
  savedBrightness = stateManager.getBrightnessPercent();
  
  Serial.println("[BLE] Starting connection blink notification (3x blue blinks)");
}
