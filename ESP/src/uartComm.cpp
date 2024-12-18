# include "uartComm.h"
#include "Arduino.h"
#include <memory>
#include "wifiMessage.h"
#include "dataExchange.h"

UartComm::UartComm()
{
    Serial.begin(115200);
}

bool UartComm::send(const char* str)//std::shared_ptr<char> &str)
{
    Serial.println(str);
    return true;
}

void UartComm::processIncomingData() 
{
    while (Serial.available() > 0) { // Check if data is available
        String incomingData = Serial.readStringUntil('\n'); // Read until newline
        digitalWrite(16,HIGH);
        handleReceivedData(incomingData.c_str());
        
    }
}

// Private method to handle the received data
void UartComm::handleReceivedData(const char* data) 
{
    Serial.println("recieved");
    if (data == nullptr || strlen(data) < 3) { // Validate data length
        Serial.println("Error: Received invalid data");
        return;
    }
    WifiMessage msg;
    msg.setDeviceId(0x00);
    msg.setMessage(msg.convertCharToEnum(data[2])); // Assuming third char represents the message type
    exchange.writeMessageRecieved(msg);
    Serial.println(data[0]);
    Serial.println(data[1]);
    Serial.println(data[2]);

}