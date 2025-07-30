#ifndef __SEAR_KEYRING_MODIFIER_H_
#define __SEAR_KEYRING_MODIFIER_H_

#include "irrsdl00.hpp"
#include "security_request.hpp"

namespace SEAR {
class KeyringModifier {
 private:
  static void buildKeyringArgs(keyring_args_t *p_args,
                               const SecurityRequest &request,
                               bool use_keyring_owner);
  static char *preserveRawRequest(const char *p_arg_area,
                                  const int &raw_request_length);

 public:
  void addOrDeleteKeyring(SecurityRequest &request);
  void addCertificate(SecurityRequest &request);
  void deleteOrRemoveCertificate(SecurityRequest &request);
};
}  // namespace SEAR

#endif
