#include "processor.h"
#include "wifiMessage.h"
#include "wifiController.h"
#include <thread>
#include <Arduino.h>
#include "dataExchange.h"
#include <string.h>
#include <cstring>
#include <unistd.h>

#include <esp_timer.h>

const int pinHandTrigger = 15;//pinu 15//I09//GPIO 25
const int pinLightcurtain = 32;//
const int pinUartTx= 35;//GPIO1//24,23
const int pinUartRx= 34;//GPIO3//24,23
const int led1 = 5; //PINu 5//IO5//GPIO35
const int led3 = 16; //Pinu16// Io18//GPIO11
const int led2 =17;//pinu17//Io19//GPIO does not correlate
const int statusBridge = 13;//pinu13//Io12//GPIO14
int timerInterrutCount = 0;

DataExchange exchange;

esp_timer_create_args_t timerArgs = {};
esp_timer_handle_t timer;

Processor::Processor(bool paramIsMasterDevice, uint8_t *recieverMac, uint8_t aDeviceId)
{
    //Serial.begin(115200);
    deviceId = aDeviceId;
    //Serial.println("proc initialiing");
    isMasterDevice = paramIsMasterDevice;
    wifiController = std::shared_ptr<WifiControll>(new WifiControll(recieverMac));
    pinMode(pinHandTrigger, INPUT_PULLUP);
    pinMode(pinLightcurtain, INPUT_PULLUP);
    //pinMode(3, INPUT_PULLUP);
    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(led3, OUTPUT);
    //pinMode(pinUartRx, OUTPUT);

    timerArgs.callback = &timerHandler;
    timerArgs.name = "Periodic Timer";

    if (esp_timer_create(&timerArgs, &timer) != ESP_OK) {}
    if (esp_timer_start_periodic(timer, 1000000) != ESP_OK) {}
}

Processor::~Processor()
{
}

void timerHandler(void* arg)
{
    //Serial.println(timerInterrutCount);
    timerInterrutCount ++;
}

void Processor::run()
{
    while(1)
    {
        try
        {  
        readGPIOs();
        uartInterface.processIncomingData();
        wifiMessageRecieved = hasNewMessage();
        
        if((isMasterDevice))
        {
            handleMasterInteractions();
        }
        else
        {
            handleSlaveInteractions();
        }

        if(!messagesToSend.empty())
        {
            for(size_t i = 0; i < messagesToSend.size();)
            {
                //Serial.println("Triign toSend");
                wifiController->send(messagesToSend.at(i));
                //Serial.println("written to exchange");
                messagesToSend.erase(messagesToSend.begin()+i);
            } 
        }

        updateRunProgressLed();
        doTimerSpecificChecks();
        vTaskDelay(1);
        }
        catch(const std::exception& e)
        {
            //Serial.println("ExcpectionProcessor");
            Serial.print(e.what());
        }
    }
}

void Processor::doTimerSpecificChecks()
{
    if(lastKnownTimerInterruptCount != timerInterrutCount)
    {
        lastKnownTimerInterruptCount = timerInterrutCount;
        if(timerInterrutCount % 5 == 0)//only every 5th time
        {
            if(connectionConsiderdDead())
            {
                digitalWrite(led3,HIGH);
            }
            else
            {
                digitalWrite(led3,LOW);
            }
        }

        if(isMasterDevice)//to check if slave alive
        {
            WifiMessage message;
            message.setDeviceId(deviceId);
            message.setMessage(MessageType::messageRecieved);
            messagesToSend.push_back(message);
        }
    }
}

bool Processor::connectionConsiderdDead()
{
    if(communicationAlive)
    {
        communicationAlive = false;
        return false;
    }
    return true;
}

void Processor::readGPIOs()
{
    bool handTrigger = !digitalRead(pinHandTrigger);
    if(!handTrigerPrevoius and handTrigger)
    {
        handTriggerIsPressed = handTrigger;
    }
    handTrigerPrevoius = handTrigger;

    bool lightcurtan = !digitalRead(pinLightcurtain);
    if(!lightCurtanPreviouslyInterrupted and lightcurtan)
    {
        lightCurtanIsInterrupted = lightcurtan;
    }
    lightCurtanPreviouslyInterrupted = lightcurtan;
    digitalWrite(led1,!lightcurtan);
}

void Processor::updateRunProgressLed()
{
    if(runIsInProgress)
    {
        digitalWrite(led2,HIGH);
    }
    else
    {
        digitalWrite(led2,LOW);
    }
}

bool Processor::hasNewMessage()
{
    recievedMessage = exchange.readMessageRecieved();
    if(recievedMessage.getMessage() != MessageType::Empty)
    {
        return true;
    }
    return false;
}

void Processor::handleMasterInteractions()
{
    if(handTriggerIsPressed or lightCurtanIsInterrupted)
    {
        recievedData data;
        data.id = deviceId;
        data.delay= 0;
        if(handTriggerIsPressed)
        {
            data.automatic = false;
        }
        else
        {
            data.automatic = true;
        }
        interruptedDevices.push_back(data);
        handTriggerIsPressed = false;
        lightCurtanIsInterrupted = false;
    }   

    if(wifiMessageRecieved)
    {
        communicationAlive = true;
        wifiMessageRecieved = false;
        MessageType msg = recievedMessage.getMessage();
        if(msg == MessageType::manualInterupt or msg == MessageType::autoInterut)
        {
            measureDelay(true); 
            recievedData data;
            data.id = recievedMessage.getDeviceId();
            if(msg == MessageType::autoInterut)
            {
                data.automatic = true;
            }   
            else
            {
                data.automatic = false;
            }          
            interruptedDevices.push_back(data);  
        }
        else if(msg == MessageType::messageRecieved)
        {
            //enters if alive check or if delay calc
            if(interruptedDevices.size() > 0 && interruptedDevices.back().delay == -1)
            {
                measureDelay(false);
                interruptedDevices.back().delay = delay;
            }
        }
        else if (msg == MessageType::runFinished)
        {
            runIsInProgress = false;
            WifiMessage message;
            message.setDeviceId(deviceId);
            message.setMessage(MessageType::runFinished);
            messagesToSend.push_back(message);
            //to measure delay on raspi
            std::shared_ptr<char> str1=std::shared_ptr<char>(new char[70]);
            snprintf(str1.get(),70,"0,0.0,0");
            uartInterface.send(str1.get());
        }
        else if(msg == MessageType::runInProgress)
        {
            runIsInProgress = true;
            WifiMessage message;
            message.setDeviceId(deviceId);
            message.setMessage(MessageType::runInProgress);
            messagesToSend.push_back(message);
            //to measure delay on raspi
            std::shared_ptr<char> str1=std::shared_ptr<char>(new char[70]);
            snprintf(str1.get(),70,"0,0.0,0");
            uartInterface.send(str1.get());
        }
    }

    handleUartMessages();
    //ask if alive  measure time
}

void Processor::handleUartMessages()
{
    for(size_t i = 0; i < interruptedDevices.size();)//auto interruptedDevice = begin (interruptedDevices); interruptedDevice != end (interruptedDevices); ++interruptedDevice)
    {
        if(interruptedDevices.at(i).delay != -1)
        {
            
            size_t len =70;
            std::shared_ptr<char> str1 =std::shared_ptr<char>(new char[len]);
            snprintf(str1.get(),len,"%d,%.3f,%d",
                            interruptedDevices.at(i).id, 
                            interruptedDevices.at(i).delay, 
                            interruptedDevices.at(i).automatic?1:0);
            uartInterface.send(str1.get());
            interruptedDevices.erase(interruptedDevices.begin()+i);
            
        }
        else
        {
            i++;
        }
    }
}

void Processor::handleSlaveInteractions()
{
    if(handTriggerIsPressed or lightCurtanIsInterrupted)
    {
        WifiMessage message;
        message.setDeviceId(deviceId);
        if(handTriggerIsPressed)
        {
            message.setMessage(MessageType::manualInterupt);
        }
        else
        {
            message.setMessage(MessageType::autoInterut);
        }
        messagesToSend.push_back(message);
        handTriggerIsPressed = false;
        lightCurtanIsInterrupted = false;
        //Serial.println("lightcurtain event hanled");
    }   
    if(wifiMessageRecieved)
    {
        communicationAlive = true;
        wifiMessageRecieved = false;
        MessageType msg = recievedMessage.getMessage();
        if(msg == MessageType::messageRecieved)
        {
            WifiMessage message;
            message.setDeviceId(deviceId);
            message.setMessage(MessageType::messageRecieved);
            messagesToSend.push_back(message);
        }
        else if (msg == MessageType::runFinished)
        {
            runIsInProgress = false;
        }
        else if(msg == MessageType::runInProgress)
        {
            runIsInProgress = true;
        }
    }  
}

void Processor::measureDelay(bool start)
{
    if(start && startTime ==0)
    {
        startTime = millis();
        WifiMessage message;
        message.setDeviceId(deviceId);
        message.setMessage(MessageType::messageRecieved);
        messagesToSend.push_back(message);
    }
    else
    {
        delay  = (millis() - startTime)/1000.0;
        startTime = 0;
        //std::string str= "Otherdevicetime*1.5agoManualorAuto";
        //uartInterface.send(str.data());
    }
    recievedMessage.setMessage(MessageType::Empty);
    wifiMessageRecieved = false;
}