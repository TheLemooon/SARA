#ifndef _UARTCOMM_H_
#define _UARTCOMM_H_
#include <memory>

class UartComm
{
public:
    UartComm();
    bool send(const char* str);
    void processIncomingData();
private:
    void handleReceivedData(const char* data);
};
#endif
