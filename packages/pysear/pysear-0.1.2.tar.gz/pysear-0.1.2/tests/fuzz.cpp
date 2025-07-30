#include "sear.h"

extern "C" int LLVMFuzzerTestOneInput(const char *request_json, int length) {
  sear(request_json, length, false);
  return 0;
}
