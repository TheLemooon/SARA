#ifndef _PROCESSOR_H_
#define _PROCESSOR_H_

#include "uartComm.h"
#include "wifiController.h"
#include <thread>
#include "dataExchange.h"
#include <time.h>
#include <esp_timer.h>

struct recievedData //rename
{
    uint8_t id;
    float delay = -1;
    bool automatic;
};

class Processor
{
private:
    bool isMasterDevice;
    bool handTriggerIsPressed = false;
    bool handTrigerPrevoius = false;
    bool lightCurtanIsInterrupted = false;
    bool lightCurtanPreviouslyInterrupted = false;

    bool wifiMessageRecieved = false;//to handle any wifi message
    uint8_t deviceId = 0x01;
    UartComm uartInterface;
    WifiMessage recievedMessage;
    std::vector<WifiMessage> messagesToSend;
    std::shared_ptr<WifiControll> wifiController;
    std::thread wifiThread;
    
    std::vector<recievedData> interruptedDevices;
    float delay;
    unsigned long startTime = 0;

    int lastKnownTimerInterruptCount =0;
    bool communicationAlive = false;//to check if partner device alive

    bool runIsInProgress = false;

    void updateRunProgressLed();
    void doTimerSpecificChecks();
    bool connectionConsiderdDead();
    void readGPIOs();
    void handleMasterInteractions();
    void handleUartMessages();
    void handleSlaveInteractions();
    void measureDelay(bool start);
    bool hasNewMessage();

public:
    Processor(bool paramIsMasterDevice, uint8_t *recieverMa, uint8_t aDeviceId);
    ~Processor();
    void run();

    
};

void timerHandler(void* arg);

#endif
