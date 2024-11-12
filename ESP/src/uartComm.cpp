# include "uartComm.h"
#include "Arduino.h"
#include <memory>

UartComm::UartComm()
{
    Serial.begin(115200);
}

bool UartComm::send(char* str)//std::shared_ptr<char> &str)
{
    Serial.print(str);
    return true;
}