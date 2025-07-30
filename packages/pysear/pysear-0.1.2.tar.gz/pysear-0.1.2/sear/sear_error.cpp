#include "sear_error.hpp"

#include <algorithm>

namespace SEAR {
SEARError::SEARError(const std::vector<std::string>& errors) : errors_(errors) {
  std::for_each(errors_.begin(), errors_.end(),
                [](std::string& error) { error = "sear: " + error; });
}

SEARError::SEARError(const std::string& error) : errors_({"sear: " + error}) {}

const std::vector<std::string>& SEARError::getErrors() const { return errors_; }

}  // namespace SEAR
