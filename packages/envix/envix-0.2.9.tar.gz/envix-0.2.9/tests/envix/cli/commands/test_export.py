from textwrap import dedent

import pytest
from envix.cli.app import App
from envix.exception import EnvixConfigFileNotFound

from tests.config_builder import ConfigV1Builder


class TestCliAppExportCommand:
    def test_export_command_with_help(self):
        with pytest.raises(SystemExit):
            App.run(["export", "--help"])

    def test_export_command_with_config(
        self,
        config_builder: ConfigV1Builder,
        capsys: pytest.CaptureFixture[str],
    ):
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(["export", "--config-file", config_file.name])

        out, err = capsys.readouterr()
        assert (
            out
            == dedent(
                """
                FOO=1234567890
                BAR=abcdefghijklmn
                """
            ).lstrip()
        )
        assert err == ""

    def test_format_options(
        self,
        config_builder: ConfigV1Builder,
        capsys: pytest.CaptureFixture[str],
    ):
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(["export", "--config-file", config_file.name, "--format", "json"])

        out, err = capsys.readouterr()
        assert out == '{"FOO": "1234567890", "BAR": "abcdefghijklmn"}\n'
        assert err == ""

    def test_config_name(self):
        App.run(["export", "--config-name", "sample"])

    def test_config_name_not_exists(self):
        with pytest.raises(EnvixConfigFileNotFound):
            App.run(["export", "--config-name", "not_exists"])

    def test_export_command_with_config_and_dotenv(
        self,
        config_builder: ConfigV1Builder,
        capsys: pytest.CaptureFixture[str],
    ):
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(["export", "--config-file", config_file.name, "--dotenv"])

        out, err = capsys.readouterr()
        assert (
            out
            == dedent(
                """
                FOO=1234567890
                BAR=abcdefghijklmn
                HELLO=WORLD
                """
            ).lstrip()
        )
        assert err == ""
