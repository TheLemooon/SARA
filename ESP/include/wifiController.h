#ifndef _WIFICONTROLLER_H_
#define _WIFICONTROLLER_H_

#include "wifiMessage.h"
#include "dataExchange.h"
#include <stdint.h>
#include <vector>
#include <esp_now.h>
#include <WiFi.h>

typedef struct struct_message {
    char message[4];
} struct_message;

class WifiControll
{
public:
    WifiControll( uint8_t *recieverMac);

    void run();
    void send(WifiMessage msg);
    static void onDataReceive(const uint8_t * mac, const uint8_t * incomingData, int len);
    //void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status);
private:
    struct_message incomingData;
    uint8_t *recMac;
    struct_message outgoingData;
    std::shared_ptr<char> hexToCharArray(std::vector<uint8_t> hexValues);

    std::vector<esp_now_peer_info_t> peers;

    int32_t getWiFiChannel(const char *ssid);

};

#endif