import os
from textwrap import dedent

import pytest
from envix.cli.app import App
from envix.exception import EnvixConfigFileNotFound

from tests.config_builder import ConfigV1Builder


class TestCliAppInjectCommand:
    def test_inject_command_with_help(self):
        with pytest.raises(SystemExit):
            App.run(["inject", "--help"])

    def test_inject_command_with_config(
        self,
        config_builder: ConfigV1Builder,
        capfd: pytest.CaptureFixture[str],
    ):
        os.environ.clear()
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(["inject", "--config-file", config_file.name, "env"])

        out, err = capfd.readouterr()
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

    @pytest.mark.parametrize(
        ("options", "ok"),
        [
            ([], False),
            (["--clear-environments"], True),
        ],
    )
    def test_clear_environments(
        self,
        config_builder: ConfigV1Builder,
        capfd: pytest.CaptureFixture[str],
        options: list[str],
        ok: bool,
    ):
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(["inject", "--config-file", config_file.name, *options, "env"])

        out, err = capfd.readouterr()
        assert (
            out
            == dedent(
                """
                FOO=1234567890
                BAR=abcdefghijklmn
                """
            ).lstrip()
        ) is ok

        assert err == ""

    def test_config_name(self):
        App.run(["inject", "--config-name", "sample", "--", "env"])

    def test_config_name_not_exists(self):
        with pytest.raises(EnvixConfigFileNotFound):
            App.run(["inject", "--config-name", "not_exists", "--", "env"])

    def test_inject_command_with_config_and_dotenv(
        self,
        config_builder: ConfigV1Builder,
        capfd: pytest.CaptureFixture[str],
    ):
        os.environ.clear()
        with (
            config_builder.chain()
            .add_env("FOO", "1234567890")
            .add_env("BAR", "abcdefghijklmn")
            .build_file()
        ) as config_file:
            App.run(
                ["inject", "--config-file", config_file.name, "--dotenv", "--", "env"]
            )

        out, err = capfd.readouterr()
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
