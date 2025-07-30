#ifndef __SEAR_TRAITS_H_
#define __SEAR_TRAITS_H_

#include <nlohmann/json.hpp>
#include <string>
#include <unordered_map>
#include <vector>

namespace SEAR {

enum TraitType { STRING, BOOLEAN, LIST, UINT };

class Trait {
 private:
  std::string sear_key_;
  std::string racf_key_;
  TraitType trait_type_;

 public:
  Trait(const std::string& sear_key, const std::string& racf_key,
        TraitType trait_type);
  const std::string& getSEARKey();
  const std::string& getRACFKey();
  const std::string& getTraitType();
};

class Traits {
 private:
  std::unordered_map<std::string, std::vector<TraitType>> traits_;

 public:
  Traits(const nlohmann::json& sear_schema);
  const std::string& getSEARKey(const std::string& racf_key);
  const std::string& getRACFKey(const std::string& sear_key);
  TraitType getTraitType(const std::string& sear_key);
};

}  // namespace SEAR

#endif
