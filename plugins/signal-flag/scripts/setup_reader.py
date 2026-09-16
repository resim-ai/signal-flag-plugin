#!/usr/bin/env python3
"""Install the bundled native reader into a private, versioned Python runtime."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


class SetupError(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle(plugin: Path) -> tuple[dict, Path, Path, str]:
    directory = plugin / "reader"
    manifest_path = directory / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
        name = manifest["wheel"]
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or not name.endswith("-py3-none-any.whl")
        ):
            raise SetupError("Reader manifest must name one bundled pure-Python wheel")
        if manifest["python_version"] != "3.12":
            raise SetupError("Reader bundle requires an unsupported Python version")
        if not re.fullmatch(r"[a-f0-9]{40}", manifest["source_revision"]):
            raise SetupError("Reader manifest must identify the full source commit")
        wheel = directory / name
        lock = directory / "requirements.lock"
        for path, key in ((wheel, "sha256"), (lock, "requirements_sha256")):
            if path.is_symlink() or not path.is_file() or digest(path) != manifest[key]:
                raise SetupError(f"Reader bundle integrity check failed: {path.name}")
        if re.search(r"(?im)^resim[-_]open[-_]core\b", lock.read_text()):
            raise SetupError("Native reader lock must not include the Linux-only SDK")
        identity = hashlib.sha256(
            (digest(manifest_path) + platform.system() + platform.machine()).encode()
        ).hexdigest()[:24]
        return manifest, wheel, lock, identity
    except (OSError, KeyError, TypeError, ValueError) as error:
        raise SetupError(
            "Reader bundle is missing or invalid; install a complete plugin release"
        ) from error


def state_directory(value: str | None) -> Path:
    selected = value or os.environ.get("SIGNAL_FLAG_READER_HOME")
    if selected:
        path = Path(selected).expanduser()
        if not path.is_absolute():
            raise SetupError(
                "SIGNAL_FLAG_READER_HOME / --state-dir must be an absolute path"
            )
        return path
    return Path.home() / ".cache" / "signal-flag" / "reader"


def private_fallback(create: bool = True) -> Path:
    path = Path(tempfile.gettempdir()) / f"signal-flag-reader-{os.getuid()}"
    if create:
        path.mkdir(mode=0o700, exist_ok=True)
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
        ):
            raise SetupError(
                "Temporary reader state must be an owned, private directory, not a symlink"
            )
    return path


def select_state(value: str | None, check: bool) -> Path:
    path = state_directory(value)
    if value or os.environ.get("SIGNAL_FLAG_READER_HOME"):
        return path
    if check:
        if not path.exists() or not os.access(path, os.W_OK):
            fallback = private_fallback(create=False)
            if fallback.is_dir():
                return fallback
        return path
    try:
        writable_directory(path)
        return path
    except SetupError:
        fallback = private_fallback()
        writable_directory(fallback)
        print(
            f"Default reader cache is not writable; using private temporary state: {fallback}",
            file=sys.stderr,
        )
        return fallback


def writable_directory(path: Path) -> None:
    try:
        missing = []
        parent = path
        while not parent.exists():
            missing.append(parent)
            parent = parent.parent
        for directory in reversed(missing):
            directory.mkdir(mode=0o700, exist_ok=True)
        # Test an actual write; os.access alone can disagree with ACLs or mounts.
        with tempfile.TemporaryFile(dir=path):
            pass
    except OSError as error:
        raise SetupError(
            f"Directory is not writable: {path}. Choose an authorized writable cache/state path."
        ) from error


def run(command: list[str], env: dict[str, str]) -> None:
    try:
        completed = subprocess.run(
            command, env=env, capture_output=True, text=True, check=False
        )
        output = completed.stdout + completed.stderr
        if output:
            print(redact_urls(output), file=sys.stderr, end="")
        completed.check_returncode()
    except subprocess.CalledProcessError as error:
        raise SetupError(
            f"Reader setup command exited with status {error.returncode}; inspect the diagnostics above"
        ) from error
    except OSError as error:
        raise SetupError(
            "Reader setup command could not start; check the executable and filesystem access"
        ) from error


def redact_urls(text: str) -> str:
    def replace(match):
        parsed = urlsplit(match.group())
        return urlunsplit(
            (parsed.scheme, parsed.netloc.rsplit("@", 1)[-1], parsed.path, "", "")
        )

    return re.sub(r"https?://[^\s<>\"']+", replace, text)


def find_python(uv: str, env: dict[str, str]) -> str | None:
    try:
        result = subprocess.run(
            [uv, "python", "find", "--no-python-downloads", "3.12"],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        found = result.stdout.strip()
        return found if result.returncode == 0 and Path(found).is_file() else None
    except OSError as error:
        raise SetupError("Could not inspect installed Python runtimes") from error


SMOKE = """
import importlib.metadata, io, json, sys
assert sys.version_info[:2] == (3, 12), 'Python 3.12 is required'
import field_sessions_parser, field_sessions_parser.reader, field_sessions_parser.remote
import mcap, rosbags.highlevel, google.protobuf, boto3, lz4.frame, zstandard
try:
    importlib.metadata.distribution('resim-open-core')
except importlib.metadata.PackageNotFoundError:
    pass
else:
    raise AssertionError('Native inspection environment unexpectedly contains the SDK')
from mcap.writer import Writer
from field_sessions_parser.reader import LogReader
stream = io.BytesIO()
writer = Writer(stream)
writer.start()
channel_id = writer.register_channel('/signal_flag/setup', 'json', 0)
exact_ns = 1700000000000000123
writer.add_message(channel_id, exact_ns, b'{"value":7}', exact_ns)
writer.finish()
reader = LogReader(stream).open()
messages = list(reader.iter_messages())
assert len(messages) == 1 and reader.statistics.message_count == 1
channel, message = messages[0]
assert channel.topic == '/signal_flag/setup' and message.log_time == exact_ns
assert reader.decode(channel, message) == {'value': 7}
print(json.dumps({'python_version': sys.version.split()[0],
                  'parser_version': importlib.metadata.version('field-sessions-parser'),
                  'synthetic_mcap': 'passed'}))
"""


def inspect_runtime(python: Path) -> dict:
    try:
        completed = subprocess.run(
            [str(python), "-I", "-c", SMOKE], check=True, capture_output=True, text=True
        )
        return json.loads(completed.stdout)
    except subprocess.CalledProcessError as error:
        if error.stderr:
            print(redact_urls(error.stderr), file=sys.stderr, end="")
        raise SetupError(
            f"Native reader smoke check exited with status {error.returncode}; inspect the diagnostics above"
        ) from error
    except OSError as error:
        raise SetupError(
            "Native reader smoke check could not start; run setup again and check runtime access"
        ) from error
    except ValueError as error:
        raise SetupError(
            "Native reader smoke check returned invalid output; run setup again"
        ) from error


def setup(plugin: Path, state: Path, check: bool = False) -> dict:
    if platform.system() not in {"Darwin", "Linux"}:
        raise SetupError("Native reader setup currently supports macOS and Linux")
    if platform.system() == "Darwin" and int(platform.mac_ver()[0].split(".")[0]) < 12:
        raise SetupError("Native reader setup requires macOS 12 or newer")
    manifest, wheel, lock, identity = bundle(plugin)
    runtime = state / "environments" / identity
    python = runtime / "bin" / "python"
    receipt = runtime / ".signal-flag-reader.json"
    if check:
        if (
            not receipt.is_file()
            or json.loads(receipt.read_text()).get("bundle_id") != identity
        ):
            raise SetupError(
                "This reader bundle is not installed; run /signal-flag:setup-reader"
            )
        info = inspect_runtime(python)
    else:
        uv = shutil.which("uv")
        if not uv:
            raise SetupError(
                "uv is required. Install it through your approved package manager, then rerun setup"
            )
        writable_directory(state)
        env = dict(os.environ)
        cache = Path(env.get("UV_CACHE_DIR") or state / "uv-cache").expanduser()
        if not cache.is_absolute():
            raise SetupError("UV_CACHE_DIR must be an absolute writable path")
        writable_directory(cache)
        env["UV_CACHE_DIR"] = str(cache)
        installed_python = find_python(uv, env.copy())
        for key, default in (("UV_PYTHON_INSTALL_DIR", state / "python"),):
            directory = Path(env.get(key) or default).expanduser()
            if not directory.is_absolute():
                raise SetupError(f"{key} must be an absolute writable path")
            writable_directory(directory)
            env[key] = str(directory)
        with (state / ".setup.lock").open("a") as mutex:
            fcntl.flock(mutex, fcntl.LOCK_EX)
            info = None
            if (
                receipt.is_file()
                and json.loads(receipt.read_text()).get("bundle_id") == identity
            ):
                try:
                    info = inspect_runtime(python)
                except SetupError:
                    receipt.unlink()
            if info is None:
                writable_directory(runtime.parent)
                run(
                    [
                        uv,
                        "venv",
                        "--python",
                        installed_python or "3.12",
                        *([] if installed_python else ["--managed-python"]),
                        "--allow-existing",
                        str(runtime),
                    ],
                    env,
                )
                run(
                    [
                        uv,
                        "pip",
                        "sync",
                        "--python",
                        str(python),
                        "--require-hashes",
                        "--only-binary",
                        ":all:",
                        str(lock),
                    ],
                    env,
                )
                wheel_lock = runtime / ".reader-wheel.lock"
                wheel_lock.write_text(
                    f"field-sessions-parser @ {wheel.as_uri()} --hash=sha256:{manifest['sha256']}\n"
                )
                run(
                    [
                        uv,
                        "pip",
                        "install",
                        "--python",
                        str(python),
                        "--no-deps",
                        "--require-hashes",
                        "-r",
                        str(wheel_lock),
                    ],
                    env,
                )
                run([uv, "pip", "check", "--python", str(python)], env)
                info = inspect_runtime(python)
                receipt.write_text(
                    json.dumps(
                        {
                            "bundle_id": identity,
                            "source_repository": manifest.get("source_repository"),
                            "source_revision": manifest["source_revision"],
                        }
                    )
                    + "\n"
                )
    return {
        "status": "ready",
        "bundle_id": identity,
        "source_repository": manifest.get("source_repository"),
        "source_revision": manifest["source_revision"],
        "python": str(python),
        "cli": str(runtime / "bin" / "field-sessions-parser"),
        "sdk_available": False,
        "state_dir": str(state),
        **info,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify an existing setup without installing or accessing the network",
    )
    parser.add_argument(
        "--state-dir",
        help="Absolute authorized writable location for private runtime/cache",
    )
    args = parser.parse_args()
    try:
        result = setup(
            Path(__file__).resolve().parents[1],
            select_state(args.state_dir, args.check),
            args.check,
        )
    except (SetupError, OSError, ValueError) as error:
        print(json.dumps({"status": "blocked", "error": str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
