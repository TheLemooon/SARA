#include "wifiController.h"
#include "wifiMessage.h"
#include "dataExchange.h"
#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>
#include <stdint.h>
#include <vector>

int ESP_NOW_ROLE_CONTROLLER = 0;
int receiverMacAddress =0;

esp_now_peer_info_t peerInfo;
constexpr char WIFI_SSID[] = "ESP32AP";

void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status)
{
    if (status == ESP_NOW_SEND_SUCCESS)
    {
        // Serial.println("message sent successfully");
    }
    else
    {
        // Serial.println("couldnt't send message");
    }
}

WifiControll::WifiControll(uint8_t *recieverMac)
{
    recMac = recieverMac;
    WiFi.mode(WIFI_STA);
    if (esp_now_init() != ESP_OK)
    {
        Serial.println("Error initializing ESP-NOW");
        return;
    }

    // register send callback
    esp_now_register_recv_cb(onDataReceive);
    esp_now_register_send_cb(onDataSent);

    // set up peer for esp now communication
    memcpy(peerInfo.peer_addr, recMac, 6);
    peerInfo.channel = 1;
    peerInfo.encrypt = false;
    if (esp_now_add_peer(&peerInfo) != ESP_OK)
    {
        Serial.println("failed to add peer.");
        return;
    }
    std::vector<uint8_t> hexValues= {0x55, 0x01, 0x01};
    strcpy(outgoingData.message, hexToCharArray(hexValues).get());
    esp_now_send(recMac, (uint8_t *)&outgoingData, sizeof(outgoingData));
}

void WifiControll::send(WifiMessage msg)
{   
    std::vector<uint8_t> hexValues;
    hexValues.push_back(0x55);
    hexValues.push_back(msg.getDeviceId());
    hexValues.push_back(msg.getMessage());
    size_t length = hexValues.size();
    if (length < sizeof(outgoingData.message)) {
        for (size_t i = 0; i < length; i++) {
            outgoingData.message[i] = hexValues[i];
        }
        outgoingData.message[length] = '\0'; // Null-terminate
    } else {
        Serial.println("Error: Message too long");
        return; // Handle error appropriately
    }
    esp_err_t result = esp_now_send(recMac, (uint8_t *)&outgoingData, sizeof(outgoingData));
    if (result != ESP_OK) 
    {
        Serial.printf("Error sending message: %s\n", esp_err_to_name(result));
    }
}

void WifiControll::onDataReceive(const uint8_t * mac, const uint8_t * incomingData, int len) 
{
    WifiMessage msg;
    struct_message myData;
    memcpy(&myData.message, incomingData, sizeof(myData));
    msg.setDeviceId(myData.message[1]);
    msg.setMessage(msg.convertHexToEnum(myData.message[2]));
    exchange.writeMessageRecieved(msg);
}

std::shared_ptr<char> WifiControll::hexToCharArray(std::vector<uint8_t> hexValues) //bon
{
    // Allocate memory for the character array
    size_t length = hexValues.size();
    std::shared_ptr<char> charArray = std::shared_ptr<char>(new char[length + 1]); // +1 for the null terminator

    for (size_t i = 0; i < length; i++) {
        // Convert each hex value to its ASCII representation
        charArray.get()[i] = hexValues.at(i);
    }

    charArray.get()[length] = '\0'; // Null-terminate the char array
    return charArray;
}



int32_t WifiControll::getWiFiChannel(const char *ssid) {
  if (int32_t n = WiFi.scanNetworks()) {
      for (uint8_t i=0; i<n; i++) {
          if (!strcmp(ssid, WiFi.SSID(i).c_str())) {
              return WiFi.channel(i);
          }
      }
  }
  return 0;
}