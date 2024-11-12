#ifndef _DATAEXCHANGE_H_
#define _DATAEXCHANGE_H_

#include <mutex>
#include <vector>

#include "wifiMessage.h"

class DataExchange {
private:
    std::mutex mtx; // Mutex for thread safety
    std::vector<WifiMessage> dataToSend;
    std::vector<WifiMessage> dataRecieved;

public:
    void writeMessageToSend(WifiMessage msg);
    bool readMessageToSend(WifiMessage &msg);// const;
    void writeMessageRecieved(WifiMessage msg);
    WifiMessage readMessageRecieved();// const;
};
#endif
