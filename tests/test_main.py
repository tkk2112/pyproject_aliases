import tomllib
from collections.abc import Generator
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pyproject_aliases.main import (
    get_alias_from_config,
    get_all_aliases,
    main,
    parse_args,
)


@pytest.fixture
def mock_config_data() -> dict[str, dict[str, dict[str, str]]]:
    return {"tool": {"aliases": {"test-alias": "echo 'Hello, World!'"}}}


class TestParseArgs:
    @pytest.mark.parametrize(
        "argv,expected_toml,expected_alias,expected_extra_args",
        [
            (["alias", "test-alias"], "pyproject.toml", "test-alias", []),
            (
                ["alias", "--pyproject-toml", "custom.toml", "test-alias"],
                "custom.toml",
                "test-alias",
                [],
            ),
            (["alias", "--pyproject-toml", "custom.toml"], "custom.toml", None, []),
            (
                ["alias", "test-alias", "arg1", "arg2"],
                "pyproject.toml",
                "test-alias",
                ["arg1", "arg2"],
            ),
            (
                [
                    "alias",
                    "--pyproject-toml",
                    "custom.toml",
                    "test-alias",
                    "arg1",
                    "arg2",
                ],
                "custom.toml",
                "test-alias",
                ["arg1", "arg2"],
            ),
        ],
    )
    def test_parse_args(
        self,
        argv: list[str],
        expected_toml: str,
        expected_alias: str | None,
        expected_extra_args: list[str],
    ) -> None:
        with patch("sys.argv", argv):
            args = parse_args()
            assert args.pyproject_toml == expected_toml
            assert args.alias == expected_alias
            assert args.extra_args == expected_extra_args


class TestGetAllAliases:
    def test_aliases_found(
        self,
        mock_config_data: dict[str, dict[str, dict[str, str]]],
    ) -> None:
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("tomllib.load", return_value=mock_config_data),
        ):
            result = get_all_aliases("pyproject.toml")
            assert result == {"test-alias": "echo 'Hello, World!'"}
            mock_file.assert_called_once_with("pyproject.toml", "rb")

    def test_no_aliases(self) -> None:
        with (
            patch("builtins.open", mock_open()),
            patch("tomllib.load", return_value={}),
        ):
            result = get_all_aliases("pyproject.toml")
            assert result == {}

    @pytest.mark.parametrize(
        "error_case,exception,expected_exit_code",
        [
            ("file_not_found", FileNotFoundError(), 1),
            ("invalid_toml", tomllib.TOMLDecodeError("Invalid TOML", "", 0), 1),
            ("general_exception", Exception("Unexpected error"), 1),
        ],
    )
    def test_get_all_aliases_error_cases(
        self,
        error_case: str,
        exception: BaseException,
        expected_exit_code: int,
    ) -> None:
        with patch("builtins.open") as mock_open_func:
            if error_case == "file_not_found":
                mock_open_func.side_effect = exception
                with pytest.raises(SystemExit) as excinfo:
                    get_all_aliases("nonexistent.toml")
                assert excinfo.value.code == expected_exit_code
            else:
                with patch("tomllib.load") as mock_load:
                    mock_load.side_effect = exception
                    with pytest.raises(SystemExit) as excinfo:
                        get_all_aliases("invalid.toml")
                    assert excinfo.value.code == expected_exit_code


class TestGetAliasFromConfig:
    def test_alias_found(
        self,
        mock_config_data: dict[str, dict[str, dict[str, str]]],
    ) -> None:
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("tomllib.load", return_value=mock_config_data),
        ):
            result = get_alias_from_config("pyproject.toml", "test-alias")
            assert result == "echo 'Hello, World!'"
            mock_file.assert_called_once_with("pyproject.toml", "rb")

    @pytest.mark.parametrize(
        "error_case,exception,expected_exit_code",
        [
            ("alias_not_found", None, 1),
            ("file_not_found", FileNotFoundError(), 1),
            ("invalid_toml", tomllib.TOMLDecodeError("Invalid TOML", "", 0), 1),
        ],
    )
    def test_get_alias_error_cases(
        self,
        error_case: str,
        exception: BaseException | None,
        expected_exit_code: int,
        mock_config_data: dict[str, dict[str, dict[str, str]]],
    ) -> None:
        if error_case == "alias_not_found":
            with (
                patch("builtins.open", mock_open()),
                patch("tomllib.load", return_value=mock_config_data),
            ):
                with pytest.raises(SystemExit) as excinfo:
                    get_alias_from_config("pyproject.toml", "nonexistent-alias")
                assert excinfo.value.code == expected_exit_code
        else:
            with patch("builtins.open") as mock_open_func:
                if error_case == "file_not_found":
                    mock_open_func.side_effect = exception

                    with pytest.raises(SystemExit) as excinfo:
                        get_alias_from_config("nonexistent.toml", "test-alias")
                    assert excinfo.value.code == expected_exit_code
                else:
                    with patch("tomllib.load") as mock_load:
                        mock_load.side_effect = exception

                        with pytest.raises(SystemExit) as excinfo:
                            get_alias_from_config("invalid.toml", "test-alias")
                        assert excinfo.value.code == expected_exit_code


class TestMain:
    @pytest.fixture
    def mock_main_dependencies(
        self,
    ) -> Generator[tuple[MagicMock, MagicMock, MagicMock, MagicMock]]:
        with (
            patch("pyproject_aliases.main.parse_args") as mock_parse_args,
            patch("pyproject_aliases.main.get_alias_from_config") as mock_get_alias,
            patch("pyproject_aliases.main.get_all_aliases") as mock_get_all,
            patch("subprocess.run") as mock_run,
        ):
            yield mock_parse_args, mock_get_alias, mock_get_all, mock_run

    def test_successful_execution(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        mock_parse_args, mock_get_alias, _, mock_run = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias="test-alias",
            extra_args=[],
        )
        mock_get_alias.return_value = "echo 'Hello, World!'"
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        mock_run.assert_called_once_with(
            "echo 'Hello, World!'",
            shell=True,
            text=True,
            check=False,
        )

    def test_execution_with_extra_args(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        mock_parse_args, mock_get_alias, _, mock_run = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias="test-alias",
            extra_args=["arg1", "arg with space"],
        )
        mock_get_alias.return_value = "echo"
        mock_run.return_value = MagicMock(returncode=0)

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 0
        # shlex.quote() doesn't quote simple arguments without spaces or special chars
        mock_run.assert_called_once_with(
            "echo arg1 'arg with space'",
            shell=True,
            text=True,
            check=False,
        )

    def test_failed_execution(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        mock_parse_args, mock_get_alias, _, mock_run = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias="test-alias",
            extra_args=[],
        )
        mock_get_alias.return_value = "invalid_command"
        mock_run.return_value = MagicMock(returncode=127)

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 127

    def test_execution_exception(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        mock_parse_args, mock_get_alias, _, mock_run = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias="test-alias",
            extra_args=[],
        )
        mock_get_alias.return_value = "some_command"
        mock_run.side_effect = Exception("Execution failed")

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1

    def test_no_alias_provided(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        mock_parse_args, _, mock_get_all, _ = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias=None,
            extra_args=[],
        )
        mock_get_all.return_value = {"test-alias": "echo 'Hello, World!'"}

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        mock_get_all.assert_called_once_with("pyproject.toml")

    def test_no_aliases_defined(
        self,
        mock_main_dependencies: tuple[MagicMock, MagicMock, MagicMock, MagicMock],
    ) -> None:
        """Test when no aliases are defined in the configuration."""
        mock_parse_args, _, mock_get_all, _ = mock_main_dependencies

        mock_parse_args.return_value = MagicMock(
            pyproject_toml="pyproject.toml",
            alias=None,
            extra_args=[],
        )
        mock_get_all.return_value = {}  # Empty aliases dictionary

        with pytest.raises(SystemExit) as excinfo:
            main()
        assert excinfo.value.code == 1
        mock_get_all.assert_called_once_with("pyproject.toml")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
