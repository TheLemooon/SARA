#ifndef _UARTCOMM_H_
#define _UARTCOMM_H_
#include <memory>

class UartComm
{
public:
    UartComm();
    bool send(char* str);//std::shared_ptr<char> &str);
};
#endif
