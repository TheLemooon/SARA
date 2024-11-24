#include "wifiMessage.h"
#include <string.h>

void WifiMessage::setDeviceId(uint8_t id)
{
    deviceId = id;
}

void WifiMessage::setMessage(MessageType msg)
{
    message=msg;
}

MessageType WifiMessage::getMessage()
{
    return message;
}

uint8_t WifiMessage::getDeviceId()
{
    return deviceId;
}

MessageType WifiMessage::convertHexToEnum(uint8_t val)
{
    switch(val)
    {
        case 0x00: return MessageType::Empty;
        case 0x01: return MessageType::autoInterut;
        case 0x02: return MessageType::manualInterupt;
        case 0x03: return MessageType::messageRecieved;
        default: return MessageType::Empty;//add errorhandling
    }
}