from pathlib import Path

import pytest
from envix.config.config import Config
from envix.exception import EnvixConfigFileNotFound
from envix.loader import collect_secrets, load_secrets

from tests.config_builder import ConfigV1Builder


class TestV1Load:
    @pytest.mark.asyncio
    async def test_load_v1(
        self,
        config_builder: ConfigV1Builder,
        caplog: pytest.LogCaptureFixture,
    ):
        config = Config(config_builder.add_include("not_exists.yml").build())

        await collect_secrets(config, None)
        for record in caplog.records:
            assert isinstance(record.msg, EnvixConfigFileNotFound)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "config_file, expected_keys",
        [
            ("registered/envix_sample.yml", ["SNOWFLAKE_ACCOUNT"]),
            (
                "registered/envix_includes_sample.yml",
                ["SNOWFLAKE_ACCOUNT", "POSTGRES_ACCOUNT"],
            ),
        ],
    )
    async def test_load_configs(
        self,
        data_dir: Path,
        config_file: str,
        expected_keys: list,
        caplog: pytest.LogCaptureFixture,
    ):
        secrets, errors = await load_secrets(data_dir.joinpath(config_file))
        assert not errors
        assert not caplog.records
        assert list(secrets.keys()) == expected_keys
