"""Tests for ``runner`` module."""

from __future__ import annotations

import contextlib
import multiprocessing
import pathlib
import sys
import typing as t
from pathlib import Path

import pytest

from rstcheck_core import checker, config, runner, types

if t.TYPE_CHECKING:
    import pytest_mock


class TestRstcheckMainRunnerInit:
    """Test ``RstcheckMainRunner.__init__`` method."""

    @staticmethod
    def test_load_config_file_if_set(mocker: pytest_mock.MockerFixture) -> None:
        """Test config file is loaded if set."""
        mocked_loader = mocker.patch.object(runner.RstcheckMainRunner, "load_config_file")
        config_file_path = pathlib.Path("some-file")
        init_config = config.RstcheckConfig(config_path=config_file_path)

        runner.RstcheckMainRunner([], init_config)  # act

        mocked_loader.assert_called_once_with(config_file_path, warn_unknown_settings=False)

    @staticmethod
    def test_no_load_config_file_if_unset(mocker: pytest_mock.MockerFixture) -> None:
        """Test no config file is loaded if unset."""
        mocked_loader = mocker.patch.object(runner.RstcheckMainRunner, "load_config_file")
        init_config = config.RstcheckConfig()

        runner.RstcheckMainRunner([], init_config)  # act

        mocked_loader.assert_not_called()

    @staticmethod
    @pytest.mark.skipif(sys.platform != "win32", reason="Windows specific.")
    @pytest.mark.parametrize("pool_size", [0, 1, 60, 61, 62, 100])
    def test_max_pool_size_on_windows(pool_size: int, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test pool size is 61 at max on windows."""
        monkeypatch.setattr(multiprocessing, "cpu_count", lambda: pool_size)
        init_config = config.RstcheckConfig()

        result = runner.RstcheckMainRunner([], init_config)._pool_size

        assert result <= 61


class TestRstcheckMainRunnerConfigFileLoader:
    """Test ``RstcheckMainRunner.load_config_file`` method."""

    @staticmethod
    def test_no_config_update_on_no_file_config(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config is not updated when no file config is found."""
        monkeypatch.setattr(
            config, "load_config_file_from_path", lambda _, warn_unknown_settings: None
        )
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        _runner.load_config_file(pathlib.Path())  # act

        assert _runner.config == init_config

    @staticmethod
    def test_config_update_on_found_file_config(monkeypatch: pytest.MonkeyPatch) -> None:
        """Test config is updated when file config is found."""
        file_config = config.RstcheckConfigFile(report_level=config.ReportLevel.SEVERE)
        monkeypatch.setattr(
            config, "load_config_file_from_path", lambda _, warn_unknown_settings: file_config
        )
        init_config = config.RstcheckConfig(report_level=config.ReportLevel.INFO)
        _runner = runner.RstcheckMainRunner([], init_config, overwrite_config=True)

        _runner.load_config_file(pathlib.Path())  # act

        assert _runner.config.report_level == config.ReportLevel.SEVERE


class TestRstcheckMainRunnerFileListUpdater:
    """Test ``RstcheckMainRunner.update_file_list`` method."""

    @staticmethod
    def test_empty_file_list() -> None:
        """Test empty file list results in no changes."""
        file_list: list[pathlib.Path] = []
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert not _runner._files_to_check

    @staticmethod
    def test_single_file_in_list(tmp_path: pathlib.Path) -> None:
        """Test single file in list results in only this file in the list."""
        test_file = tmp_path / "rst.rst"
        test_file.touch()
        file_list = [test_file]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert _runner._files_to_check == file_list

    @staticmethod
    def test_multiple_files_in_list(tmp_path: pathlib.Path) -> None:
        """Test multiple files in list results in only these files in the list."""
        test_dir_1 = tmp_path / "one"
        test_dir_1.mkdir()
        test_dir_2 = tmp_path / "two"
        test_dir_2.mkdir()
        test_file1 = test_dir_1 / "rst.rst"
        test_file1.touch()
        test_file2 = test_dir_2 / "rst.rst"
        test_file2.touch()
        file_list = [test_file1, test_file2]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert _runner._files_to_check == file_list

    @staticmethod
    def test_non_rst_files(tmp_path: pathlib.Path) -> None:
        """Test non rst files are filtered out."""
        test_file1 = tmp_path / "rst.rst"
        test_file1.touch()
        test_file2 = tmp_path / "foo.bar"
        test_file2.touch()
        test_file3 = tmp_path / "rst.rst"
        test_file3.touch()
        file_list = [test_file1, test_file2, test_file3]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner._files_to_check) == 2

    @staticmethod
    def test_directory_without_recursive(tmp_path: pathlib.Path) -> None:
        """Test directory without recursive results in empty file list."""
        test_file = tmp_path / "rst.rst"
        test_file.touch()
        file_list = [tmp_path]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert not _runner._files_to_check

    @staticmethod
    def test_directory_with_recursive(tmp_path: pathlib.Path) -> None:
        """Test directory with recursive results in directories files in file list."""
        test_file1 = tmp_path / "rst.rst"
        test_file1.touch()
        test_file2 = tmp_path / "rst2.rst"
        test_file2.touch()
        file_list = [tmp_path]
        init_config = config.RstcheckConfig(recursive=True)
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner._files_to_check) == 2
        assert tmp_path / "rst.rst" in _runner._files_to_check
        assert tmp_path / "rst2.rst" in _runner._files_to_check

    @staticmethod
    def test_dash_as_file() -> None:
        """Test dash as file."""
        file_list = [pathlib.Path("-")]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert file_list == _runner._files_to_check

    @staticmethod
    def test_dash_as_file_with_others(tmp_path: pathlib.Path) -> None:
        """Test dash as file with other files gets ignored."""
        test_file = tmp_path / "rst.rst"
        test_file.touch()
        file_list = [pathlib.Path("-"), test_file]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        _runner.update_file_list()  # act

        assert len(_runner._files_to_check) == 1
        assert test_file in _runner._files_to_check


class TestRstcheckMainRunnerFileListFilter:
    """Test ``RstcheckMainRunner._filter_nonexisting`` method."""

    @staticmethod
    def test_empty_file_list() -> None:
        """Test empty file list results in no changes."""
        file_list: list[pathlib.Path] = []
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert not result
        assert not _runner._nonexisting_paths

    @staticmethod
    def test_single_file_in_list(tmp_path: pathlib.Path) -> None:
        """Test single file in list results in only this file in the list."""
        test_file = tmp_path / "rst.rst"
        test_file.touch()
        file_list = [test_file]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert result == file_list
        assert not _runner._nonexisting_paths

    @staticmethod
    def test_multiple_files_in_list(tmp_path: pathlib.Path) -> None:
        """Test multiple files in list results in only these files in the list."""
        test_dir_1 = tmp_path / "one"
        test_dir_1.mkdir()
        test_dir_2 = tmp_path / "two"
        test_dir_2.mkdir()
        test_file1 = test_dir_1 / "rst.rst"
        test_file1.touch()
        test_file2 = test_dir_2 / "rst.rst"
        test_file2.touch()
        file_list = [test_file1, test_file2]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert result == file_list
        assert not _runner._nonexisting_paths

    @staticmethod
    def test_non_rst_files(tmp_path: pathlib.Path) -> None:
        """Test non rst files are not filtered out."""
        test_file1 = tmp_path / "rst.rst"
        test_file1.touch()
        test_file2 = tmp_path / "foo.bar"
        test_file2.touch()
        test_file3 = tmp_path / "rst.rst"
        test_file3.touch()
        file_list = [test_file1, test_file2, test_file3]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert result == file_list
        assert not _runner._nonexisting_paths

    @staticmethod
    def test_directory_without_recursive(tmp_path: pathlib.Path) -> None:
        """Test directory without recursive results in empty file list."""
        test_file = tmp_path / "rst.rst"
        test_file.touch()
        file_list = [tmp_path]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert not result
        assert _runner._nonexisting_paths == file_list

    @staticmethod
    def test_directory_with_recursive(tmp_path: pathlib.Path) -> None:
        """Test directory with recursive results in directories files in file list."""
        test_file1 = tmp_path / "rst.rst"
        test_file1.touch()
        test_file2 = tmp_path / "rst2.rst"
        test_file2.touch()
        file_list = [tmp_path]
        init_config = config.RstcheckConfig(recursive=True)
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert result == file_list
        assert not _runner._nonexisting_paths

    @staticmethod
    def test_dash_as_file() -> None:
        """Test dash as file gets filtered out."""
        file_list = [pathlib.Path("-")]
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner(file_list, init_config)

        result = _runner._filter_nonexisting_paths(file_list)

        assert not result
        assert _runner._nonexisting_paths == file_list


@pytest.mark.parametrize(
    "lint_errors",
    [[], [types.LintError(source_origin="<string>", line_number=0, message="message")]],
)
def test__run_checks_sync_method(
    lint_errors: list[types.LintError], monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Test ``RstcheckMainRunner._run_checks_sync`` method.

    Test results are returned.
    """
    monkeypatch.setattr(checker, "check_file", lambda _0, _1, _3: lint_errors)
    test_file1 = tmp_path / "rst.rst"
    test_file1.touch()
    test_file2 = tmp_path / "rst2.rst"
    test_file2.touch()
    file_list = [test_file1, test_file2]
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner(file_list, init_config)

    result = _runner._run_checks_sync()

    assert len(result) == 2
    assert len(result[0]) == len(lint_errors)
    assert len(result[1]) == len(lint_errors)


@pytest.mark.parametrize(
    "lint_errors",
    [[], [types.LintError(source_origin="<string>", line_number=0, message="message")]],
)
def test__run_checks_parallel_method(
    lint_errors: list[types.LintError], monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path
) -> None:
    """Test ``RstcheckMainRunner._run_checks_parallel`` method.

    Test results are returned.
    The multiprocessing.Pool needs to be mocked, because it interferes with pytest-xdist.
    """

    class MockedPool:
        """Mocked instance of ``multiprocessing.Pool``."""

        @staticmethod
        def starmap(_0: t.Any, _1: t.Any) -> list[list[types.LintError]]:  # noqa: ANN401
            """Mock for ``multiprocessing.Pool.starmap`` method."""
            return [lint_errors, lint_errors]

    @contextlib.contextmanager
    def mock_pool(_: t.Any) -> t.Generator[MockedPool, None, None]:  # noqa: ANN401
        """Mock context manager for ``multiprocessing.Pool``."""
        yield MockedPool()

    monkeypatch.setattr(multiprocessing, "Pool", mock_pool)
    test_file1 = tmp_path / "rst.rst"
    test_file1.touch()
    test_file2 = tmp_path / "rst2.rst"
    test_file2.touch()
    file_list = [test_file1, test_file2]
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner(file_list, init_config)

    result = _runner._run_checks_parallel()  # act

    assert len(result) == 2
    assert len(result[0]) == len(lint_errors)
    assert len(result[1]) == len(lint_errors)


@pytest.mark.parametrize(
    ("results", "error_count"),
    [([], 0), ([[types.LintError(source_origin="<string>", line_number=0, message="message")]], 1)],
)
def test__update_results_method(results: list[list[types.LintError]], error_count: int) -> None:
    """Test ``RstcheckMainRunner._update_results`` method.

    Test results are set.
    """
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)

    _runner._update_results(results)  # act

    assert len(_runner.errors) == error_count


def test_check_method_sync_with_1_file(mocker: pytest_mock.MockerFixture) -> None:
    """Test ``RstcheckMainRunner.check`` method.

    Test checks are run in sync for 1 file.
    """
    mocked_sync_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_sync")
    mocked_parallel_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_parallel")
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)
    _runner._files_to_check = [pathlib.Path("file")]

    _runner.check()  # act

    mocked_sync_runner.assert_called_once()
    mocked_parallel_runner.assert_not_called()


def test_check_method_parallel_with_more_files(mocker: pytest_mock.MockerFixture) -> None:
    """Test ``RstcheckMainRunner.check`` method.

    Test checks are run in parallel for more file.
    """
    mocked_sync_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_sync")
    mocked_parallel_runner = mocker.patch.object(runner.RstcheckMainRunner, "_run_checks_parallel")
    init_config = config.RstcheckConfig()
    _runner = runner.RstcheckMainRunner([], init_config)
    _runner._files_to_check = [pathlib.Path("file"), pathlib.Path("file2")]

    _runner.check()  # act

    mocked_sync_runner.assert_not_called()
    mocked_parallel_runner.assert_called_once()


class TestRstcheckMainRunnerResultPrinter:
    """Test ``RstcheckMainRunner.get_result`` method."""

    @staticmethod
    def test_exit_code_on_success() -> None:
        """Test exit code 0 is returned on no errors."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        result = _runner.print_result()

        assert result == 0

    @staticmethod
    def test_success_message_on_success(capsys: pytest.CaptureFixture[str]) -> None:
        """Test success message is printed to stdout by default if no errors."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)

        _runner.print_result()  # act

        assert "Success! No issues detected." in capsys.readouterr().out

    @staticmethod
    def test_error_message_on_error(
        tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test error message is printed to stderr by default if errors are found."""
        test_file = tmp_path / "nonexisting.rst"
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([test_file], init_config)

        _runner.print_result()  # act

        assert "Error! Issues detected." in capsys.readouterr().err

    @staticmethod
    def test_success_message_print_to_file(tmp_path: pathlib.Path) -> None:
        """Test success message is printed to given file."""
        out_file = tmp_path / "outfile.txt"
        out_file.touch()
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        # fmt: off
        with Path(out_file).open(encoding="utf-8", mode="w") as out_file_handle:

            _runner.print_result(output_file=out_file_handle)  # act

        # fmt: on
        assert "Success! No issues detected." in out_file.read_text()

    @staticmethod
    def test_exit_code_on_error() -> None:
        """Test exit code 1 is returned when errors were found."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner.errors = [
            types.LintError(source_origin="<string>", line_number=0, message="message")
        ]

        result = _runner.print_result()

        assert result == 1

    @staticmethod
    def test_no_success_message_on_error(capsys: pytest.CaptureFixture[str]) -> None:
        """Test no success message is printed when errors were found."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner.errors = [
            types.LintError(source_origin="<string>", line_number=0, message="message")
        ]

        _runner.print_result()  # act

        assert "Success! No issues detected." not in capsys.readouterr()

    @staticmethod
    def test_error_printed_to_stderr_by_default(capsys: pytest.CaptureFixture[str]) -> None:
        """Test errors are printed to stderr."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [[types.LintError(source_origin="<string>", line_number=0, message="Some error.")]]
        )

        _runner.print_result()  # act

        assert "(ERROR/3) Some error" in capsys.readouterr().err

    @staticmethod
    def test_error_printed_to_file(tmp_path: pathlib.Path) -> None:
        """Test errors are printed to stderr."""
        out_file = tmp_path / "outfile.txt"
        out_file.touch()
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [[types.LintError(source_origin="<string>", line_number=0, message="Some error.")]]
        )
        # fmt: off
        with Path(out_file).open(encoding="utf-8", mode="w") as out_file_handle:

            _runner.print_result(output_file=out_file_handle)  # act

        # fmt: on
        assert "(ERROR/3) Some error" in out_file.read_text()

    @staticmethod
    def test_error_category_prepend(capsys: pytest.CaptureFixture[str]) -> None:
        """Test ``(ERROR/3)`` is prepended when no category is present."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [[types.LintError(source_origin="<string>", line_number=0, message="Some error.")]]
        )

        _runner.print_result()  # act

        assert "(ERROR/3) Some error." in capsys.readouterr().err

    @staticmethod
    def test_error_message_format(capsys: pytest.CaptureFixture[str]) -> None:
        """Test error message format."""
        init_config = config.RstcheckConfig()
        _runner = runner.RstcheckMainRunner([], init_config)
        _runner._update_results(
            [
                [
                    types.LintError(
                        source_origin="<string>", line_number=0, message="(ERROR/3) Some error."
                    )
                ]
            ]
        )

        _runner.print_result()  # act

        assert "<string>:0: (ERROR/3) Some error." in capsys.readouterr().err
