import argparse
import filecmp
import io
import logging
import os
import shutil
import sys
import threading
import tomllib
import yaml
import zmq
import platformdirs
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional
from .plugin import Plugin
from .config import APP_NAME, APP_AUTHOR, log


class ReOxideError(Exception):
    pass


def ld_library_path() -> Path:
    return Path(__file__).parent.resolve() / 'data' / 'bin'


def unpack_name(
    plugins: list[Plugin],
    name: str,
    action: bool,
    message: list[bytes]
) -> bool:
    plug_id = None
    name_id = None

    for i, p in enumerate(plugins):
        lookup = p.actions
        if not action:
            lookup = p.rules

        nid = lookup.get(name)
        if nid is not None:
            name_id = nid
            plug_id = i
            message.append(plug_id.to_bytes(2, 'little'))
            message.append(name_id.to_bytes(2, 'little'))
            return True
    return False


def unpack_action_rule(message: list[bytes], action: Any):
    if 'group' not in action:
        message.append(b'')
    else:
        message.append(action['group'].encode())
    if 'extra_args' not in action:
        message.append(b'\x00')
        return

    arg_count = len(action['extra_args'])
    message.append(arg_count.to_bytes())
    for arg in action['extra_args']:
        match arg['type']:
            case "bool":
                message.append(b'b')
                message.append(arg['value'].to_bytes())


def pipeline_to_message(
    message: list[bytes],
    plugins: list[Plugin],
    pipeline: Any
):
    for step in pipeline:
        if 'action' in step:
            tmp_msg = []
            name_found = unpack_name(
                plugins,
                step['action'],
                True,
                tmp_msg
            )
            if not name_found:
                log.warning(f'Could not find action {step["action"]}')

            message.append(b'a')
            message.extend(tmp_msg)
            unpack_action_rule(message, step)
        elif 'action_group' in step:
            message.append(b'g')
            message.append(step['action_group'].encode())
            pipeline_to_message(message, plugins, step['actions'])
            message.append(b'e')
        elif 'pool' in step:
            message.append(b'p')
            message.append(step['pool'].encode())
            for rule in step['rules']:
                tmp_msg = []
                name_found = unpack_name(
                    plugins,
                    rule['rule'],
                    False,
                    tmp_msg
                )
                if not name_found:
                    log.warning(f'Could not find rule {rule["rule"]}')
                    continue
                message.append(b'r')
                message.extend(tmp_msg)
                unpack_action_rule(message, rule)
            message.append(b'e')


def ghidra_decomp_path(ghidra_root: Path) -> Optional[Path]:
    p = ghidra_root / 'Ghidra' / 'Features' / 'Decompiler' / 'os'
    p = p / 'linux_x86_64' / 'decompile'
    return p if p.exists() and p.is_file() else None


def cmd_init_config(
    config_path: Path,
    **_
):
    print('Creating new basic config.')
    ghidra_root = input('Enter a Ghidra root install directory: ')
    
    ghidra_root = Path(ghidra_root)
    if not ghidra_root.exists():
        exit('Entered Ghidra root directory does not exist.')
    
    ghidra_decomp = ghidra_decomp_path(ghidra_root)
    if not ghidra_decomp:
        msg = 'Entered Ghidra root does not contain decompiler.'
        msg += f' Tried path: {ghidra_decomp}'
        exit(msg)
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with config_path.open('w', encoding='utf-8') as f:
        print('[[ghidra-install]]', file=f)
        print('enabled = true', file=f)
        print(f'root-dir = "{ghidra_root}"', file=f)
    
    print(f'Config saved to {config_path}')


def cmd_link_ghidra(
    config_path: Path,
    config: dict[str, Any],
    **_
):
    bin_path = Path(__file__).parent.resolve() / 'data' / 'bin'
    reoxide_bin =  bin_path / 'decompile'
    try:
        reoxide_bin = reoxide_bin.resolve(strict=True)
    except OSError:
        exit('Could not resolve path to ReOxide binary')

    if 'ghidra-install' not in config:
        msg = 'No Ghidra installation info (ghidra-install) found in '
        msg += f'{config_path}. Need at least one!'
        exit(msg)

    for ghidra_install in config['ghidra-install']:
        ghidra_root = Path(ghidra_install['root-dir'])
        print(f'Checking Ghidra install at "{ghidra_root}"')

        ghidra_enabled = True
        if 'enabled' in ghidra_install:# and not ghidra_install['enabled']:
            entry = ghidra_install['enabled']
            if not isinstance(entry, bool):
                print(f'WARNING: "enabled" is not a boolean value, skipping "{ghidra_root}"')
                continue

            if not entry:
                ghidra_enabled = False

        ghidra_decomp = ghidra_decomp_path(ghidra_root)
        if not ghidra_decomp:
            print(f'WARNING: No decompiler found for "{ghidra_root}", skipping')
            continue

        if ghidra_enabled:
            print(f'Linking "{ghidra_root}" with ReOxide')

            if ghidra_decomp.is_symlink():
                try:
                    decomp_resolved = ghidra_decomp.resolve(strict=True)
                except OSError:
                    print(f'Could not resolve symlink for "{ghidra_decomp}"')
                    continue

                if decomp_resolved != reoxide_bin:
                    print(f'WARNING: Ghidra directory "{ghidra_root}"' +\
                        'has a decompile symlink that does not point to ReOxide')
                    continue

                print(f'Ghidra directory "{ghidra_root}" already linked')
                continue

            try:
                os.rename(
                    ghidra_decomp,
                    ghidra_decomp.with_name('decompile.orig')
                )
            except OSError:
                print(
                    f'Could not rename {ghidra_decomp}, skipping "{ghidra_root}"',
                    file=sys.stderr
                )
                continue

            try:
                ghidra_decomp.symlink_to(reoxide_bin)
            except OSError:
                print(
                    f'Could not create ReOxide symlink, skipping "{ghidra_root}"',
                    file=sys.stderr
                )
                continue

            print(f'Successfully linked "{ghidra_root}"')
        else:
            print(f'Unlinking "{ghidra_root}" from ReOxide')

            if not ghidra_decomp.is_symlink():
                print(f'Ghidra directory "{ghidra_root}" is not linked')
                continue

            orig_decomp = ghidra_decomp.with_name('decompile.orig')
            if not orig_decomp.exists() or not orig_decomp.is_file():
                print(f'Cannot find original decompile binary')
                continue

            try:
                ghidra_decomp.unlink()
                os.rename(orig_decomp, ghidra_decomp)
            except OSError:
                print(
                    f'Could not restore decompile, skipping "{ghidra_root}"',
                    file=sys.stderr
                )
                continue

            print(f'Successfully unlinked "{ghidra_root}"')


def cmd_print_plugin_dir(**_):
    data_dir = platformdirs.user_data_path(APP_NAME, APP_AUTHOR)
    plugin_dir = data_dir / 'plugins'
    plugin_dir.mkdir(parents=True, exist_ok=True)
    print(plugin_dir.resolve())


def cmd_print_data_dir(**_):
    print(Path(__file__).parent.resolve() / 'data')


def cmd_print_ld_library_path(**_):
    print(ld_library_path())


def client_cli():
    parser = argparse.ArgumentParser()
    parser.description = 'Client program for the ReOxide daemon.'
    cmd_parser = parser.add_subparsers(dest="cmd", required=True)

    desc = 'Initialize a ReOxide config file, needed for other commands to function'
    p = cmd_parser.add_parser(
        'init-config',
        description=desc,
        help=desc,
    )

    desc = 'Replace the Ghidra decompile binary with a symlink to ReOxide/restore original decompile binary'
    p = cmd_parser.add_parser(
        'link-ghidra',
        description=desc,
        help=desc,
    )
    p.set_defaults(func=cmd_link_ghidra)

    desc = 'Output the directory used for loading/storing plugins'
    p = cmd_parser.add_parser(
        'print-plugin-dir',
        description=desc,
        help=desc
    )
    p.set_defaults(func=cmd_print_plugin_dir)

    desc = 'Output the directory containing packaged ReOxide data'
    p = cmd_parser.add_parser(
        'print-data-dir',
        description=desc,
        help=desc
    )
    p.set_defaults(func=cmd_print_data_dir)

    desc = 'Print the LD_LIBRARY_PATH that is needed for ReOxide to run'
    p = cmd_parser.add_parser(
        'print-ld-library-path',
        description=desc,
        help=desc
    )
    p.set_defaults(func=cmd_print_ld_library_path)

    args = parser.parse_args()

    config_dir = platformdirs.user_config_path(APP_NAME, APP_AUTHOR)
    config_path = config_dir / 'reoxide.toml'
    if not config_path.exists() or not config_path.is_file():
        if args.cmd == 'init-config':
            cmd_init_config(config_path)
            exit()
        else:
            exit(f'Config file does not exist: {config_path}')

    config = dict()
    with config_path.open('rb') as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            exit(f'Could not parse {config_path}: {e}')

    args.func(config_path=config_path, config=config, args=args)


class ReOxideManager:
    def __init__(self, log_to_buffer=False):
        self.log_buffer = io.StringIO()
        if log_to_buffer:
            handler = logging.StreamHandler(self.log_buffer)
            if log.root.handlers:
                handler.setFormatter(log.root.handlers[0].formatter)
                handler.setLevel(log.root.handlers[0].level)
            log.addHandler(handler)

        data_dir = platformdirs.user_data_path(APP_NAME, APP_AUTHOR)
        config_dir = platformdirs.user_config_path(APP_NAME, APP_AUTHOR)
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / 'reoxide.toml'

        self._install_data(data_dir)
        self._ensure_config_exists(config_path)
        self._check_config(config_path)
        self._load_default_actions(data_dir)
        self._load_plugins(data_dir)
        self._init_zmq()

    def _install_data(self, data_dir: Path):
        base = Path(__file__).parent.resolve() / 'data'
        plugin_dir = data_dir / 'plugins'
        plugin_dir.mkdir(parents=True, exist_ok=True)

        default_yaml = data_dir / 'default.yaml'
        if not default_yaml.exists():
            shutil.copy(base / 'default.yaml', data_dir)

        core_src = base / 'bin' / 'libcore.so'
        core_dst = plugin_dir / 'libcore.so'
        if not core_dst.exists():
            shutil.copy(core_src, core_dst)
        elif not filecmp.cmp(core_src, core_dst):
            log.info('Updating core plugin with new version')
            core_dst.unlink(missing_ok=True)
            shutil.copy(core_src, core_dst)

    def _ensure_config_exists(self, config_path: Path):
        if not config_path.exists():
            msg = f'Config file not found at "{config_path}"'
            raise ReOxideError(msg)

    def _check_config(self, config_path: Path):
        config = dict()
        with config_path.open('rb') as f:
            try:
                config = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                msg = f'Could not parse {config_path}: {e}'
                raise ReOxideError(msg)

        if 'ghidra-install' not in config:
            msg = 'No Ghidra installation info (ghidra-install) found in '
            msg += f'{config_path}. Need at least one!'
            raise ReOxideError(msg)

        for ghidra_install in config['ghidra-install']:
            ghidra_root = Path(ghidra_install['root-dir'])
            ghidra_decomp = ghidra_decomp_path(ghidra_root)
            if not ghidra_decomp:
                log.warning(f'No decompiler found for {ghidra_root}')
                continue

            if not ghidra_decomp.is_symlink():
                msg = f'decompile file is not a symlink. '
                msg += 'If the Ghidra directory has not been linked with '
                msg += 'ReOxide yet, execute "reoxide link-ghidra".'
                log.warning(msg)
                continue

    def _load_default_actions(self, data_dir: Path):
        """
        :raises yaml.YAMLError: If the default pipeline is not a
                                valid yaml file.
        """
        actions_path = data_dir / 'default.yaml'
        if not actions_path.exists() or not actions_path.is_file():
            raise ReOxideError(f'{actions_path} does not exist')

        with actions_path.open() as f:
            self.default_actions = yaml.safe_load(f)

    def _load_plugins(self, data_dir: Path):
        plugin_dir = data_dir / 'plugins'
        plugin_dir.mkdir(parents=True, exist_ok=True)

        self.plugins = []
        for plugin in plugin_dir.glob('*.so'):
            if not plugin.is_file():
                log.info(f'Skipping {plugin} in plugin directory...')
                continue

            p = Plugin.load_shared_lib(plugin)
            if p is None:
                log.error(f'Could not load plugin {plugin}')
                continue

            self.plugins.append(p)

    def _init_zmq(self):
        self.ctx = zmq.Context()
        self.router = self.ctx.socket(zmq.ROUTER)
        self.router.bind("ipc:///tmp/reoxide.sock")
        self.shutdown_signal = self.ctx.socket(zmq.PAIR)
        self.shutdown_signal.connect("inproc://shutdown")
        self.shutdown_sink = self.ctx.socket(zmq.PAIR)
        self.shutdown_sink.bind("inproc://shutdown")
        self.poller = zmq.Poller()
        self.poller.register(self.router, zmq.POLLIN)
        self.poller.register(self.shutdown_sink, zmq.POLLIN)

    def get_logs(self) -> str:
        for handler in log.handlers:
            handler.flush()
        return self.log_buffer.getvalue()

    def shutdown(self):
        log.handlers.clear()
        self.shutdown_signal.send(b'')

    def run(self):
        running = True
        while running:
            try:
                socks = dict(self.poller.poll())
            except KeyboardInterrupt:
                # We use the shutdown signal here instead of just
                # breaking, so that all shutdown code is handled in
                # the same place if we decide to do additional cleanup
                self.shutdown_signal.send(b'')
                continue

            if self.shutdown_sink in socks:
                running = False

            if self.router not in socks:
                continue

            msg_parts = self.router.recv_multipart()
            client_id = msg_parts[0]
            data = msg_parts[2:]

            match data[0]:
                case b'\x00':
                    log.info('Decompiler registered, loading plugins')
                    msg_parts = [client_id, b'']

                    # TODO: Do some sanity checking to make sure we are
                    # not sending garbage to the decompiler process (or
                    # let the decompiler handle it)
                    plugin_paths = [
                        str(p.file_path).encode()
                        for p in self.plugins
                    ]

                    # Make sure we at least send an empty message if we
                    # don't have any plugins to load
                    if plugin_paths:
                        msg_parts.extend(plugin_paths)
                    else:
                        msg_parts.append(b'')

                    self.router.send_multipart(msg_parts)
                case b'\x01':
                    msg_parts = [client_id, b'']
                    pipeline_to_message(
                        msg_parts,
                        self.plugins,
                        self.default_actions
                    )
                    self.router.send_multipart(msg_parts)
                case _:
                    log.info(f'recv: {data[0].decode()}')
                    self.router.send_multipart([client_id, b'', b'OK'])


@contextmanager
def start_background():
    r = ReOxideManager(log_to_buffer=True)
    t = threading.Thread(target=r.run)

    try:
        t.start()
        yield r
    finally:
        r.shutdown()
        t.join()


def main_cli():
    parser = argparse.ArgumentParser()
    parser.description = 'ReOxide daemon for communication with decompiler instances'
    parser.add_argument(
        '--no-adjust-loader-path',
        required=False,
        action='store_true',
        help='If specified, do not start new process with '\
            'adjusted LD_LIBRARY_PATH. The daemon has to '\
            'adjust the path for loading native plugin '\
            'libraries and will restart itself with the'\
            'adjust path if this flag is not passed.'
    )
    args = parser.parse_args()

    format = '%(asctime)s %(levelname)s %(name)s - %(message)s'
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format=format,
        datefmt="%Y-%m-%dT%H:%M:%S"
    )

    # For the plugins to work, we need to add the binary folder to the
    # LD_LIBRARY_PATH. Setting the env var from a running process does
    # not change the dlopen behavior, so we need to start a new process
    # for that.
    if not args.no_adjust_loader_path:
        bin_path = ld_library_path()
        env = dict(os.environ)
        env['LD_LIBRARY_PATH'] = str(bin_path)
        args = sys.orig_argv + ['--no-adjust-loader-path']
        path = sys.executable
        log.info('Restarting with updated LD_LIBRARY_PATH...')
        os.execve(path, args, env)

    try:
        manager = ReOxideManager()
        manager.run()
    except ReOxideError as e:
        log.error(e)
