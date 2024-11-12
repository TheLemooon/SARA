#include "processor.h"
#include <thread>

static const bool IS_MASTER_DEVICE = false;//get from switch
uint8_t broadcastAddress[] = {0x1C, 0x69, 0x20, 0x89, 0xDA, 0x20};//start 
                            //{0x1C, 0x69, 0x20, 0x89, 0xB7, 0xFC};//stop
 
/*int main()
{
  Serial.begin(115200);
  Serial.print("main");
  Processor processor(IS_MASTER_DEVICE, broadcastAddress, 0x01);
  std::thread thread;
  thread = std::thread(&Processor::run,&processor);
  thread.join();
  return 0;
}*/

void loop()
{
  Serial.begin(115200);
  Processor processor(IS_MASTER_DEVICE, broadcastAddress, 0x01);
  std::thread thread;
  thread = std::thread(&Processor::run,&processor);
  thread.join();
}

void setup()
{
}
