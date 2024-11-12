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

constexpr char WIFI_SSID[] = "ESP32AP";

WifiControll::WifiControll(uint8_t *recieverMac, DataExchange &dataEx) : exchange(dataEx)
{
    Serial.begin(115200);
    // Set up the ESP32 in station mode
    //exchange = dataEx;
    recMac = recieverMac;
    WiFi.mode(WIFI_STA);
    int32_t channel = getWiFiChannel(WIFI_SSID);

    if (channel > 0) 
    {
        esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);
    } 
    else 
    {
        esp_wifi_set_channel(0, WIFI_SECOND_CHAN_NONE);
        Serial.println("Failed to get a valid channel.");
        //return; // Early return if the channel is invalid
    }
    // Initialize ESP-NOW
    WiFi.printDiag(Serial);
    esp_err_t err = esp_now_init();
    if (err != ESP_OK) {
        Serial.println("error esp init");
        //return;
    }
    else
    {
        Serial.println("ESPNOW_is init");
    }
    //WiFi.begin();
    // Register the receive callback function
    esp_now_register_recv_cb(onDataReceive);
    esp_now_peer_info_t addPeer;
    memcpy(addPeer.peer_addr, recMac, 6);
    uint8_t ch = 0;
    addPeer.channel = ch;
    Serial.println(addPeer.channel);
    addPeer.encrypt = false;
    peers.push_back(addPeer);
    Serial.printf("Peer MAC Address: %02X:%02X:%02X:%02X:%02X:%02X\n",
              recMac[0], recMac[1], recMac[2],
              recMac[3], recMac[4], recMac[5]);
    for(auto peer : peers)
    {
        esp_err_t result = esp_now_add_peer(&peer);
        if (result != ESP_OK) {
            Serial.printf("couldn't add peer, error code: %d\n", result);
        }
    }
    
    std::vector<uint8_t> hexValues= {0x55, 0x01, 0x01};
    strcpy(outgoingData.message, hexToCharArray(hexValues).get());
    esp_now_send(recMac, (uint8_t *)&outgoingData, sizeof(outgoingData));
    Serial.println("wifi init");
}

void WifiControll::run()
{
    try
    { 
        while(1)
        {
            WifiMessage message;
            if(exchange.readMessageToSend(message))
            {
                Serial.println(message.getMessage());
                send(message);
            }
            vTaskDelay(1);
        }
        
    }
    catch(const std::exception& e)
    {
        Serial.print(e.what());
    }
}

void WifiControll::send(WifiMessage msg)
{   
    Serial.println("sending message");//error here
    std::vector<uint8_t> hexValues;
    hexValues.push_back(0x55);
    hexValues.push_back(msg.getDeviceId());
    hexValues.push_back(msg.getMessage());
    Serial.println("sending message1");
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
    Serial.println("sending message2");
    esp_err_t result = esp_now_send(recMac, (uint8_t *)&outgoingData, sizeof(outgoingData));
    if (result != ESP_OK) 
    {
        Serial.printf("Error sending message: %s\n", esp_err_to_name(result));
    }
    Serial.println("sendDone");

}

void WifiControll::onDataReceive(const uint8_t * mac, const uint8_t * incomingData, int len) 
{
    Serial.println("recieved message");
    std::shared_ptr<char> data[len];
    memcpy(&incomingData, incomingData, sizeof(incomingData));
    WifiMessage msg;
    msg.setDeviceId(incomingData[1]);
    msg.setMessage(msg.convertHexToEnum(incomingData[2]));
    Serial.println("recieveDone");
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