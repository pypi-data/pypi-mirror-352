import ctypes
from pathlib import Path
from .config import log 


class _ActionRuleEntry(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('func', ctypes.POINTER(ctypes.c_ubyte))
    ]


class Plugin:
    actions: dict[str, int]
    rules: dict[str, int]
    file_path: Path

    def __init__(
        self,
        file_path: Path,
        actions: dict[str, int],
        rules: dict[str, int]
    ):
        self.actions = actions
        self.rules = rules
        self.file_path = file_path

    @staticmethod
    def load_shared_lib(file: Path):
        path = file.resolve()
        log.info(f'Loading {path}')

        # Python currently doesn't have a platform independent way to
        # unload CDLLs after loading them... this is gonna be rough
        # if we want to rebuild the plugins dynamically
        lib = ctypes.CDLL(str(path))

        try:
            getattr(lib, 'RULEDEFS')
            getattr(lib, 'RULECOUNT')
        except AttributeError:
            log.error(f'Library {file} does not contain RULEDEFS')
            return None

        try:
            getattr(lib, 'ACTIONDEFS')
            getattr(lib, 'ACTIONCOUNT')
        except AttributeError:
            log.error(f'Library {file} does not contain ACTIONDEFS')
            return None

        try:
            getattr(lib, 'plugin_new')
            getattr(lib, 'plugin_delete')
        except AttributeError:
            log.error(f'Library {file} does not contain context functions')
            return None

        action_count = ctypes.c_size_t.in_dll(lib, 'ACTIONCOUNT').value
        action_table = (_ActionRuleEntry * action_count)
        actions = {
            action.name.decode(): i
            for i, action 
            in enumerate(action_table.in_dll(lib, "ACTIONDEFS"))
        }

        rule_count = ctypes.c_size_t.in_dll(lib, 'RULECOUNT').value
        rule_table = (_ActionRuleEntry * rule_count)
        rule = {
            rule.name.decode(): i
            for i, rule
            in enumerate(rule_table.in_dll(lib, "RULEDEFS"))
        }

        return Plugin(path, actions, rule)
