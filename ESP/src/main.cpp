#include "processor.h"
#include <thread>

static const bool IS_MASTER_DEVICE = false;//get from switch TODO use hardware to readin
//broadcast to
uint8_t slaveReciever[] = {0x1C, 0x69, 0x20, 0x89, 0xDA, 0x20};//start
uint8_t masterReciever[] = {0x1C, 0x69, 0x20, 0x89, 0xB7, 0xFC};//Ziel

void loop()
{
  uint8_t devicId;
  uint8_t* reciever;
  if(IS_MASTER_DEVICE)
  {
    reciever = slaveReciever;
    devicId = 1;
  }
  else
  {
    reciever = masterReciever;
    devicId =2;
  }
  Serial.begin(115200);
  Processor processor(IS_MASTER_DEVICE, reciever, devicId);
  try {
  processor.run();
  }
  catch(const std::exception& e)
  {
    Serial.print(e.what());
  }
}

void setup()
{
}
