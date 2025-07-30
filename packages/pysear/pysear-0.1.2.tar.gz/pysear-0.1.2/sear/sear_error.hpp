#ifndef __SEAR_ERROR_H_
#define __SEAR_ERROR_H_

#include <exception>
#include <iostream>
#include <string>
#include <vector>

namespace SEAR {
class SEARError : public std::exception {
 private:
  std::vector<std::string> errors_;

 public:
  explicit SEARError(const std::vector<std::string>& errors);
  explicit SEARError(const std::string& error);
  const std::vector<std::string>& getErrors() const;
};
}  // namespace SEAR

#endif
