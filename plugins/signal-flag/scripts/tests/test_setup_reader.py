import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "setup_reader.py"
SPEC = importlib.util.spec_from_file_location("setup_reader", SCRIPT)
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)


class SetupReaderTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plugin = self.root / "installed plugin"
        self.state = self.root / "private state"
        self.directory = self.plugin / "reader"
        self.directory.mkdir(parents=True)
        self.wheel = self.directory / "field_sessions_parser-0.1.1-py3-none-any.whl"
        self.wheel.write_bytes(b"test wheel")
        self.lock = self.directory / "requirements.lock"
        self.lock.write_text("mcap==1.4.0 --hash=sha256:" + "b" * 64 + "\n")
        self.manifest = {
            "wheel": self.wheel.name,
            "sha256": reader.digest(self.wheel),
            "requirements_sha256": reader.digest(self.lock),
            "source_repository": "https://github.com/resim-ai/field-sessions-parser",
            "source_revision": "a" * 40,
            "python_version": "3.12",
        }
        self.write_manifest()
        self.info = {"python_version": "3.12.11", "parser_version": "0.1.1"}
        finder = patch.object(reader, "find_python", return_value=None)
        self.finder = finder.start()
        self.addCleanup(finder.stop)

    def write_manifest(self):
        (self.directory / "manifest.json").write_text(json.dumps(self.manifest))

    def install(self):
        commands = []

        def run(command, env):
            commands.append((command, env.copy()))
            if command[1] == "venv":
                Path(command[-1]).mkdir(parents=True, exist_ok=True)

        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(reader.shutil, "which", return_value="/approved/uv"),
            patch.object(reader, "run", side_effect=run),
            patch.object(reader, "inspect_runtime", return_value=self.info),
        ):
            result = reader.setup(self.plugin, self.state)
        return result, commands

    def test_explicit_setup_uses_private_python_hashes_and_all_binary_dependencies(
        self,
    ):
        result, commands = self.install()
        self.assertEqual(result["status"], "ready")
        self.assertFalse(result["sdk_available"])
        self.assertEqual(result["source_repository"], self.manifest["source_repository"])
        self.assertTrue(result["python"].startswith(str(self.state)))
        self.assertEqual(len(commands), 4)
        self.assertEqual(
            commands[0][0][1:6],
            ["venv", "--python", "3.12", "--managed-python", "--allow-existing"],
        )
        self.assertIn("--require-hashes", commands[1][0])
        self.assertIn("--only-binary", commands[1][0])
        self.assertIn("--no-deps", commands[2][0])
        self.assertEqual(commands[3][0][1:3], ["pip", "check"])
        for command, env in commands:
            self.assertEqual(env["UV_CACHE_DIR"], str(self.state / "uv-cache"))
            self.assertEqual(env["UV_PYTHON_INSTALL_DIR"], str(self.state / "python"))
            self.assertNotIn("--system", command)
        wheel_lock = Path(result["python"]).parents[1] / ".reader-wheel.lock"
        self.assertIn("installed%20plugin", wheel_lock.read_text())
        self.assertNotIn("UV_CACHE_DIR", os.environ)

    def test_check_is_offline_and_does_not_install(self):
        result, _ = self.install()
        with (
            patch.object(reader, "run", side_effect=AssertionError("must not install")),
            patch.object(
                reader.shutil, "which", side_effect=AssertionError("must not find uv")
            ),
            patch.object(reader, "inspect_runtime", return_value=self.info),
        ):
            self.assertEqual(reader.setup(self.plugin, self.state, check=True), result)

    @unittest.skipUnless(
        shutil.which("uv"), "requires uv for actual argument-parser regression"
    )
    def test_sync_command_is_accepted_by_real_uv_offline(self):
        _, commands = self.install()
        uv = shutil.which("uv")
        environment = self.root / "parser-check-env"
        env = dict(os.environ, UV_CACHE_DIR=str(self.root / "parser-check-cache"))
        subprocess.run(
            [
                uv,
                "venv",
                "--python",
                sys.executable,
                "--no-python-downloads",
                str(environment),
            ],
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        empty_lock = self.root / "empty.lock"
        empty_lock.write_text("")
        command = commands[1][0].copy()
        command[0] = uv
        command[command.index("--python") + 1] = str(environment / "bin" / "python")
        command[-1] = str(empty_lock)
        command.extend(["--offline", "--dry-run"])
        completed = subprocess.run(
            command, env=env, check=False, capture_output=True, text=True
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_existing_python312_is_used_before_private_download_directory(self):
        self.finder.return_value = "/approved/python3.12"
        _, commands = self.install()
        self.assertIn("/approved/python3.12", commands[0][0])
        self.assertNotIn("--managed-python", commands[0][0])
        self.assertNotIn("UV_PYTHON_INSTALL_DIR", self.finder.call_args.args[1])

    def test_default_unwritable_home_uses_secure_temporary_state(self):
        default = self.root / "home-cache"
        original = reader.writable_directory

        def writable(path):
            if path == default:
                raise reader.SetupError("not writable")
            original(path)

        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(reader, "state_directory", return_value=default),
            patch.object(reader.tempfile, "gettempdir", return_value=str(self.root)),
            patch.object(reader, "writable_directory", side_effect=writable),
        ):
            actual = reader.select_state(None, False)
            self.assertEqual(actual.stat().st_mode & 0o777, 0o700)
            self.assertEqual(reader.select_state(None, True), actual)
            self.assertEqual(reader.select_state(str(default), False), default)

    def test_temporary_fallback_rejects_symlink_or_shared_directory(self):
        path = self.root / f"signal-flag-reader-{os.getuid()}"
        with patch.object(reader.tempfile, "gettempdir", return_value=str(self.root)):
            path.symlink_to(self.directory)
            with self.assertRaises(reader.SetupError):
                reader.private_fallback()
            path.unlink()
            path.mkdir(mode=0o755)
            with self.assertRaises(reader.SetupError):
                reader.private_fallback()

    def test_dependency_diagnostics_strip_url_credentials_and_queries(self):
        message = reader.redact_urls(
            "403 https://user:password@example.test/python.tar.gz?sig=secret#fragment\n"
        )
        self.assertEqual(message, "403 https://example.test/python.tar.gz\n")

    def test_command_argument_failure_reports_exit_status_without_guessing_cause(self):
        diagnostics = io.StringIO()
        with (
            patch.object(
                reader.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    ["uv", "pip", "sync"], 2, "", "error: unexpected argument '-r'\n"
                ),
            ),
            redirect_stderr(diagnostics),
            self.assertRaisesRegex(
                reader.SetupError, "exited with status 2"
            ) as failure,
        ):
            reader.run(["uv", "pip", "sync"], {})
        self.assertIn("unexpected argument", diagnostics.getvalue())
        self.assertNotIn("network", str(failure.exception))

    def test_missing_install_check_creates_no_state(self):
        with self.assertRaisesRegex(reader.SetupError, "not installed"):
            reader.setup(self.plugin, self.state, check=True)
        self.assertFalse(self.state.exists())

    def test_new_private_directories_are_0700_and_existing_modes_are_preserved(self):
        parent = self.root / "existing"
        parent.mkdir(mode=0o755)
        before = parent.stat().st_mode
        target = parent / "new-state" / "cache"
        reader.writable_directory(target)
        self.assertEqual(parent.stat().st_mode, before)
        self.assertEqual(target.stat().st_mode & 0o777, 0o700)
        self.assertEqual(target.parent.stat().st_mode & 0o777, 0o700)

    def test_tampered_wheel_or_lock_fails_before_any_install(self):
        for target in (self.wheel, self.lock):
            original = target.read_bytes()
            target.write_bytes(original + b"modified")
            with self.assertRaisesRegex(reader.SetupError, "integrity"):
                reader.setup(self.plugin, self.state)
            self.assertFalse(self.state.exists())
            target.write_bytes(original)

    def test_unsafe_or_incomplete_manifest_is_rejected(self):
        for key, value in (
            ("wheel", "../outside-py3-none-any.whl"),
            ("source_revision", "pending"),
            ("python_version", "3.14"),
        ):
            original = self.manifest[key]
            self.manifest[key] = value
            self.write_manifest()
            with self.assertRaises(reader.SetupError):
                reader.bundle(self.plugin)
            self.manifest[key] = original
        self.write_manifest()
        self.wheel.unlink()
        self.wheel.symlink_to(self.lock)
        with self.assertRaisesRegex(reader.SetupError, "integrity"):
            reader.bundle(self.plugin)

    def test_sdk_lock_is_rejected_even_with_matching_hash(self):
        self.lock.write_text("resim-open-core==1.5.0\n")
        self.manifest["requirements_sha256"] = reader.digest(self.lock)
        self.write_manifest()
        with self.assertRaisesRegex(reader.SetupError, "Linux-only SDK"):
            reader.bundle(self.plugin)

    def test_nonwritable_configured_cache_is_not_silently_replaced(self):
        cache = self.root / "cache-is-a-file"
        cache.write_text("occupied")
        with (
            patch.dict(os.environ, {"UV_CACHE_DIR": str(cache)}),
            patch.object(reader.shutil, "which", return_value="uv"),
            patch.object(reader, "run", side_effect=AssertionError("must not install")),
            self.assertRaisesRegex(reader.SetupError, "not writable"),
        ):
            reader.setup(self.plugin, self.state)
        self.assertEqual(cache.read_text(), "occupied")

    def test_failed_imports_never_create_ready_receipt(self):
        def run(command, _env):
            if command[1] == "venv":
                Path(command[-1]).mkdir(parents=True, exist_ok=True)

        diagnostics = io.StringIO()
        with (
            patch.dict(os.environ, {}, clear=True),
            patch.object(reader.shutil, "which", return_value="uv"),
            patch.object(reader, "run", side_effect=run),
            patch.object(
                reader.subprocess,
                "run",
                side_effect=subprocess.CalledProcessError(
                    1,
                    ["python", "-I", "-c", "smoke"],
                    stderr="ImportError: https://user:password@example.test/module?sig=secret#fragment\n",
                ),
            ),
            redirect_stderr(diagnostics),
            self.assertRaisesRegex(
                reader.SetupError, "smoke check exited with status 1"
            ),
        ):
            reader.setup(self.plugin, self.state)
        self.assertEqual(list(self.state.rglob(".signal-flag-reader.json")), [])
        self.assertEqual(
            diagnostics.getvalue(), "ImportError: https://example.test/module\n"
        )


if __name__ == "__main__":
    unittest.main()
