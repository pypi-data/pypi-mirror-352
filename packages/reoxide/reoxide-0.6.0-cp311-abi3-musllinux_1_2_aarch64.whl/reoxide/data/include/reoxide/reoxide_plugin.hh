#pragma once
#include <cstdint>
#include <cstddef>

namespace ghidra {
class Architecture;
class AddrSpace;
class ReOxideInterface;
class Action;
class Rule;
}  // namespace ghidra

namespace reoxide {

class Plugin {
 public:
  virtual ~Plugin() {}
};

struct Context {
  ghidra::Architecture* arch;
  ghidra::AddrSpace* stackspace;
  ghidra::ReOxideInterface* reoxide;
  Plugin* plugin_context;
  const char* group_name;
  uint64_t extra_arg;
};

typedef ghidra::Action* ActionCnstr(const Context*);
typedef ghidra::Rule* RuleCnstr(const Context*);

struct ActionDefinition {
  const char* name;
  ActionCnstr* cnstr;
};

struct RuleDefinition {
  const char* name;
  RuleCnstr* cnstr;
};

#define REOXIDE_RULES(...)                                             \
  extern "C" const reoxide::RuleDefinition RULEDEFS[] = {__VA_ARGS__}; \
  extern "C" const size_t RULECOUNT =                                  \
      sizeof(RULEDEFS) / sizeof(reoxide::RuleDefinition);
#define REOXIDE_ACTIONS(...)                                               \
  extern "C" const reoxide::ActionDefinition ACTIONDEFS[] = {__VA_ARGS__}; \
  extern "C" const size_t ACTIONCOUNT =                                    \
      sizeof(ACTIONDEFS) / sizeof(reoxide::ActionDefinition);
#define REOXIDE_CONTEXT(x)                                 \
  extern "C" reoxide::Plugin* plugin_new() {               \
    return new x{};                                        \
  }                                                        \
  extern "C" void plugin_delete(reoxide::Plugin* plugin) { \
    delete plugin;                                         \
  }

}  // namespace reoxide
