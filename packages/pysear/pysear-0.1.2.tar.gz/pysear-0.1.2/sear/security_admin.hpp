#ifndef __SEAR_SECURITY_ADMIN_H_
#define __SEAR_SECURITY_ADMIN_H_

#include <cstdint>
#include <nlohmann/json-schema.hpp>
#include <nlohmann/json.hpp>

#include "extractor.hpp"
#include "keyring_modifier.hpp"
#include "logger.hpp"
#include "sear_result.h"
#include "sear_schema.hpp"
#include "security_request.hpp"

namespace SEAR {
static const nlohmann::json SEAR_SCHEMA_JSON = SEAR_SCHEMA;
static const nlohmann::json_schema::json_validator SEAR_SCHEMA_VALIDATOR{
    SEAR_SCHEMA_JSON};

class SecurityAdmin {
 private:
  SecurityRequest request_;
  void doExtract(Extractor &extractor);
  void doAddAlterDelete();
  void doAddAlterDeleteKeyring(KeyringModifier &modifier);
  void doAddCertificate(KeyringModifier &modifier);
  void doDeleteCertificate(KeyringModifier &modifier);
  void doRemoveCertificate(KeyringModifier &modifier);

 public:
  SecurityAdmin(sear_result_t *p_result, bool debug);
  void makeRequest(const char *p_request_json_string, int length);
};
}  // namespace SEAR

#endif
