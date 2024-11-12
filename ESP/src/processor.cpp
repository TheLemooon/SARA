#include "processor.h"
#include "wifiMessage.h"
#include "wifiController.h"
#include <thread>
#include <Arduino.h>
//#include "dataExchange.h"
#include <string.h>
#include <cstring>

const int pinHandTrigger = 15;//pinu 15//I09//GPIO 25
const int pinLightcurtain = 32;//
const int pinUartTx= 35;//GPIO1//24,23
const int pinUartRx= 34;//GPIO3//24,23
const int led1 = 5; //PINu 5//IO5//GPIO35
const int led3 = 16; //Pinu16// Io18//GPIO11
const int led2 =17;//pinu17//Io19//GPIO does not correlate
const int statusBridge = 13;//pinu13//Io12//GPIO14
//HardwareSerial mySerial(1);

Processor::Processor(bool paramIsMasterDevice, uint8_t *recieverMac, uint8_t deviceId)
{
    //Serial.begin(115200);
    Serial.println("proc initialiing");
    isMasterDevice = paramIsMasterDevice;
    wifiController = std::shared_ptr<WifiControll>(new WifiControll(recieverMac,exchange));
    wifiThread = std::thread(&WifiControll::run,wifiController);
    pinMode(pinHandTrigger, INPUT_PULLUP);
    pinMode(pinLightcurtain, INPUT_PULLUP);
    //pinMode(pinUartTx, OUTPUT);
    //pinMode(pinUartRx, OUTPUT);
}

Processor::~Processor()
{
    wifiThread.join();
}

void Processor::run()
{
    while(1)
    {
        try
        {  
        readGPIOs();
    
        if((isMasterDevice))
        {
            handleMasterInteractions();
        
        }
        else
        {
            handleSlaveInteractions();
        }
        
        wifiMessageRecieved = hasNewMessage();

        if(!messagesToSend.empty())
        {
            for(size_t i = 0; i < messagesToSend.size();)
            {
                //Serial.println("Triign toSend");
                exchange.writeMessageToSend(messagesToSend.at(i));
                //Serial.println("written to exchange");
                messagesToSend.erase(messagesToSend.begin()+i);
            } 
        }
        vTaskDelay(1);
        }
        catch(const std::exception& e)
        {
            //Serial.println("ExcpectionProcessor");
            Serial.print(e.what());
        }
    }
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
            measureDelay(false);
            if(interruptedDevices.back().delay == -1)
            {
                interruptedDevices.back().delay = delay;
            }
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
            //Serial.println(interruptedDevices.at(i).id);
            //Serial.println(interruptedDevices.at(i).delay);
            //Serial.println(interruptedDevices.at(i).automatic);
            sniprintf(str1.get(),len,"Device:%d delay: %.2f automatic: %d",
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
        Serial.println("lightcurtain event hanled");
    }   
    if(wifiMessageRecieved)
    {
        Serial.println("recieved message in proc");
        wifiMessageRecieved = false;
        WifiMessage message;
        message.setDeviceId(deviceId);
        message.setMessage(MessageType::messageRecieved);
        messagesToSend.push_back(message);
    }  
}

void Processor::measureDelay(bool start)
{
    if(start and startTime ==0)
    {
        startTime = time_t(NULL);
    }
    else
    {
        delay  = time_t(NULL) - startTime;
        startTime = 0;
        uartInterface.send("Otherdevicetime*1.5agoManualorAuto");
    }
    recievedMessage.setMessage(MessageType::Empty);
    wifiMessageRecieved = false;
}