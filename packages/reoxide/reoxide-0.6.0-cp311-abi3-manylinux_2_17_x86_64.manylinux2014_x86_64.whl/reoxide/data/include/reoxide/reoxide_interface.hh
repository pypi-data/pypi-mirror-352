#pragma once
#include <string>

namespace ghidra {
class ReOxideInterface {
public:
  virtual ~ReOxideInterface() {};
  virtual void send_string(const std::string& s) = 0;
};
} // namespace ghidra
