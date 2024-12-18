#ifndef _WIFIMESSAGE_H_
#define _WIFIMESSAGE_H_

#include <stdint.h>

enum MessageType
{
    Empty = 0x00,
    autoInterut = 0x01,
    manualInterupt = 0x02,
    messageRecieved = 0x03,
    runInProgress = 0x04,
    runFinished = 0x05
};


class WifiMessage
{
public:
    void setDeviceId(uint8_t id);
    void setMessage(MessageType msg);
    MessageType getMessage();
    uint8_t getDeviceId();
    MessageType convertHexToEnum(uint8_t val);
    MessageType convertCharToEnum(char val);
private:
    uint8_t deviceId;
    MessageType message;
};
#endif //WifiMessage