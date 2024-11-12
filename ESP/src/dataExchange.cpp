#include <thread>
#include <mutex>
#include <dataExchange.h>
#include "wifiMessage.h"
#include <Arduino.h>

void DataExchange::writeMessageToSend(WifiMessage msg) 
{
    std::lock_guard<std::mutex> lock(mtx);
    if(msg.getMessage() != MessageType::Empty)
    {
        dataToSend.push_back(msg);
        Serial.println(dataToSend.back().getMessage());
    }
}

// Method to get the boolean value with lock
bool DataExchange::readMessageToSend(WifiMessage &msg)  //const
{
    std::lock_guard<std::mutex> lock(mtx);
    if(!dataToSend.empty())
    {
        msg = dataToSend.at(0);
        dataToSend.erase(dataToSend.begin());
        return true;
    }
    else
    {
        msg.setMessage(MessageType::Empty);
        return false;
    }    
}

void DataExchange::writeMessageRecieved(WifiMessage msg) 
{
    std::lock_guard<std::mutex> lock(mtx);
    if(msg.getMessage() != MessageType::Empty)
    {
        dataRecieved.push_back(msg);
    }
}

// Method to get the boolean value with lock
WifiMessage DataExchange::readMessageRecieved() //const 
{
    std::lock_guard<std::mutex> lock(mtx);
    WifiMessage msg;
    if(!dataRecieved.empty())
    {
        msg = dataRecieved.at(0);
        dataRecieved.erase(dataRecieved.begin());
    }
    else
    {
        msg.setMessage(MessageType::Empty);
    }
    return msg;
}
